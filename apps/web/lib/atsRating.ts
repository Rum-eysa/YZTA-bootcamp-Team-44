import type { AtsRating } from "@/types/atsCheck";

export const ATS_RATING_LABELS: Record<AtsRating, string> = {
  mukemmel: "Mükemmel",
  iyi: "İyi",
  orta: "Orta",
  iyilestirilebilir: "İyileştirilebilir",
  iyilestirilmeli: "İyileştirilmeli",
};

export function scoreToAtsRating(score: number): AtsRating {
  if (score >= 90) return "mukemmel";
  if (score >= 75) return "iyi";
  if (score >= 55) return "orta";
  if (score >= 35) return "iyilestirilebilir";
  return "iyilestirilmeli";
}

/** 5 seviyeli ATS renk bandı */
export function atsScoreColor(score: number): string {
  const rating = scoreToAtsRating(score);
  switch (rating) {
    case "mukemmel":
      return "#16a34a";
    case "iyi":
      return "#15803d";
    case "orta":
      return "#ca8a04";
    case "iyilestirilebilir":
      return "#ea580c";
    default:
      return "#dc2626";
  }
}

export const ATS_CATEGORY_LABELS = {
  tasarim: "Tasarım",
  duzen: "Düzen",
  icerik: "İçerik",
} as const;
