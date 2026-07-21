"use client";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { FormError } from "@/components/ui/FormError";
import { Textarea } from "@/components/ui/Textarea";
import type { ListingDocument } from "@/types/listing";
import { Download, ExternalLink, FileText } from "lucide-react";
import { useState } from "react";
import { StaleWarningIcon } from "./StaleWarningIcon";

// US-050: extra_prompt karakter sınırı backend şeması ile hizalı
// (bkz. apps/api/app/schemas/cv_generation.py EXTRA_PROMPT_MAX_LENGTH)
const EXTRA_PROMPT_MAX_LENGTH = 500;

interface CvResultSectionProps {
  documents: ListingDocument[];
  loading: boolean;
  error?: string;
  outdated?: boolean;
  onGenerate: (extraPrompt?: string) => void;
}

export function CvResultSection({
  documents,
  loading,
  error,
  outdated = false,
  onGenerate,
}: CvResultSectionProps) {
  const cv = [...documents]
    .reverse()
    .find((document) => document.doc_type === "cv");
  const [downloadError, setDownloadError] = useState<string>();
  const [extraPrompt, setExtraPrompt] = useState("");

  const handleDownload = async () => {
    if (!cv?.cv_url) return;
    setDownloadError(undefined);

    try {
      const response = await fetch(cv.cv_url);
      if (!response.ok) throw new Error("CV indirilemedi");

      const objectUrl = URL.createObjectURL(await response.blob());
      const anchor = document.createElement("a");
      anchor.href = objectUrl;
      anchor.download = "CareerTrack-CV.pdf";
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(objectUrl);
    } catch {
      setDownloadError(
        "PDF doğrudan indirilemedi. Dosyayı yeni sekmede açıp tarayıcınızdan indirebilirsiniz.",
      );
    }
  };

  return (
    <Card
      title="İlana Özel CV"
      titleAddon={
        outdated && cv ? (
          <StaleWarningIcon message="Bu CV eski. İlan yeniden analiz edildi; güncellemenizi öneririz." />
        ) : undefined
      }
      className="border-primary/20 shadow-card"
    >
      <p className="text-body-sm text-on-surface-variant">
        Profiliniz ve ilan gereksinimleriyle uyumlu PDF özgeçmiş oluşturun.
      </p>

      <div className="mt-3">
        <Textarea
          label="Ekstra vurgu notu (isteğe bağlı)"
          placeholder='Ör. "takım çalışmasını vurgula", "eşleşme düşükse motivasyonumu öne çıkar"'
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
          <FileText className="h-4 w-4" />
          {cv ? "CV’yi Yeniden Oluştur" : "CV Oluştur"}
        </Button>
      </div>

      {loading && (
        <div
          role="status"
          aria-label="CV hazırlanıyor"
          className="mt-4 animate-pulse space-y-3 rounded-xl bg-surface-container-low p-4"
        >
          <div className="h-4 w-2/3 rounded bg-surface-container-high" />
          <div className="h-48 rounded bg-surface-container-high" />
        </div>
      )}
      <FormError message={error} />

      {cv?.cv_url ? (
        <div className="mt-4 space-y-3">
          <div className="flex flex-wrap justify-end gap-2">
            <a
              href={cv.cv_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-lg border border-primary px-4 py-2 text-label-md font-semibold text-primary transition-colors hover:bg-primary hover:text-on-primary"
            >
              <ExternalLink className="h-4 w-4" />
              Yeni Sekmede Aç
            </a>
            <Button
              type="button"
              onClick={() => void handleDownload()}
              className="inline-flex items-center gap-2"
            >
              <Download className="h-4 w-4" />
              PDF İndir
            </Button>
          </div>
          <FormError message={downloadError} />
          <div className="overflow-hidden rounded-xl border border-outline-variant bg-surface">
            <iframe
              src={cv.cv_url}
              title="Oluşturulan CV PDF önizlemesi"
              className="h-[520px] w-full"
            />
          </div>
          <p className="text-label-md text-on-surface-variant">
            PDF tarayıcıda görüntülenemiyorsa yeni sekmede açabilir veya
            indirebilirsiniz.
          </p>
        </div>
      ) : (
        !loading && (
          <p className="mt-4 rounded-xl bg-surface-container-low p-4 text-body-sm text-on-surface-variant">
            Henüz bu ilana özel CV oluşturulmadı.
          </p>
        )
      )}
    </Card>
  );
}
