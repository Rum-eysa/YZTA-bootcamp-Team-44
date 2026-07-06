import api from "../api";
import type { AnalyzeRequest, AnalyzeResponse } from "@/types/analysis";

export async function analyzeListing(
  payload: AnalyzeRequest
): Promise<AnalyzeResponse> {
  const body: AnalyzeRequest = {};
  if (payload.listing_text?.trim()) {
    body.listing_text = payload.listing_text.trim();
  }
  if (payload.listing_url?.trim()) {
    body.listing_url = payload.listing_url.trim();
  }
  if (payload.company_name?.trim()) {
    body.company_name = payload.company_name.trim();
  }
  const { data } = await api.post<AnalyzeResponse>("/api/analyze", body);
  return data;
}

export function saveAnalysisResult(result: AnalyzeResponse) {
  sessionStorage.setItem(`analysis:${result.listing_id}`, JSON.stringify(result));
}

export function getAnalysisResult(listingId: string): AnalyzeResponse | null {
  const raw = sessionStorage.getItem(`analysis:${listingId}`);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AnalyzeResponse;
  } catch {
    return null;
  }
}
