import {
  ActionIcon,
  Badge,
  Group,
  NumberInput,
  Stack,
  Text,
  Title,
} from "@mantine/core";
import { useTranslation } from "react-i18next";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import ZoomInIcon from "@mui/icons-material/ZoomIn";
import ZoomOutIcon from "@mui/icons-material/ZoomOut";
import type { FrenchReaderPageState } from "@app/hooks/tools/frenchReader/useFrenchReaderPageState";

interface FrenchReaderViewerControlsProps {
  pageState: FrenchReaderPageState;
}

export function FrenchReaderViewerControls({
  pageState,
}: FrenchReaderViewerControlsProps) {
  const { t } = useTranslation();
  const {
    currentPage,
    totalPages,
    zoomPercent,
    scrollToPage,
    scrollToPreviousPage,
    scrollToNextPage,
    zoomIn,
    zoomOut,
  } = pageState;

  return (
    <Stack gap="xs">
      <Text size="sm" fw={500}>
        {t("frenchReader.controls.title", "Viewer")}
      </Text>
      <Group gap="xs" wrap="nowrap">
        <ActionIcon
          variant="default"
          aria-label={t("frenchReader.controls.prevPage", "Previous page")}
          onClick={scrollToPreviousPage}
          disabled={currentPage <= 1}
        >
          <ChevronLeftIcon fontSize="small" />
        </ActionIcon>
        <NumberInput
          size="xs"
          min={1}
          max={Math.max(totalPages, 1)}
          value={currentPage}
          onChange={(value) => {
            const page = typeof value === "number" ? value : Number(value);
            if (Number.isFinite(page) && page >= 1) {
              scrollToPage(page);
            }
          }}
          styles={{ input: { width: 64, textAlign: "center" } }}
          hideControls
        />
        <Text size="sm" c="dimmed">
          / {totalPages || "—"}
        </Text>
        <ActionIcon
          variant="default"
          aria-label={t("frenchReader.controls.nextPage", "Next page")}
          onClick={scrollToNextPage}
          disabled={totalPages > 0 && currentPage >= totalPages}
        >
          <ChevronRightIcon fontSize="small" />
        </ActionIcon>
      </Group>
      <Group gap="xs">
        <ActionIcon
          variant="default"
          aria-label={t("frenchReader.controls.zoomOut", "Zoom out")}
          onClick={zoomOut}
        >
          <ZoomOutIcon fontSize="small" />
        </ActionIcon>
        <Badge variant="light">{zoomPercent}%</Badge>
        <ActionIcon
          variant="default"
          aria-label={t("frenchReader.controls.zoomIn", "Zoom in")}
          onClick={zoomIn}
        >
          <ZoomInIcon fontSize="small" />
        </ActionIcon>
      </Group>
    </Stack>
  );
}
