import api from "../api";
import type {
  CoverLetterResponse,
  CVGenerationResponse,
  MatchResponse,
} from "@/types/analysis";

export async function matchListing(listingId: string): Promise<MatchResponse> {
  const { data } = await api.post<MatchResponse>("/api/match", {
    listing_id: listingId,
  });
  return data;
}

export async function generateCoverLetter(
  listingId: string
): Promise<CoverLetterResponse> {
  const { data } = await api.post<CoverLetterResponse>(
    "/api/generate-cover-letter",
    { listing_id: listingId },
    { timeout: 60_000 }
  );
  return data;
}

export async function generateCV(
  listingId: string
): Promise<CVGenerationResponse> {
  const { data } = await api.post<CVGenerationResponse>(
    "/api/generate-cv",
    { listing_id: listingId },
    { timeout: 120_000 }
  );
  return data;
}
