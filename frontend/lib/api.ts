import axios from "axios";

import type {
  ChatRequest,
  ChatResponse,
  HealthStatus,
  ModelInfo,
  PredictionRequest,
  PredictionResponse,
} from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
  timeout: 120000,
});

export async function getHealth(): Promise<HealthStatus> {
  const { data } = await api.get<HealthStatus>("/health", { timeout: 5000 });
  return data;
}

export async function getModelInfo(): Promise<ModelInfo> {
  const { data } = await api.get<ModelInfo>("/model-info");
  return data;
}

export async function classifyTicket(payload: PredictionRequest): Promise<PredictionResponse> {
  const { data } = await api.post<PredictionResponse>("/predict", payload);
  return data;
}

export async function sendChatMessage(payload: ChatRequest): Promise<ChatResponse> {
  const { data } = await api.post<ChatResponse>("/chat", payload);
  return data;
}
