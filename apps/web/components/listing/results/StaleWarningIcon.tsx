"use client";

const DEFAULT_MESSAGE =
  "Bu veri eski. İlan yeniden analiz edildi; güncellemenizi öneririz.";

interface StaleWarningIconProps {
  /** Hover / erişilebilirlik için uzun açıklama */
  message?: string;
  /** Başlığın yanında görünen kısa uyarı metni */
  label?: string;
}

export function StaleWarningIcon({
  message = DEFAULT_MESSAGE,
  label = "Güncel değil",
}: StaleWarningIconProps) {
  return (
    <span
      className="shrink-0 text-label-md font-medium text-error"
      title={message}
      role="status"
    >
      {label}
    </span>
  );
}
