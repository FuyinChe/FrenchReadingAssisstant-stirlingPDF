from __future__ import annotations

import logging
from dataclasses import dataclass

from PIL import Image

from french_reader.bubble_detector import (
    BubbleDetection,
    _expand_bbox,
    _merge_candidate_boxes,
    _normalize_bbox,
)
from french_reader.schemas import BBox

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class _TextLine:
    x: int
    y: int
    w: int
    h: int

    @property
    def x2(self) -> int:
        return self.x + self.w

    @property
    def y2(self) -> int:
        return self.y + self.h

    @property
    def area(self) -> int:
        return self.w * self.h

    @property
    def y_center(self) -> float:
        return self.y + self.h / 2

    def as_tuple(self) -> tuple[int, int, int, int]:
        return self.x, self.y, self.w, self.h


def _horizontal_overlap_ratio(
    a: tuple[int, int, int, int],
    b: tuple[int, int, int, int],
) -> float:
    ax, _, aw, _ = a
    bx, _, bw, _ = b
    inter = max(0, min(ax + aw, bx + bw) - max(ax, bx))
    return inter / min(aw, bw) if min(aw, bw) > 0 else 0.0


def _union_bbox(boxes: list[tuple[int, int, int, int]]) -> tuple[int, int, int, int]:
    xs = [box[0] for box in boxes]
    ys = [box[1] for box in boxes]
    x2s = [box[0] + box[2] for box in boxes]
    y2s = [box[1] + box[3] for box in boxes]
    x = min(xs)
    y = min(ys)
    return x, y, max(x2s) - x, max(y2s) - y


def _median(values: list[int | float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[mid])
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def _page_has_illustrations(rgb, gray) -> bool:
    import cv2

    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    saturation = hsv[:, :, 1]
    colorful = (saturation > 55).mean()
    contrast = float(gray.std())
    return colorful > 0.045 or contrast > 62.0


def _trim_page_margins(ink, img_w: int) -> None:
    margin_x = max(8, int(img_w * 0.045))
    ink[:, :margin_x] = 0
    ink[:, img_w - margin_x :] = 0


def _build_text_ink_mask(rgb, gray, img_w: int, img_h: int, *, illustrated: bool):
    import cv2
    import numpy as np

    if illustrated:
        blur = cv2.GaussianBlur(gray, (31, 31), 0)
        local_contrast = blur.astype(np.int16) - gray.astype(np.int16)
        ink = (local_contrast > 22).astype(np.uint8) * 255
    else:
        mean_bg = float(gray.mean())
        dark_threshold = min(230, max(100, int(mean_bg - 35)))
        ink = np.where(gray < dark_threshold, 255, 0).astype(np.uint8)

    ink = cv2.morphologyEx(
        ink,
        cv2.MORPH_OPEN,
        cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)),
    )
    _trim_page_margins(ink, img_w)
    return ink


def _line_ink_fill(ink, line: _TextLine) -> float:
    roi = ink[line.y : line.y2, line.x : line.x2]
    if roi.size == 0:
        return 0.0
    return float((roi > 0).mean())


def _count_text_glyphs(ink, line: _TextLine) -> int:
    import cv2

    roi = ink[line.y : line.y2, line.x : line.x2]
    if roi.size == 0:
        return 0
    binary = (roi > 0).astype("uint8")
    count, _, stats, _ = cv2.connectedComponentsWithStats(binary)
    return sum(1 for index in range(1, count) if stats[index, cv2.CC_STAT_AREA] >= 4)


def _is_plausible_text_line(
    ink,
    line: _TextLine,
    img_w: int,
    img_h: int,
    *,
    expected_line_h: float,
    illustrated: bool,
) -> bool:
    fill = _line_ink_fill(ink, line)
    aspect = line.w / max(line.h, 1)
    glyphs = _count_text_glyphs(ink, line)

    max_aspect = 24 if illustrated else 55
    if fill < 0.012 or aspect > max_aspect:
        return False
    if line.w < max(36, int(img_w * (0.05 if illustrated else 0.03))):
        return False
    if line.h > max(22, expected_line_h * 2.6):
        return False

    if illustrated:
        if fill > 0.34:
            return False
        if fill > 0.14 and glyphs < 12:
            return False
        if aspect > 12 and fill > 0.11:
            return False
        if glyphs >= 8 and fill <= 0.32 and line.w >= img_w * 0.12:
            return True
        return fill <= 0.1 and glyphs >= 4 and aspect <= 16

    if fill > 0.28:
        return False
    return True


