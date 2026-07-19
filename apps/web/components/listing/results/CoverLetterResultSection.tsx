"use client";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { FormError } from "@/components/ui/FormError";
import type { ListingDocument } from "@/types/listing";
import { Clipboard, Sparkles } from "lucide-react";
import { useMemo, useState } from "react";
import { StaleWarningIcon } from "./StaleWarningIcon";

interface CoverLetterResultSectionProps {
  documents: ListingDocument[];
  score: number | null;
  loading: boolean;
  error?: string;
  outdated?: boolean;
  onGenerate: () => void;
}

export function CoverLetterResultSection({
  documents,
  score,
  loading,
  error,
  outdated = false,
  onGenerate,
}: CoverLetterResultSectionProps) {
  const [copyFeedback, setCopyFeedback] = useState<string>();
  const coverLetter = [...documents]
    .reverse()
    .find((document) => document.doc_type === "cover_letter");
  const text = coverLetter?.cover_letter_text ?? "";

  const counts = useMemo(() => {
    const trimmed = text.trim();
    return {
      words: trimmed ? trimmed.split(/\s+/).length : 0,
      characters: text.length,
    };
  }, [text]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopyFeedback("Önyazı panoya kopyalandı.");
    } catch {
      setCopyFeedback("Önyazı kopyalanamadı.");
    }
    window.setTimeout(() => setCopyFeedback(undefined), 2500);
  };

  return (
    <Card
      title="Önyazı"
      titleAddon={
        outdated && text ? (
          <StaleWarningIcon message="Bu önyazı eski. İlan yeniden analiz edildi; güncellemenizi öneririz." />
        ) : undefined
      }
      className="border-primary/20 shadow-card"
    >
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-body-sm text-on-surface-variant">
          Şirkete ve pozisyona göre kişiselleştirilmiş bir başvuru metni oluşturun.
        </p>
        <Button
          type="button"
          onClick={onGenerate}
          loading={loading}
          variant="secondary"
          className="shrink-0"
        >
          <Sparkles className="h-4 w-4" />
          {text ? "Önyazıyı Yeniden Oluştur" : "Önyazı Oluştur"}
        </Button>
      </div>

      {loading && (
        <div
          role="status"
          aria-label="Önyazı hazırlanıyor"
          className="mt-4 animate-pulse space-y-3 rounded-xl bg-surface-container-low p-4"
        >
          <div className="h-4 w-3/4 rounded bg-surface-container-high" />
          <div className="h-4 w-full rounded bg-surface-container-high" />
          <div className="h-4 w-5/6 rounded bg-surface-container-high" />
        </div>
      )}
      <FormError message={error} />

      {score != null && score < 70 && (
        <div className="mt-4 rounded-xl border border-yellow-300 bg-yellow-50 p-3 text-body-sm text-yellow-900">
          Eşleşme skorunuz düşük. Göndermeden önce önyazıda aktarılabilir deneyimlerinizi ve
          eksik becerileri nasıl geliştirdiğinizi somut örneklerle açıklayın.
        </div>
      )}

      {text ? (
        <div className="mt-4 space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="text-label-md text-on-surface-variant">
              {counts.words} kelime • {counts.characters} karakter
            </p>
            <Button type="button" variant="outline" onClick={handleCopy}>
              <Clipboard className="h-4 w-4" />
              Kopyala
            </Button>
          </div>
          {copyFeedback && (
            <p role="status" className="text-label-md text-primary">
              {copyFeedback}
            </p>
          )}
          <article className="max-h-[520px] overflow-y-auto whitespace-pre-wrap rounded-xl border border-outline-variant bg-surface-container-low p-4 text-body-sm leading-relaxed text-on-surface">
            {text}
          </article>
        </div>
      ) : (
        !loading && (
          <p className="mt-4 rounded-xl bg-surface-container-low p-4 text-body-sm text-on-surface-variant">
            Henüz bu ilana özel önyazı oluşturulmadı.
          </p>
        )
      )}
    </Card>
  );
}
