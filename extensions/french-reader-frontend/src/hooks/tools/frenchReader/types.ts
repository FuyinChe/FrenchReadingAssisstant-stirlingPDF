export interface NormalizedBBox {
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface OcrLineResult {
  text: string;
  confidence: number;
}

export interface OcrResult {
  text: string;
  confidence: number;
  lines: OcrLineResult[];
}

export interface FrenchReaderSelection {
  page: number;
  pageIndex: number;
  bbox: NormalizedBBox;
}
