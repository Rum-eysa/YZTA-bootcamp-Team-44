export interface CoverLetterRequest {
  listing_id: string;
  /** İsteğe bağlı ekstra vurgu notu (ör. "takım çalışmasını vurgula"), max 500 karakter. */
  extra_prompt?: string;
}

export interface CoverLetterResponse {
  document_id: string;
  listing_id: string;
  company_name: string;
  cover_letter_text: string;
}
