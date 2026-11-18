export interface ChatMessage {
  sessionId: string;
  role: string;
  content: string;
  id?: string;
}

export interface UploadedFile {
  filename: string;
  original_filename: string;
  size: number;
  chunks: number;
  status: string;
  doc_id: number;
}

export interface UploadItem {
  status: "uploading" | "done" | "error";
  doc_id: number;
  filename: string;
  original_filename: string;
}
