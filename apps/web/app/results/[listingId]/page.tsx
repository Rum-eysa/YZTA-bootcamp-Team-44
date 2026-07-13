"use client";

import { AppLayout } from "@/components/layout/AppLayout";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { FormError } from "@/components/ui/FormError";
import { Spinner } from "@/components/ui/Spinner";
import { Toast } from "@/components/ui/Toast";
import { getAnalysisResult } from "@/lib/api/analysis";
import { generateCoverLetter } from "@/lib/api/coverLetter";
import { generateCv } from "@/lib/api/cvGeneration";
import { matchListing } from "@/lib/api/match";
import { getApiErrorMessage } from "@/lib/apiErrors";
import type { AnalyzeResponse } from "@/types/analysis";
import type { CoverLetterResponse } from "@/types/coverLetter";
import type { CVGenerationResponse } from "@/types/cvGeneration";
import type { MatchResponse } from "@/types/match";
import {
  ArrowLeft,
  CheckCircle2,
  Copy,
  Download,
  ExternalLink,
  FileText,
  Sparkles,
  Target,
} from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

function AnalyzeResultContent() {
  const params = useParams();
  const listingId = params.listingId as string;
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const [matchResult, setMatchResult] = useState<MatchResponse | null>(null);
  const [matchLoading, setMatchLoading] = useState(false);
  const [matchError, setMatchError] = useState<string>();

  const [cvResult, setCvResult] = useState<CVGenerationResponse | null>(null);
  const [cvLoading, setCvLoading] = useState(false);
  const [cvError, setCvError] = useState<string>();

  const [coverLetterResult, setCoverLetterResult] = useState<CoverLetterResponse | null>(null);
  const [coverLetterLoading, setCoverLetterLoading] = useState(false);
  const [coverLetterError, setCoverLetterError] = useState<string>();
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const data = getAnalysisResult(listingId);
    setResult(data);
    setLoading(false);
  }, [listingId]);

  async function handleMatch() {
    setMatchError(undefined);
    setMatchLoading(true);
    try {
      const data = await matchListing({ listing_id: listingId });
      setMatchResult(data);
    } catch (err: unknown) {
      setMatchError(
        getApiErrorMessage(
          err,
          "Uygunluk hesaplanamadı. Lütfen profilinizi kontrol edip tekrar deneyin."
        )
      );
    } finally {
      setMatchLoading(false);
    }
  }

  async function handleGenerateCv() {
    setCvError(undefined);
    setCvLoading(true);
    try {
      const data = await generateCv({ listing_id: listingId });
      setCvResult(data);
    } catch (err: unknown) {
      setCvError(
        getApiErrorMessage(err, "CV oluşturulamadı. Lütfen tekrar deneyin.", {
          serviceUnavailable:
            "CV oluşturma servisi şu an kullanılamıyor. Lütfen daha sonra tekrar deneyin.",
        })
      );
    } finally {
      setCvLoading(false);
    }
  }

  async function handleGenerateCoverLetter() {
    setCoverLetterError(undefined);
    setCoverLetterLoading(true);
    try {
      const data = await generateCoverLetter({ listing_id: listingId });
      setCoverLetterResult(data);
    } catch (err: unknown) {
      setCoverLetterError(
        getApiErrorMessage(
          err,
          "Önyazı oluşturulamadı. Lütfen tekrar deneyin.",
          {
            serviceUnavailable:
              "Önyazı servisi şu an kullanılamıyor. Lütfen daha sonra tekrar deneyin.",
          }
        )
      );
    } finally {
      setCoverLetterLoading(false);
    }
  }

  async function handleCopyCoverLetter() {
    if (!coverLetterResult?.cover_letter_text) return;
    try {
      await navigator.clipboard.writeText(coverLetterResult.cover_letter_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCoverLetterError("Önyazı panoya kopyalanamadı.");
    }
  }

  if (loading) {
    return (
      <div className="py-3xl">
        <Spinner label="Sonuçlar yükleniyor..." />
      </div>
    );
  }

  if (!result) {
    return (
      <main className="max-w-[1024px] mx-auto px-margin-mobile md:px-lg py-xl text-center">
        <h1 className="text-headline-lg-mobile font-semibold mb-2">Sonuç bulunamadı</h1>
        <p className="text-body-sm text-on-surface-variant mb-6">
          Analiz sonucu oturumda bulunamadı. Lütfen yeni bir analiz başlatın.
        </p>
        <Link href="/apply">
          <Button>Yeni Analiz Başlat</Button>
        </Link>
      </main>
    );
  }

  const confidencePercent = Math.round(result.confidence * 100);
  const matchScore = matchResult
    ? Math.min(100, Math.max(0, Math.round(matchResult.score)))
    : 0;

  return (
    <main className="max-w-[1024px] mx-auto px-margin-mobile md:px-lg py-lg md:py-xl space-y-lg">
      <div className="flex items-center gap-2 text-primary">
        <CheckCircle2 className="w-5 h-5" />
        <span className="text-body-sm font-semibold">Analiz tamamlandı</span>
      </div>

      <Card>
        <h1 className="text-headline-lg-mobile md:text-headline-lg font-semibold text-on-surface mb-2">
          {result.position_title || "Pozisyon"}
        </h1>
        <div className="flex flex-wrap gap-2 mb-4">
          <span className="bg-primary-fixed/20 text-primary px-3 py-1 rounded-full text-label-md capitalize">
            {result.seniority || "Belirsiz"}
          </span>
          <span className="bg-secondary-container text-on-secondary-container px-3 py-1 rounded-full text-label-md">
            Güven: %{confidencePercent}
          </span>
        </div>
        <p className="text-body-sm text-on-surface-variant">İlan ID: {result.listing_id}</p>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-lg">
        <Card title="Zorunlu Beceriler">
          <div className="flex flex-wrap gap-2">
            {result.required_skills.length > 0 ? (
              result.required_skills.map((skill) => (
                <span
                  key={skill}
                  className="bg-primary-fixed/20 text-primary px-2 py-1 rounded font-label-md"
                >
                  {skill}
                </span>
              ))
            ) : (
              <p className="text-body-sm text-on-surface-variant">Belirlenemedi</p>
            )}
          </div>
        </Card>

        <Card title="Tercih Edilen Beceriler">
          <div className="flex flex-wrap gap-2">
            {result.nice_to_have.length > 0 ? (
              result.nice_to_have.map((skill) => (
                <span
                  key={skill}
                  className="bg-secondary-container text-on-secondary-container px-2 py-1 rounded font-label-md"
                >
                  {skill}
                </span>
              ))
            ) : (
              <p className="text-body-sm text-on-surface-variant">Belirlenemedi</p>
            )}
          </div>
        </Card>
      </div>

      <Card
        title="Başvuru Araçları"
        className="overflow-hidden bg-gradient-to-br from-surface-container-lowest to-primary-fixed/10 shadow-card"
      >
        <p className="text-body-sm text-on-surface-variant mb-4">
          Analiz tamamlandı. Profilinize göre uygunluk skorunu hesaplayabilir, ilana özel CV ve
          önyazı oluşturabilirsiniz.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="rounded-2xl border border-outline-variant bg-surface-container-lowest p-5 space-y-3 shadow-card transition-shadow hover:shadow-card-hover">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-fixed/20 text-primary">
              <Target className="w-5 h-5" />
            </div>
            <div className="flex items-center justify-between gap-2">
              <span className="text-label-md font-semibold">Uygunluk</span>
              {matchResult && (
                <span className="rounded-full bg-primary-fixed/20 px-2 py-1 text-label-md text-primary">
                  %{matchScore}
                </span>
              )}
            </div>
            <p className="text-body-sm text-on-surface-variant">
              Profiliniz ile ilan arasındaki eşleşme skorunu hesaplar.
            </p>
            <Button onClick={handleMatch} loading={matchLoading} className="w-full">
              Uygunluğumu Hesapla
            </Button>
            <FormError message={matchError} />
          </div>

          <div className="rounded-2xl border border-outline-variant bg-surface-container-lowest p-5 space-y-3 shadow-card transition-shadow hover:shadow-card-hover">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-fixed/20 text-primary">
              <FileText className="w-5 h-5" />
            </div>
            <div className="flex items-center justify-between gap-2">
              <span className="text-label-md font-semibold">CV</span>
              {cvResult && (
                <span className="rounded-full bg-secondary-container px-2 py-1 text-label-md text-on-secondary-container">
                  Hazır
                </span>
              )}
            </div>
            <p className="text-body-sm text-on-surface-variant">
              İlana özel PDF CV oluşturur ve indirme linki sunar.
            </p>
            <Button onClick={handleGenerateCv} loading={cvLoading} className="w-full">
              CV Oluştur
            </Button>
          </div>

          <div className="rounded-2xl border border-outline-variant bg-surface-container-lowest p-5 space-y-3 shadow-card transition-shadow hover:shadow-card-hover">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-fixed/20 text-primary">
              <Sparkles className="w-5 h-5" />
            </div>
            <div className="flex items-center justify-between gap-2">
              <span className="text-label-md font-semibold">Önyazı</span>
              {coverLetterResult && (
                <span className="rounded-full bg-secondary-container px-2 py-1 text-label-md text-on-secondary-container">
                  Hazır
                </span>
              )}
            </div>
            <p className="text-body-sm text-on-surface-variant">
              Şirkete özel önyazı metni üretir.
            </p>
            <Button onClick={handleGenerateCoverLetter} loading={coverLetterLoading} className="w-full">
              Önyazı Oluştur
            </Button>
            <FormError message={coverLetterError} />
          </div>
        </div>
      </Card>

      {matchResult && (
        <Card title="Uygunluk Sonucu" className="shadow-card-hover">
          <div className="grid grid-cols-1 items-center gap-lg lg:grid-cols-[180px_1fr]">
            <div className="flex flex-col items-center gap-3">
              <div
                role="progressbar"
                aria-label={`Uygunluk skoru yüzde ${matchScore}`}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-valuenow={matchScore}
                className="flex h-36 w-36 items-center justify-center rounded-full p-3"
                style={{
                  background: `conic-gradient(#10b981 ${matchScore * 3.6}deg, #e7eefe 0deg)`,
                }}
              >
                <div className="flex h-full w-full flex-col items-center justify-center rounded-full bg-surface-container-lowest">
                  <span className="text-headline-lg font-semibold text-primary">%{matchScore}</span>
                  <span className="text-label-md text-on-surface-variant">Eşleşme</span>
                </div>
              </div>
              {matchResult.cached && (
                <span className="bg-secondary-container text-on-secondary-container px-2 py-1 rounded-full text-label-md">
                  Önbellekten
                </span>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-lg">
              <div className="rounded-xl bg-primary-fixed/10 p-4">
                <h3 className="text-label-md font-semibold text-on-surface mb-3">
                  Eşleşen Beceriler
                </h3>
                <div className="flex flex-wrap gap-2">
                  {matchResult.matched_skills.length > 0 ? (
                    matchResult.matched_skills.map((skill) => (
                      <span
                        key={skill}
                        className="bg-primary-fixed/20 text-primary px-2 py-1 rounded font-label-md"
                      >
                        {skill}
                      </span>
                    ))
                  ) : (
                    <p className="text-body-sm text-on-surface-variant">
                      Eşleşen beceri bulunamadı
                    </p>
                  )}
                </div>
              </div>

              <div className="rounded-xl bg-error-container/30 p-4">
                <h3 className="text-label-md font-semibold text-on-surface mb-3">
                  Eksik Beceriler
                </h3>
                <div className="flex flex-wrap gap-2">
                  {matchResult.missing_skills.length > 0 ? (
                    matchResult.missing_skills.map((skill) => (
                      <span
                        key={skill}
                        className="bg-error-container text-on-error-container px-2 py-1 rounded font-label-md"
                      >
                        {skill}
                      </span>
                    ))
                  ) : (
                    <p className="text-body-sm text-on-surface-variant">Eksik beceri yok</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </Card>
      )}

      {cvLoading && (
        <Card title="CV Hazırlanıyor">
          <Spinner label="CV oluşturuluyor, lütfen bekleyin..." className="py-6" />
        </Card>
      )}

      {cvResult && (
        <Card title="CV Hazır">
          <div className="flex flex-wrap justify-end gap-3 mb-4">
            <a href={cvResult.cv_url} download target="_blank" rel="noopener noreferrer">
              <Button variant="outline">
                <Download className="w-4 h-4" />
                İndir
              </Button>
            </a>
            <a href={cvResult.cv_url} target="_blank" rel="noopener noreferrer">
              <Button variant="outline">
                <ExternalLink className="w-4 h-4" />
                Yeni Sekmede Aç
              </Button>
            </a>
          </div>
          <iframe
            src={cvResult.cv_url}
            title="CV önizleme"
            className="w-full h-[600px] rounded-lg border border-outline-variant bg-surface-container-low"
          />
        </Card>
      )}

      {coverLetterResult && (
        <Card
          title={`Önyazı — ${coverLetterResult.company_name}`}
          className="border-primary/30 shadow-card-hover"
        >
          <div className="flex justify-end mb-3">
            <Button variant="outline" onClick={handleCopyCoverLetter}>
              <Copy className="w-4 h-4" />
              {copied ? "Kopyalandı" : "Panoya Kopyala"}
            </Button>
          </div>
          <div className="rounded-xl bg-gradient-to-br from-surface-container-low to-primary-fixed/10 p-5 whitespace-pre-wrap text-body-sm leading-relaxed text-on-surface">
            {coverLetterResult.cover_letter_text}
          </div>
        </Card>
      )}

      <div className="flex gap-3">
        <Link href="/apply">
          <Button variant="outline">
            <ArrowLeft className="w-4 h-4" />
            Yeni Analiz
          </Button>
        </Link>
        <Link href="/profile">
          <Button>Profile Git</Button>
        </Link>
      </div>

      <Toast message={cvError} variant="error" onClose={() => setCvError(undefined)} />
    </main>
  );
}

export default function AnalyzeResultPage() {
  return (
    <AppLayout>
      <AnalyzeResultContent />
    </AppLayout>
  );
}
