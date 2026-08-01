"use client";

import { atsScoreColor, ATS_RATING_LABELS, scoreToAtsRating } from "@/lib/atsRating";

interface AtsScoreGaugeProps {
  score: number;
  label?: string;
  size?: "md" | "lg";
}

export function AtsScoreGauge({ score, label = "ATS Skor", size = "lg" }: AtsScoreGaugeProps) {
  const safeScore = Math.min(100, Math.max(0, Math.round(score)));
  const color = atsScoreColor(safeScore);
  const rating = scoreToAtsRating(safeScore);
  const dim = size === "lg" ? "h-36 w-36" : "h-24 w-24";
  const scoreClass = size === "lg" ? "text-[32px]" : "text-[22px]";

  return (
    <div
      role="progressbar"
      aria-label={`ATS skoru yüzde ${safeScore}, ${ATS_RATING_LABELS[rating]}`}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={safeScore}
      className={`flex shrink-0 items-center justify-center rounded-full p-3 ${dim}`}
      style={{
        background: `conic-gradient(${color} ${safeScore * 3.6}deg, #e5e7eb 0deg)`,
      }}
    >
      <div className="flex h-full w-full flex-col items-center justify-center rounded-full bg-surface-container-lowest">
        <span className={`${scoreClass} font-bold leading-none`} style={{ color }}>
          {safeScore}
        </span>
        <span className="mt-1 text-label-md text-on-surface-variant">{label}</span>
      </div>
    </div>
  );
}
