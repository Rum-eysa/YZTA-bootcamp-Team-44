import api from "../api";
import type { MatchRequest, MatchResponse } from "@/types/match";

export async function matchListing(payload: MatchRequest): Promise<MatchResponse> {
  const { data } = await api.post<MatchResponse>("/api/match", payload);
  return data;
}
