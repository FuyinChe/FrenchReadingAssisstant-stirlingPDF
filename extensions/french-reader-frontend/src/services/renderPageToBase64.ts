import { pdfWorkerManager } from "@app/services/pdfWorkerManager";

const RENDER_SCALE = 2.5;

export async function renderPageToBase64(
  file: File | Blob,
  pageNumber: number,
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

    const dataUrl = canvas.toDataURL("image/png");
    return dataUrl.split(",", 2)[1] ?? dataUrl;
  } finally {
    pdfWorkerManager.destroyDocument(pdf);
  }
}
