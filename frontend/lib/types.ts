export type PredictionRequest = {
  title: string;
  description: string;
};

export type PredictionResponse = {
  category: string;
  priority: string;
  confidence: number;
  agent_solution: string;
  customer_reply: string;
  model_used: string;
  vectorizer_used: string;
};

export type ModelInfo = {
  selected_model: string;
  model_path: string;
  metrics: Record<string, unknown>;
};

export type HealthStatus = {
  status: string;
  model_loaded: boolean;
  model_name: string | null;
  vectorizer_name?: string | null;
  response_model_name?: string | null;
  response_mode?: string | null;
  qwen_ready?: boolean;
};

export type ChatRequest = {
  message: string;
};

export type ChatResponse = {
  reply: string;
  model_used: string;
  examples_used: number;
};
