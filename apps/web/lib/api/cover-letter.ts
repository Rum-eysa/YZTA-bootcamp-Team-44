import api from "../api";
import type { CoverLetterRequest, CoverLetterResponse } from "@/types/coverLetter";

export async function generateCoverLetter(
  payload: CoverLetterRequest
): Promise<CoverLetterResponse> {
  const { data } = await api.post<CoverLetterResponse>("/api/generate-cover-letter", payload, {
    timeout: 60_000,
  });
  return data;
}