def _split_tall_text_line(ink, line: _TextLine, expected_line_h: float) -> list[_TextLine]:
    import numpy as np

    if line.h <= max(10, expected_line_h * 1.7):
        return [line]

    band = ink[line.y : line.y2, line.x : line.x2]
    row_sums = np.sum(band > 0, axis=1)
    threshold = max(2, int(line.w * 0.012))
    segments: list[tuple[int, int]] = []
    in_row = False
    row_start = 0

    for index, value in enumerate(row_sums):
        if value >= threshold and not in_row:
            in_row = True
            row_start = index
        elif in_row and value < threshold:
            row_end = index
            if row_end - row_start >= 3:
                segments.append((row_start, row_end))
            in_row = False

    if in_row:
        row_end = len(row_sums)
        if row_end - row_start >= 3:
            segments.append((row_start, row_end))

    if len(segments) <= 1:
        return [line]

    split_lines: list[_TextLine] = []
    for row_start, row_end in segments:
        sub_band = band[row_start:row_end, :]
        cols = np.flatnonzero(np.sum(sub_band > 0, axis=0) > 0)
        if cols.size == 0:
            continue
        x = int(cols[0])
        x2 = int(cols[-1]) + 1
        split_lines.append(
            _TextLine(
                x=line.x + x,
                y=line.y + row_start,
                w=x2 - x,
                h=row_end - row_start,
            ),
        )
    return split_lines or [line]


def _extract_line_segments_from_band(
    band,
    band_start: int,
    band_h: int,
    img_w: int,
    *,
    min_line_w: int,
) -> list[_TextLine]:
    import numpy as np

    col_ink = np.sum(band > 0, axis=0)
    active_cols = np.flatnonzero(col_ink > 0)
    if active_cols.size == 0:
        return []

    gutter = max(10, int(img_w * 0.035))
    segments: list[_TextLine] = []
    seg_start = int(active_cols[0])
    prev_col = int(active_cols[0])

    for col in active_cols[1:]:
        col = int(col)
        if col - prev_col > gutter:
            seg_w = prev_col - seg_start + 1
            if seg_w >= min_line_w:
                segments.append(_TextLine(x=seg_start, y=band_start, w=seg_w, h=band_h))
            seg_start = col
        prev_col = col

    seg_w = prev_col - seg_start + 1
    if seg_w >= min_line_w:
        segments.append(_TextLine(x=seg_start, y=band_start, w=seg_w, h=band_h))
    return segments


def _split_vertical_band(
    ink,
    band_start: int,
    band_end: int,
    img_w: int,
    *,
    min_line_w: int,
    min_line_h: int,
) -> list[_TextLine]:
    import numpy as np

    band = ink[band_start:band_end, :]
    if band.size == 0:
        return []

    row_sums = np.sum(band > 0, axis=1)
    threshold = max(2, int(img_w * 0.006))
    segments: list[tuple[int, int]] = []
    in_row = False
    row_start = 0

    for index, value in enumerate(row_sums):
        if value >= threshold and not in_row:
            in_row = True
            row_start = index
        elif in_row and value < threshold:
            row_end = index
            if row_end - row_start >= min_line_h:
                segments.append((row_start, row_end))
            in_row = False

    if in_row:
        row_end = len(row_sums)
        if row_end - row_start >= min_line_h:
            segments.append((row_start, row_end))

    lines: list[_TextLine] = []
    for row_start, row_end in segments:
        sub_band = band[row_start:row_end, :]
        for segment in _extract_line_segments_from_band(
            sub_band,
            band_start + row_start,
            row_end - row_start,
            img_w,
            min_line_w=min_line_w,
        ):
            lines.append(segment)
    return lines


def _detect_text_lines_projection(ink, img_w: int, img_h: int, *, illustrated: bool) -> list[_TextLine]:
    import numpy as np

    page_area = img_w * img_h
    row_ink = np.sum(ink > 0, axis=1)
    row_threshold = max(4, int(img_w * (0.008 if illustrated else 0.012)))
    min_line_h = max(4, int(img_h * 0.003))
    max_line_h = max(8, int(img_h * (0.028 if illustrated else 0.045)))
    min_line_w = max(32, int(img_w * (0.05 if illustrated else 0.035)))
    min_line_area = page_area * 0.00012

    lines: list[_TextLine] = []
    in_band = False
    band_start = 0

    def _consume_band(band_end: int) -> None:
        nonlocal in_band
        band_h = band_end - band_start
        if band_h < min_line_h:
            in_band = False
            return
        if band_h > max_line_h:
            lines.extend(
                _split_vertical_band(
                    ink,
                    band_start,
                    band_end,
                    img_w,
                    min_line_w=min_line_w,
                    min_line_h=min_line_h,
                ),
            )
        else:
            band = ink[band_start:band_end, :]
            for segment in _extract_line_segments_from_band(
                band,
                band_start,
                band_h,
                img_w,
                min_line_w=min_line_w,
            ):
                if segment.w * segment.h >= min_line_area:
                    aspect = segment.w / segment.h if segment.h else 0.0
                    if aspect >= 1.2:
                        lines.append(segment)
        in_band = False

    for row_index, ink_count in enumerate(row_ink):
        if ink_count >= row_threshold and not in_band:
            in_band = True
            band_start = row_index
            continue
        if in_band and ink_count < row_threshold:
            _consume_band(row_index)

    if in_band:
        _consume_band(img_h)

    return lines


