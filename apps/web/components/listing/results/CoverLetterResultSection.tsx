"use client";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { FormError } from "@/components/ui/FormError";
import { Textarea } from "@/components/ui/Textarea";
import type { ListingDocument } from "@/types/listing";
import { Clipboard, Sparkles } from "lucide-react";
import { useMemo, useState } from "react";
import { StaleWarningIcon } from "./StaleWarningIcon";

// US-049: extra_prompt karakter sınırı backend şeması ile hizalı
// (bkz. apps/api/app/schemas/cover_letter.py EXTRA_PROMPT_MAX_LENGTH)
const EXTRA_PROMPT_MAX_LENGTH = 500;

interface CoverLetterResultSectionProps {
  documents: ListingDocument[];
  score: number | null;
  loading: boolean;
  error?: string;
  outdated?: boolean;
  onGenerate: (extraPrompt?: string) => void;
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
  const [extraPrompt, setExtraPrompt] = useState("");
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
      <p className="text-body-sm text-on-surface-variant">
        Şirkete ve pozisyona göre kişiselleştirilmiş bir başvuru metni oluşturun.
      </p>

      <div className="mt-3">
        <Textarea
          label="Ekstra vurgu notu (isteğe bağlı)"
          placeholder='Ör. "takım çalışmasını vurgula", "staj motivasyonumu öne çıkar"'
          value={extraPrompt}
          onChange={(event) => setExtraPrompt(event.target.value)}
          maxLength={EXTRA_PROMPT_MAX_LENGTH}
          showCount
          rows={2}
        />
      </div>

      <div className="mt-3 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-end">
        <Button
          type="button"
          onClick={() => onGenerate(extraPrompt.trim() || undefined)}
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

      {/* US-049: Bu UI ipucu eşiği (70) bilinçli olarak agent'ın "potansiyel vurgusu"
          stratejisine geçtiği eşikten (40, bkz. apps/api/app/agents/cover_letter.py
          _LOW_SCORE_THRESHOLD) farklı ve daha geniş - amaç farklı: agent eşiği önyazı
          metninin üslubunu belirler, bu UI ipucu ise 40-69 arası skorlarda da (agent
          hâlâ standart strateji kullansa bile) kullanıcıyı göndermeden önce dikkatli
          gözden geçirmeye teşvik eder. */}
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
