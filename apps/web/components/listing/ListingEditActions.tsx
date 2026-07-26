import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils";

interface ListingEditActionsProps {
  onCancel: () => void;
  onSave: () => void;
  isSaving: boolean;
  className?: string;
  sticky?: boolean;
  /** Header: dikey yığın. Footer: yatay sıra. */
  layout?: "stack" | "row";
  /** Mobil header yanındaki daha küçük butonlar */
  compact?: boolean;
}

export function ListingEditActions({
  onCancel,
  onSave,
  isSaving,
  className,
  sticky = true,
  layout = "row",
  compact = false,
}: ListingEditActionsProps) {
  const stacked = layout === "stack";

  const cancelButton = (
    <Button
      type="button"
      variant="outline"
      onClick={onCancel}
      disabled={isSaving}
      className={cn(
        stacked
          ? cn(
              "w-full border-primary-container text-primary-container hover:bg-primary-container hover:text-on-primary",
              compact ? "px-3 py-2 text-sm" : "px-6 py-2.5"
            )
          : "w-full sm:w-auto"
      )}
    >
      İptal
    </Button>
  );

  const saveButton = (
    <Button
      type="button"
      onClick={onSave}
      loading={isSaving}
      disabled={isSaving}
      className={cn(
        stacked
          ? cn(
              "w-full shadow-card hover:shadow-card-hover",
              compact ? "px-3 py-2.5 text-sm" : "px-6 py-3.5 text-base"
            )
          : "w-full sm:w-auto px-6 py-3 md:px-8 md:py-3.5 text-base shadow-card hover:shadow-card-hover"
      )}
    >
      Değişiklikleri Kaydet
    </Button>
  );

  return (
    <div
      className={cn(
        "flex w-full gap-sm bg-transparent",
        stacked
          ? cn(
              "flex-col items-stretch min-w-0 w-full py-0",
              !compact && "md:min-w-[13rem]"
            )
          : "flex-col py-2 sm:flex-row sm:justify-center",
        sticky && !stacked && "sticky bottom-0 z-40 py-4 sm:justify-end",
        className
      )}
    >
      {stacked ? (
        <>
          {saveButton}
          {cancelButton}
        </>
      ) : (
        <>
          {cancelButton}
          {saveButton}
        </>
      )}
    </div>
  );
}
