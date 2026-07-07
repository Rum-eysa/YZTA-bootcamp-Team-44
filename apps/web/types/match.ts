export interface MatchRequest {
  listing_id: string;
}

export interface MatchResponse {
  match_id: string;
  listing_id: string;
  score: number;
  matched_skills: string[];
  missing_skills: string[];
  cached: boolean;
}
