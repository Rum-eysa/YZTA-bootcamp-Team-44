export interface CVGenerationRequest {
  listing_id: string;
  /** İsteğe bağlı ekstra vurgu notu - verilirse CV Özet bölümü buna göre yeniden yazılır, max 500 karakter. */
  extra_prompt?: string;
}

export interface CVGenerationResponse {
  document_id: string;
  listing_id: string;
  cv_url: string;
}
