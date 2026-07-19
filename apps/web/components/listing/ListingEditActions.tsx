import { Button } from "@/components/ui/Button";

interface ListingEditActionsProps {
  onCancel: () => void;
  onSave: () => void;
  isSaving: boolean;
}

export function ListingEditActions({
  onCancel,
  onSave,
  isSaving,
}: ListingEditActionsProps) {
  return (
    <div className="flex w-full flex-col gap-sm sm:flex-row sm:justify-end">
      <Button
        type="button"
        variant="outline"
        onClick={onCancel}
        disabled={isSaving}
        className="w-full sm:w-auto"
      >
        İptal
      </Button>
      <Button
        type="button"
        onClick={onSave}
        loading={isSaving}
        disabled={isSaving}
        className="w-full bg-primary text-on-primary sm:w-auto"
      >
        Değişiklikleri Kaydet
      </Button>
    </div>
  );
}
