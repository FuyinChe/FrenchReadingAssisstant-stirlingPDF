import type { NormalizedBBox } from "@app/hooks/tools/frenchReader/types";
import { pdfWorkerManager } from "@app/services/pdfWorkerManager";

const RENDER_SCALE = 2.5;

export async function cropPageRegionToBase64(
  file: File | Blob,
  pageNumber: number,
  bbox: NormalizedBBox,
): Promise<string> {
  const buffer = await file.arrayBuffer();
  const pdf = await pdfWorkerManager.createDocument(buffer, {
    disableAutoFetch: true,
    disableStream: true,
  });

  try {
    const page = await pdf.getPage(pageNumber);
    const viewport = page.getViewport({ scale: RENDER_SCALE });

    const canvas = document.createElement("canvas");
    canvas.width = Math.floor(viewport.width);
    canvas.height = Math.floor(viewport.height);
    const context = canvas.getContext("2d");
    if (!context) {
      throw new Error("Unable to create canvas context");
    }

    await page.render({ canvasContext: context, viewport, canvas }).promise;

    const sx = Math.max(0, Math.floor(bbox.x * canvas.width));
    const sy = Math.max(0, Math.floor(bbox.y * canvas.height));
    const sw = Math.min(canvas.width - sx, Math.floor(bbox.w * canvas.width));
    const sh = Math.min(canvas.height - sy, Math.floor(bbox.h * canvas.height));

    if (sw < 8 || sh < 8) {
      throw new Error("Selection too small");
    }

    const crop = document.createElement("canvas");
    crop.width = sw;
    crop.height = sh;
    const cropCtx = crop.getContext("2d");
    if (!cropCtx) {
      throw new Error("Unable to create crop canvas");
    }

    cropCtx.drawImage(canvas, sx, sy, sw, sh, 0, 0, sw, sh);

    const dataUrl = crop.toDataURL("image/png");
    return dataUrl.split(",", 2)[1] ?? dataUrl;
  } finally {
    pdfWorkerManager.destroyDocument(pdf);
  }
}
