import api from "../api";
import type { CVGenerationRequest, CVGenerationResponse } from "@/types/cvGeneration";

export async function generateCv(
  payload: CVGenerationRequest
): Promise<CVGenerationResponse> {
  const { data } = await api.post<CVGenerationResponse>("/api/generate-cv", payload, {
    timeout: 120_000,
  });
  return data;
}
