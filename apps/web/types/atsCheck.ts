export type AtsRating =
  | "mukemmel"
  | "iyi"
  | "orta"
  | "iyilestirilebilir"
  | "iyilestirilmeli";

export type AtsCategoryKey = "tasarim" | "duzen" | "icerik";

export interface AtsCategoryScore {
  score: number;
  rating: AtsRating;
  feedback: string;
}

export interface AtsCheckResponse {
  overall_score: number;
  overall_rating: AtsRating;
  categories: Record<AtsCategoryKey, AtsCategoryScore>;
  summary: string;
  suggestions: string[];
}
