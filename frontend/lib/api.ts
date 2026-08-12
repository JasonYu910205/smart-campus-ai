export type DashboardStats = {
  device_count: number;
  today_inspection_count: number;
  pending_maintenance_count: number;
  supplier_count: number;
};

export type Device = {
  id: number;
  device_code: string;
  device_name: string;
  device_type: string;
  location: string;
  status: string;
};

export type RetrievedChunk = {
  text: string;
  score: number;
  source: string;
  filename: string;
  page: number | null;
  chunk_index: number;
  document_id: string;
  document_type: string;
};

export type RetrievalResponse = {
  embedding_provider: string;
  embedding_model: string;
  query: string;
  top_k: number;
  chunks: RetrievedChunk[];
};

export type RagSource = {
  filename: string;
  page: number | null;
  chunk_index: number;
  score: number;
};

export type RagAnswer = {
  answer: string;
  sources: RagSource[];
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function get<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    next: { revalidate: 30 },
  });
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

async function post<T>(path: string, body: object): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as {
      detail?: string;
    } | null;
    throw new Error(
      payload?.detail ?? `API request failed: ${response.status}`,
    );
  }
  return response.json() as Promise<T>;
}

export const getStats = () => get<DashboardStats>("/api/dashboard/stats");
export const getDevices = () => get<Device[]>("/api/devices?limit=5");
export const askRag = (question: string) =>
  post<RagAnswer>("/api/rag/ask", { question });
export const retrieveRag = (query: string, topK = 5) =>
  post<RetrievalResponse>("/api/rag/retrieve", { query, top_k: topK });