def _detect_text_lines_components(ink, img_w: int, img_h: int, *, illustrated: bool) -> list[_TextLine]:
    import cv2

    page_area = img_w * img_h
    min_glyph_area = max(8, int(page_area * 0.0000025))
    max_glyph_h = max(10, int(img_h * (0.035 if illustrated else 0.055)))
    min_line_w = max(28, int(img_w * (0.05 if illustrated else 0.03)))
    max_line_h = max(10, int(img_h * (0.028 if illustrated else 0.045)))

    glyphs: list[tuple[int, int, int, int]] = []
    for contour in cv2.findContours(ink, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]:
        x, y, bw, bh = cv2.boundingRect(contour)
        if bw * bh < min_glyph_area:
            continue
        if bh > max_glyph_h:
            continue
        if bw > img_w * 0.88 and bh > img_h * 0.08:
            continue
        glyphs.append((x, y, bw, bh))

    if not glyphs:
        return []

    median_glyph_h = _median([glyph[3] for glyph in glyphs])
    y_tolerance = max(4.0, median_glyph_h * 0.65)
    glyphs.sort(key=lambda item: item[1] + item[3] / 2)

    glyph_groups: list[list[tuple[int, int, int, int]]] = [[glyphs[0]]]
    for glyph in glyphs[1:]:
        prev = glyph_groups[-1][-1]
        center_gap = abs((glyph[1] + glyph[3] / 2) - (prev[1] + prev[3] / 2))
        if center_gap <= y_tolerance:
            glyph_groups[-1].append(glyph)
        else:
            glyph_groups.append([glyph])

    lines: list[_TextLine] = []
    for group in glyph_groups:
        x, y, bw, bh = _union_bbox(group)
        if bw < min_line_w or bh > max_line_h:
            continue
        if bw / max(bh, 1) < 1.0:
            continue

        band = ink[y : y + bh, x : x + bw]
        segments = _extract_line_segments_from_band(
            band,
            y,
            bh,
            img_w,
            min_line_w=min_line_w,
        )
        lines.extend(segments or [_TextLine(x=x, y=y, w=bw, h=bh)])

    return lines


def _dedupe_lines(lines: list[_TextLine]) -> list[_TextLine]:
    kept: list[_TextLine] = []
    for line in sorted(lines, key=lambda item: (item.y, item.x)):
        duplicate = False
        for index, existing in enumerate(kept):
            overlap = _horizontal_overlap_ratio(line.as_tuple(), existing.as_tuple())
            vertical_gap = abs(line.y_center - existing.y_center)
            if overlap > 0.72 and vertical_gap <= max(line.h, existing.h) * 0.55:
                if line.area > existing.area:
                    kept[index] = line
                duplicate = True
                break
        if not duplicate:
            kept.append(line)
    return kept


def _detect_text_lines(ink, img_w: int, img_h: int, *, illustrated: bool) -> list[_TextLine]:
    if illustrated:
        raw_lines = _detect_text_lines_projection(ink, img_w, img_h, illustrated=True)
        if len(raw_lines) < 2:
            raw_lines = _detect_text_lines_components(ink, img_w, img_h, illustrated=True)
    else:
        raw_lines = _detect_text_lines_components(ink, img_w, img_h, illustrated=False)
        if len(raw_lines) < 2:
            raw_lines = _detect_text_lines_projection(ink, img_w, img_h, illustrated=False)

    expected_line_h = _median([line.h for line in raw_lines]) or max(8.0, img_h * 0.014)
    split_lines: list[_TextLine] = []
    for line in raw_lines:
        split_lines.extend(_split_tall_text_line(ink, line, expected_line_h))

    return [
        line
        for line in _dedupe_lines(split_lines)
        if _is_plausible_text_line(
            ink,
            line,
            img_w,
            img_h,
            expected_line_h=expected_line_h,
            illustrated=illustrated,
        )
    ]


