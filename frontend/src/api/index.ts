import type { ChatMessage, UploadedFile } from "@/types/chat";
import http, { request } from "@/utils/http";

// 聊天
export const chat = async (data: ChatMessage) => {
  return await request.post("/chat", data);
};

// 获取聊天历史
export const chatHistory = async (sessionId: string | number): Promise<any> => {
  return await request.get("/chat/" + sessionId);
};

// 上传文档
export const upload = async (data: any): Promise<UploadedFile[]> => {
  const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/upload`, {
    method: "POST",
    body: data,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `上传失败: ${res.status}`);
  }

  return await res.json();
};

// 删除文档
export const deleteFile = async (id: number | string) => {
  return await request.delete(`/delete/${id}`);
};

// 获取文档列表
export const documents = async (): Promise<UploadedFile[]> => {
  return await request.get("/documents");
};
