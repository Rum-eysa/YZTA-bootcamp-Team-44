export interface AnalyzeRequest {
  listing_text?: string;
  listing_url?: string;
  company_name?: string;
}

export interface AnalyzeResponse {
  listing_id: string;
  required_skills: string[];
  nice_to_have: string[];
  seniority: string;
  position_title: string;
  confidence: number;
}

export interface MatchResponse {
  match_id: string;
  listing_id: string;
  score: number;
  matched_skills: string[];
  missing_skills: string[];
  cached: boolean;
}

export interface CoverLetterResponse {
  document_id: string;
  listing_id: string;
  company_name: string;
  cover_letter_text: string;
}

export interface CVGenerationResponse {
  document_id: string;
  listing_id: string;
  cv_url: string;
}
