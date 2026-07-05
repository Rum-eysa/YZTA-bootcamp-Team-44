export interface AnalyzeRequest {
  listing_text?: string;
  listing_url?: string;
}

export interface AnalyzeResponse {
  listing_id: string;
  required_skills: string[];
  nice_to_have: string[];
  seniority: string;
  position_title: string;
  confidence: number;
}
