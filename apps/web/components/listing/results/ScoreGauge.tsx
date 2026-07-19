interface ScoreGaugeProps {
  score: number;
}

function gaugeColor(score: number): string {
  if (score < 40) return "#dc2626";
  if (score < 70) return "#ca8a04";
  return "#16a34a";
}

export function ScoreGauge({ score }: ScoreGaugeProps) {
  const safeScore = Math.min(100, Math.max(0, Math.round(score)));
  const color = gaugeColor(safeScore);

  return (
    <div
      role="progressbar"
      aria-label={`Uygunluk skoru yüzde ${safeScore}`}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={safeScore}
      className="flex h-36 w-36 shrink-0 items-center justify-center rounded-full p-3"
      style={{
        background: `conic-gradient(${color} ${safeScore * 3.6}deg, #e5e7eb 0deg)`,
      }}
    >
      <div className="flex h-full w-full flex-col items-center justify-center rounded-full bg-surface-container-lowest">
        <span className="text-[32px] font-bold leading-none" style={{ color }}>
          %{safeScore}
        </span>
        <span className="mt-1 text-label-md text-on-surface-variant">Eşleşme</span>
      </div>
    </div>
  );
}
