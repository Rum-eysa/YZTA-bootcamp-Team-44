export interface CVGenerationRequest {
  listing_id: string;
}

export interface CVGenerationResponse {
  document_id: string;
  listing_id: string;
  cv_url: string;
}
