import api from "../api";
import type { AnalyzeRequest, AnalyzeResponse } from "@/types/analysis";

export async function analyzeListing(
  payload: AnalyzeRequest
): Promise<AnalyzeResponse> {
  const body: AnalyzeRequest = { ...payload };
  if (payload.listing_text?.trim()) {
    body.listing_text = payload.listing_text.trim();
  } else {
    delete body.listing_text;
  }
  if (payload.listing_url?.trim()) {
    body.listing_url = payload.listing_url.trim();
  } else {
    delete body.listing_url;
  }
  if (payload.company_name?.trim()) {
    body.company_name = payload.company_name.trim();
  }
  const { data } = await api.post<AnalyzeResponse>("/api/analyze", body);
  return data;
}