def _same_text_column(a: _TextLine, b: _TextLine, img_w: int) -> bool:
    overlap = _horizontal_overlap_ratio(a.as_tuple(), b.as_tuple())
    if overlap >= 0.2:
        return True

    left_delta = abs(a.x - b.x)
    right_delta = abs(a.x2 - b.x2)
    align_tolerance = max(20, int(img_w * 0.05))
    return left_delta <= align_tolerance or right_delta <= align_tolerance


def _estimate_line_spacing(lines: list[_TextLine], img_w: int) -> float:
    center_gaps: list[float] = []
    ordered = sorted(lines, key=lambda item: (item.y, item.x))
    for index in range(len(ordered) - 1):
        current = ordered[index]
        nxt = ordered[index + 1]
        if not _same_text_column(current, nxt, img_w):
            continue
        center_gap = nxt.y_center - current.y_center
        if center_gap > 0:
            center_gaps.append(center_gap)

    if not center_gaps:
        return 18.0

    sorted_gaps = sorted(center_gaps)
    sample_size = max(2, min(len(sorted_gaps), len(sorted_gaps) // 2 + 1))
    return max(12.0, _median(sorted_gaps[:sample_size]))


def _cluster_lines_vertically(
    lines: list[_TextLine],
    img_w: int,
    img_h: int,
) -> list[list[_TextLine]]:
    if not lines:
        return []

    ordered = sorted(lines, key=lambda item: item.y)
    line_spacing = _estimate_line_spacing(ordered, img_w)
    paragraph_gap = min(max(line_spacing * 1.45, 26.0), img_h * 0.075)
    groups: list[list[_TextLine]] = [[ordered[0]]]

    for line in ordered[1:]:
        prev = groups[-1][-1]
        center_gap = line.y_center - prev.y_center
        if center_gap <= paragraph_gap:
            groups[-1].append(line)
        else:
            groups.append([line])

    return groups


def _cluster_lines_into_groups(
    lines: list[_TextLine],
    img_w: int,
    img_h: int,
) -> list[list[_TextLine]]:
    if not lines:
        return []

    column_tolerance = max(28, int(img_w * 0.07))
    columns: list[list[_TextLine]] = []
    for line in sorted(lines, key=lambda item: (item.x, item.y)):
        matched = False
        for column in columns:
            reference = column[0]
            if (
                abs(line.x - reference.x) <= column_tolerance
                or _horizontal_overlap_ratio(line.as_tuple(), reference.as_tuple()) >= 0.18
            ):
                column.append(line)
                matched = True
                break
        if not matched:
            columns.append([line])

    groups: list[list[_TextLine]] = []
    for column in columns:
        groups.extend(_cluster_lines_vertically(column, img_w, img_h))
    return groups


def _merge_nearby_groups(
    groups: list[list[_TextLine]],
    ink,
    img_w: int,
) -> list[list[_TextLine]]:
    if len(groups) <= 1:
        return groups

    merged: list[list[_TextLine]] = [groups[0]]
    for group in groups[1:]:
        prev_group = merged[-1]
        prev_line = prev_group[-1]
        current_line = group[0]
        center_gap = current_line.y_center - prev_line.y_center
        overlap = _horizontal_overlap_ratio(
            _union_bbox([line.as_tuple() for line in prev_group]),
            _union_bbox([line.as_tuple() for line in group]),
        )

        if center_gap <= 36 and overlap >= 0.15:
            merged[-1].extend(group)
        else:
            merged.append(group)
    return merged


def _line_stack_is_in_text_zone(lines: list[_TextLine], img_h: int) -> bool:
    if len(lines) >= 3:
        return True
    center_y = _median([line.y_center for line in lines]) / img_h
    return center_y <= 0.38 or center_y >= 0.58


def _filter_illustrated_groups(
    groups: list[list[_TextLine]],
    img_w: int,
    img_h: int,
) -> list[list[_TextLine]]:
    if not groups:
        return groups

    scored: list[tuple[float, list[_TextLine]]] = []
    for group in groups:
        box = _union_bbox([line.as_tuple() for line in group])
        _, _, bw, bh = box
        if len(group) < 2 and bw < img_w * 0.22:
            continue
        if not _line_stack_is_in_text_zone(group, img_h) and len(group) < 4:
            continue
        score = len(group) * 10 + bw / img_w * 4 + bh / img_h
        scored.append((score, group))

    if not scored:
        return groups

    scored.sort(key=lambda item: item[0], reverse=True)
    best_score = scored[0][0]
    kept = [group for score, group in scored if score >= best_score * 0.55]
    return kept or [scored[0][1]]


def _expand_paragraph_bbox(
    x: int,
    y: int,
    bw: int,
    bh: int,
    img_w: int,
    img_h: int,
    *,
    illustrated: bool = False,
) -> tuple[int, int, int, int]:
    if illustrated:
        pad_left = max(10, int(img_w * 0.02))
        pad_right = max(18, int(img_w * 0.038))
        pad_y = max(8, int(img_h * 0.014))
    else:
        pad_left = max(8, int(img_w * 0.018))
        pad_right = max(12, int(img_w * 0.028))
        pad_y = max(6, int(img_h * 0.012))

    x = max(0, x - pad_left)
    y = max(0, y - pad_y)
    x2 = min(img_w, x + bw + pad_left + pad_right)
    y2 = min(img_h, y + bh + 2 * pad_y)
    return x, y, x2 - x, y2 - y


def _refine_picture_book_paragraph_bbox(
    gray,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    lines: list[_TextLine],
    img_w: int,
    img_h: int,
) -> tuple[int, int, int, int]:
    import numpy as np

    if not lines:
        return 0, 0, 0, 0

    binary = _zone_adaptive_binary(gray, x0, y0, x1, y1)
    global_box = _union_bbox([line.as_tuple() for line in lines])
    if binary is None:
        return _expand_paragraph_bbox(*global_box, img_w, img_h, illustrated=True)

    local_lines = [
        _TextLine(x=line.x - x0, y=line.y - y0, w=line.w, h=line.h)
        for line in lines
    ]
    lx, ly, lw, lh = _union_bbox([line.as_tuple() for line in local_lines])

    scan_pad_left = max(10, int(img_w * 0.02))
    scan_pad_right = max(20, int(img_w * 0.045))
    scan_pad_y = max(8, int(img_h * 0.012))
    rx = max(0, lx - scan_pad_left)
    ry = max(0, ly - scan_pad_y)
    rx2 = min(binary.shape[1], lx + lw + scan_pad_right)
    ry2 = min(binary.shape[0], ly + lh + scan_pad_y)
    region = binary[ry:ry2, rx:rx2]
    if region.size == 0:
        return _expand_paragraph_bbox(*global_box, img_w, img_h, illustrated=True)

    row_ink = np.sum(region > 0, axis=1)
    col_ink = np.sum(region > 0, axis=0)
    active_rows = np.flatnonzero(row_ink > 0)
    if active_rows.size == 0:
        return _expand_paragraph_bbox(*global_box, img_w, img_h, illustrated=True)

    peak_col = float(col_ink.max()) if col_ink.size else 0.0
    col_threshold = max(1.0, peak_col * 0.06)
    strong_cols = np.flatnonzero(col_ink >= col_threshold)
    if strong_cols.size == 0:
        strong_cols = np.flatnonzero(col_ink > 0)
    if strong_cols.size == 0:
        return _expand_paragraph_bbox(*global_box, img_w, img_h, illustrated=True)

    left_col = int(strong_cols[0])
    right_col = int(strong_cols[-1])
    top_row = int(active_rows[0])
    bottom_row = int(active_rows[-1])

    fx = x0 + rx + left_col
    fy = y0 + ry + top_row
    fw = right_col - left_col + 1
    fh = bottom_row - top_row + 1
    return _expand_paragraph_bbox(fx, fy, fw, fh, img_w, img_h, illustrated=True)


def _refine_bbox_from_ink(
    ink,
    lines: list[_TextLine],
    img_w: int,
    img_h: int,
) -> tuple[int, int, int, int]:
    import numpy as np

    x, y, bw, bh = _union_bbox([line.as_tuple() for line in lines])
    pad_x = max(8, int(img_w * 0.015))
    pad_y = max(6, int(img_h * 0.01))
    x = max(0, x - pad_x)
    y = max(0, y - pad_y)
    x2 = min(img_w, x + bw + 2 * pad_x)
    y2 = min(img_h, y + bh + 2 * pad_y)

    region = ink[y:y2, x:x2]
    if region.size == 0:
        return _expand_paragraph_bbox(x, y, x2 - x, y2 - y, img_w, img_h)

    rows = np.any(region > 0, axis=1)
    cols = np.any(region > 0, axis=0)
    if not rows.any() or not cols.any():
        return _expand_paragraph_bbox(x, y, x2 - x, y2 - y, img_w, img_h)

    row_idx = np.flatnonzero(rows)
    col_idx = np.flatnonzero(cols)
    rx = x + int(col_idx[0])
    ry = y + int(row_idx[0])
    rw = int(col_idx[-1] - col_idx[0] + 1)
    rh = int(row_idx[-1] - row_idx[0] + 1)
    return _expand_paragraph_bbox(rx, ry, rw, rh, img_w, img_h)


def _score_line_group(
    lines: list[_TextLine],
    ink,
    img_w: int,
    img_h: int,
    *,
    illustrated: bool,
) -> tuple[tuple[int, int, int, int], float] | None:
    if not lines:
        return None

    line_union = _union_bbox([line.as_tuple() for line in lines])
    raw = _refine_bbox_from_ink(ink, lines, img_w, img_h)
    x, y, bw, bh = raw
    if bw < line_union[2] * 0.88 or bh < line_union[3] * 0.75:
        x, y, bw, bh = _expand_paragraph_bbox(*line_union, img_w, img_h)
    page_area = img_w * img_h
    fill = float((ink[y : y + bh, x : x + bw] > 0).mean()) if bw > 0 and bh > 0 else 0.0
    max_fill = 0.14 if illustrated else 0.22

    if fill > max_fill:
        return None
    if bw * bh < page_area * (0.0018 if illustrated else 0.0007):
        return None
    if bw < max(70, int(img_w * (0.15 if illustrated else 0.08))):
        return None
    if len(lines) == 1 and lines[0].w < img_w * (0.22 if illustrated else 0.12):
        return None

    line_count_factor = min(1.0, 0.5 + len(lines) * 0.1)
    height_factor = min(1.0, bh / max(28.0, img_h * 0.035))
    width_factor = min(1.0, bw / max(img_w * 0.3, 1.0))
    fill_factor = max(0.0, max_fill - fill) / max_fill
    confidence = min(
        0.92,
        0.42
        + line_count_factor * 0.22
        + height_factor * 0.12
        + width_factor * 0.1
        + fill_factor * 0.08,
    )
    return (x, y, bw, bh), confidence


def _cluster_lines_into_paragraphs(
    lines: list[_TextLine],
    ink,
    img_w: int,
    img_h: int,
    *,
    illustrated: bool,
) -> list[tuple[tuple[int, int, int, int], float]]:
    groups = _cluster_lines_into_groups(lines, img_w, img_h)
    groups = _merge_nearby_groups(groups, ink, img_w)
    if illustrated:
        groups = _filter_illustrated_groups(groups, img_w, img_h)

    paragraphs: list[tuple[tuple[int, int, int, int], float]] = []
    for group in groups:
        scored = _score_line_group(group, ink, img_w, img_h, illustrated=illustrated)
        if scored is not None:
            paragraphs.append(scored)
    return paragraphs


def _zone_adaptive_binary(gray, x0: int, y0: int, x1: int, y1: int):
    import cv2

    sub = gray[y0:y1, x0:x1]
    if sub.size == 0:
        return None

    block = max(15, min(31, (sub.shape[1] // 24) | 1))
    binary = cv2.adaptiveThreshold(
        sub,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        block,
        8,
    )
    return cv2.morphologyEx(
        binary,
        cv2.MORPH_OPEN,
        cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)),
    )


def _merge_window_lines_into_rows(lines: list[_TextLine], img_h: int) -> list[_TextLine]:
    if not lines:
        return []

    ordered = sorted(lines, key=lambda item: item.y)
    row_gap = max(6, int(img_h * 0.012))
    max_merged_height = max(24, int(img_h * 0.042))
    merged: list[_TextLine] = [ordered[0]]

    for line in ordered[1:]:
        prev = merged[-1]
        merged_height = max(prev.y2, line.y2) - min(prev.y, line.y)
        if (
            merged_height <= max_merged_height
            and abs(line.x - prev.x) <= max(20, prev.w * 0.08)
            and abs(line.w - prev.w) <= max(24, prev.w * 0.18)
            and line.y - prev.y2 <= row_gap
        ):
            merged[-1] = _TextLine(
                x=min(prev.x, line.x),
                y=min(prev.y, line.y),
                w=max(prev.x2, line.x2) - min(prev.x, line.x),
                h=max(prev.y2, line.y2) - min(prev.y, line.y),
            )
        else:
            merged.append(line)

    return merged


def _filter_picture_book_lines(lines: list[_TextLine], img_w: int) -> list[_TextLine]:
    max_text_width = img_w * 0.55
    min_text_width = max(48, int(img_w * 0.14))
    kept = [
        line
        for line in lines
        if min_text_width <= line.w <= max_text_width
    ]
    if len(kept) < 2:
        return []

    widths = [line.w for line in kept]
    median_w = _median(widths)
    aligned = [
        line
        for line in kept
        if abs(line.w - median_w) / max(median_w, 1) <= 0.4
    ]
    return sorted(aligned or kept, key=lambda item: item.y)


def _filter_aligned_text_lines(lines: list[_TextLine], img_w: int) -> list[_TextLine]:
    if len(lines) < 2:
        return lines

    bucket_size = max(12, int(img_w * 0.05))
    buckets: dict[int, list[_TextLine]] = {}
    for line in lines:
        key = line.x // bucket_size
        buckets.setdefault(key, []).append(line)

    def _group_score(group: list[_TextLine]) -> float:
        if len(group) < 2:
            return float(len(group))
        widths = [line.w for line in group]
        median_w = _median(widths)
        if median_w <= 0:
            return 0.0
        width_spread = _median([abs(width - median_w) / median_w for width in widths])
        aligned = [line for line in group if abs(line.w - median_w) / median_w <= 0.35]
        return len(aligned) * 4 - width_spread * 12 + median_w / img_w * 6

    best_group = max(buckets.values(), key=_group_score)
    if len(best_group) < 2:
        return sorted(lines, key=lambda item: item.y)

    median_w = _median([line.w for line in best_group])
    kept = [
        line
        for line in best_group
        if line.w >= median_w * 0.62 and line.w <= median_w * 1.45
    ]
    return sorted(kept or best_group, key=lambda item: item.y)


def _extend_text_run_width(band, local_x: int, local_w: int) -> int:
    import numpy as np

    col_ink = np.sum(band > 0, axis=0)
    right = local_x + local_w - 1
    max_extend = max(12, int(band.shape[1] * 0.028))
    hard_limit = min(band.shape[1] - 1, right + max_extend)
    extended_right = right
    gap = 0
    max_gap = max(3, int(band.shape[1] * 0.008))
    for col in range(right + 1, hard_limit + 1):
        if col_ink[col] > 0:
            extended_right = col
            gap = 0
        elif gap < max_gap:
            gap += 1
        else:
            break
    return extended_right - local_x + 1


def _detect_lines_in_text_zone(
    gray,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    img_w: int,
    img_h: int,
) -> list[_TextLine]:
    import numpy as np

    binary = _zone_adaptive_binary(gray, x0, y0, x1, y1)
    if binary is None:
        return []

    min_line_w = max(48, int(img_w * 0.14))
    max_line_w = int(img_w * 0.55)
    window = max(6, int(binary.shape[0] * 0.012))
    step = max(2, window // 3)
    raw_lines: list[_TextLine] = []

    for start in range(0, max(1, binary.shape[0] - window), step):
        end = min(binary.shape[0], start + window)
        band = binary[start:end, :]
        cols = np.flatnonzero(np.sum(band > 0, axis=0) > 0)
        if cols.size == 0:
            continue
        local_x = int(cols[0])
        local_w = _extend_text_run_width(band, local_x, int(cols[-1] - cols[0] + 1))
        fill = float((band > 0).mean())
        if local_w < min_line_w or fill < 0.015 or fill > 0.13:
            continue
        raw_lines.append(
            _TextLine(
                x=x0 + local_x,
                y=y0 + start,
                w=local_w,
                h=end - start,
            ),
        )

    merged = _merge_window_lines_into_rows(_dedupe_lines(raw_lines), img_h)
    return _filter_picture_book_lines(merged, img_w)


def _score_picture_book_zone(
    lines: list[_TextLine],
    y0: int,
    y1: int,
    img_w: int,
    img_h: int,
) -> float:
    if len(lines) < 2:
        return 0.0

    ys = [line.y_center for line in lines]
    span = max(ys) - min(ys)
    zone_h = max(1, y1 - y0)
    widths = [line.w for line in lines]
    median_w = _median(widths)
    width_spread = _median([abs(width - median_w) / max(median_w, 1) for width in widths])

    coverage = span / zone_h
    line_density = len(lines) / max(span / max(img_h * 0.02, 1), 1)

    score = len(lines) * 5.0
    score += line_density * 2.0
    score += min(median_w / img_w, 0.55) * 12
    score -= width_spread * 12

    if 0.14 <= median_w / img_w <= 0.48:
        score += 10
    if len(lines) >= 4:
        score += 8

    if median_w > img_w * 0.68:
        score *= 0.05
    if coverage > 0.82 and len(lines) > 12:
        score *= 0.2
    if len(lines) >= 3 and width_spread > 0.45:
        score *= 0.5
    relative_positions = [(line.y_center - y0) / zone_h for line in lines]
    min_rel = min(relative_positions)
    max_rel = max(relative_positions)

    if y0 <= img_h * 0.05:
        if max_rel >= 0.55:
            score += 8
        if max_rel < 0.35:
            score *= 0.15
    else:
        if min_rel >= 0.45:
            score += 8
        if max_rel < 0.35:
            score *= 0.15
    if median_w < img_w * 0.14:
        score *= 0.4

    return max(0.0, score)


def _detect_picture_book_paragraphs(
    gray,
    img_w: int,
    img_h: int,
    *,
    confidence_threshold: float,
) -> list[BubbleDetection]:
    margin_x = max(8, int(img_w * 0.035))
    zones = [
        (margin_x, 0, img_w - margin_x, int(img_h * 0.43)),
        (margin_x, int(img_h * 0.52), img_w - margin_x, img_h),
    ]

    candidates: list[tuple[float, BubbleDetection]] = []
    for x0, y0, x1, y1 in zones:
        lines = _detect_lines_in_text_zone(gray, x0, y0, x1, y1, img_w, img_h)
        zone_score = _score_picture_book_zone(lines, y0, y1, img_w, img_h)
        if zone_score < 3 or len(lines) < 2:
            continue

        zone_group = sorted(lines, key=lambda line: line.y)
        ex, ey, ew, eh = _refine_picture_book_paragraph_bbox(
            gray,
            x0,
            y0,
            x1,
            y1,
            zone_group,
            img_w,
            img_h,
        )
        confidence = min(
            0.92,
            0.45 + len(zone_group) * 0.06 + ew / img_w * 0.1 + zone_score * 0.015,
        )
        if confidence < confidence_threshold:
            continue

        candidates.append(
            (
                zone_score,
                BubbleDetection(
                    bbox=_normalize_bbox(ex, ey, ew, eh, img_w, img_h),
                    confidence=confidence,
                    detector="opencv-paragraph",
                ),
            ),
        )

    if not candidates:
        return []

    candidates.sort(key=lambda item: item[0], reverse=True)
    return [candidates[0][1]]


def detect_text_paragraphs(
    image: Image.Image,
    *,
    confidence_threshold: float = 0.35,
) -> list[BubbleDetection]:
    """Detect prose paragraph blocks by clustering validated text lines."""
    try:
        import cv2
        import numpy as np
    except ImportError as exc:
        raise RuntimeError(
            "Paragraph detection requires OpenCV. Install with:\n"
            "  cd extensions/french-reader-engine && uv sync --extra bubble",
        ) from exc

    arr = np.array(image)
    img_h, img_w = arr.shape[:2]
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    illustrated = _page_has_illustrations(arr, gray)

    if illustrated:
        return _detect_picture_book_paragraphs(
            gray,
            img_w,
            img_h,
            confidence_threshold=confidence_threshold,
        )

    ink = _build_text_ink_mask(arr, gray, img_w, img_h, illustrated=False)
    lines = _detect_text_lines(ink, img_w, img_h, illustrated=False)
    paragraphs = _cluster_lines_into_paragraphs(
        lines,
        ink,
        img_w,
        img_h,
        illustrated=False,
    )

    merged = _merge_candidate_boxes(
        [box for box, _ in paragraphs],
        [score for _, score in paragraphs],
        iou_threshold=0.25,
        contain_threshold=0.62,
    )
    merged = sorted(merged, key=lambda item: (item[0][1], item[0][0]))

    results: list[BubbleDetection] = []
    for (x, y, bw, bh), confidence in merged:
        if confidence < confidence_threshold:
            continue
        fill = float((ink[y : y + bh, x : x + bw] > 0).mean())
        if fill > 0.22:
            continue
        results.append(
            BubbleDetection(
                bbox=_normalize_bbox(x, y, bw, bh, img_w, img_h),
                confidence=confidence,
                detector="opencv-paragraph",
            ),
        )
    return results


def detect_text_paragraphs_from_base64(
    image_base64: str,
    *,
    confidence_threshold: float = 0.35,
    preprocess: bool = False,
) -> list[BubbleDetection]:
    from french_reader.bubble_detector import _decode_image, preprocess_comic_page

    image = _decode_image(image_base64)
    if preprocess:
        image = preprocess_comic_page(image)
    return detect_text_paragraphs(image, confidence_threshold=confidence_threshold)
