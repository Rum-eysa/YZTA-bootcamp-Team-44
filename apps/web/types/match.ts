export interface MatchRequest {
  listing_id: string;
}

export interface ScoreBreakdown {
  required: number;
  nice_to_have: number;
  seniority: number;
  semantic_bonus?: number;
}

export interface MatchResponse {
  match_id: string;
  listing_id: string;
  score: number;
  matched_skills: string[];
  missing_skills: string[];
  score_breakdown: ScoreBreakdown | null;
  cached: boolean;
}
