"use client";

import { AppHeader } from "@/components/layout/AppHeader";
import { AuthGuard } from "@/components/auth/AuthGuard";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { getAnalysisResult } from "@/lib/api/analysis";
import { generateCoverLetter, generateCV, matchListing } from "@/lib/api/results";
import type {
  AnalyzeResponse,
  CoverLetterResponse,
  CVGenerationResponse,
  MatchResponse,
} from "@/types/analysis";
import {
  ArrowLeft,
  CheckCircle2,
  Copy,
  Download,
  FileText,
  Mail,
  XCircle,
} from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

function errorMessage(err: unknown, fallback: string): string {
  const response = (err as { response?: { status?: number; data?: { detail?: string } } })
    ?.response;
  if (response?.status === 503) {
    return "AI servisi şu an kullanılamıyor (kota/bağlantı). Daha sonra tekrar deneyin.";
  }
  return typeof response?.data?.detail === "string" ? response.data.detail : fallback;
}

function scoreColor(score: number): string {
  if (score >= 70) return "text-green-600";
  if (score >= 40) return "text-amber-600";
  return "text-red-600";
}

function scoreStroke(score: number): string {
  if (score >= 70) return "#16a34a";
  if (score >= 40) return "#d97706";
  return "#dc2626";
}

function ScoreGauge({ score }: { score: number }) {
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - score / 100);
  return (
    <div className="relative w-36 h-36 mx-auto">
      <svg viewBox="0 0 128 128" className="w-full h-full -rotate-90">
        <circle cx="64" cy="64" r={radius} fill="none" stroke="#e5e7eb" strokeWidth="10" />
        <circle
          cx="64"
          cy="64"
          r={radius}
          fill="none"
          stroke={scoreStroke(score)}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 0.8s ease" }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`text-3xl font-bold ${scoreColor(score)}`}>{Math.round(score)}</span>
        <span className="text-label-md text-on-surface-variant">/ 100</span>
      </div>
    </div>
  );
}

function MatchSection({ listingId }: { listingId: string }) {
  const [match, setMatch] = useState<MatchResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    matchListing(listingId)
      .then(setMatch)
      .catch((err) => setError(errorMessage(err, "Eşleştirme skoru hesaplanamadı.")))
      .finally(() => setLoading(false));
  }, [listingId]);

  if (loading) {
    return (
      <Card title="Uygunluk Skoru">
        <Spinner label="Profilin ilanla eşleştiriliyor..." />
      </Card>
    );
  }
  if (error || !match) {
    return (
      <Card title="Uygunluk Skoru">
        <p className="text-body-sm text-red-600">{error}</p>
      </Card>
    );
  }

  const totalSkills = match.matched_skills.length + match.missing_skills.length;

  return (
    <Card title="Uygunluk Skoru">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-lg items-center">
        <div>
          <ScoreGauge score={match.score} />
          {totalSkills > 0 && (
            <p className="text-center text-body-sm text-on-surface-variant mt-2">
              {match.matched_skills.length} / {totalSkills} beceri eşleşti
            </p>
          )}
        </div>
        <div className="space-y-3">
          <div>
            <h3 className="text-label-md font-semibold text-on-surface mb-1">
              Eşleşen Beceriler
            </h3>
            <div className="flex flex-wrap gap-2">
              {match.matched_skills.length > 0 ? (
                match.matched_skills.map((s) => (
                  <span
                    key={s}
                    className="inline-flex items-center gap-1 bg-green-100 text-green-800 px-2 py-1 rounded text-label-md"
                  >
                    <CheckCircle2 className="w-3 h-3" /> {s}
                  </span>
                ))
              ) : (
                <p className="text-body-sm text-on-surface-variant">
                  Doğrudan eşleşme yok — aşağıdaki eksik becerilere odaklan.
                </p>
              )}
            </div>
          </div>
          <div>
            <h3 className="text-label-md font-semibold text-on-surface mb-1">
              Eksik Beceriler
            </h3>
            <div className="flex flex-wrap gap-2">
              {match.missing_skills.length > 0 ? (
                match.missing_skills.map((s) => (
                  <span
                    key={s}
                    className="inline-flex items-center gap-1 bg-red-100 text-red-800 px-2 py-1 rounded text-label-md"
                  >
                    <XCircle className="w-3 h-3" /> {s}
                  </span>
                ))
              ) : (
                <p className="text-body-sm text-on-surface-variant">
                  Eksik zorunlu beceri yok 🎉
                </p>
              )}
            </div>
          </div>
          {match.missing_skills.length > 0 && (
            <p className="text-body-sm text-on-surface-variant">
              Öneri: Önyazın eksik becerileri öğrenmeye açıklıkla dengeler; ayrıca bu
              becerilere yönelik kısa bir kurs/proje profilini güçlendirir.
            </p>
          )}
        </div>
      </div>
    </Card>
  );
}

function CoverLetterSection({ listingId }: { listingId: string }) {
  const [letter, setLetter] = useState<CoverLetterResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const generate = () => {
    setLoading(true);
    setError(null);
    generateCoverLetter(listingId)
      .then(setLetter)
      .catch((err) => setError(errorMessage(err, "Önyazı üretilemedi.")))
      .finally(() => setLoading(false));
  };

  const copy = async () => {
    if (!letter) return;
    await navigator.clipboard.writeText(letter.cover_letter_text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Card title="Kişiselleştirilmiş Önyazı">
      {!letter && !loading && (
        <div className="space-y-3">
          <p className="text-body-sm text-on-surface-variant">
            Profilin ve bu ilanın analizine göre, başvurduğun şirkete özel bir önyazı
            üretilir. Üretim birkaç saniye sürebilir.
          </p>
          {error && <p className="text-body-sm text-red-600">{error}</p>}
          <Button onClick={generate}>
            <Mail className="w-4 h-4" /> Önyazı Üret
          </Button>
        </div>
      )}
      {loading && <Spinner label="Önyazı yazılıyor (AI)..." />}
      {letter && (
        <div className="space-y-3">
          <p className="text-label-md text-on-surface-variant">
            {letter.company_name} için üretildi · {letter.cover_letter_text.length}{" "}
            karakter
          </p>
          <div className="bg-surface-bright border border-outline-variant rounded-lg p-4 whitespace-pre-wrap text-body-sm text-on-surface max-h-96 overflow-y-auto">
            {letter.cover_letter_text}
          </div>
          <Button variant="outline" onClick={copy}>
            <Copy className="w-4 h-4" /> {copied ? "Kopyalandı ✓" : "Panoya Kopyala"}
          </Button>
        </div>
      )}
    </Card>
  );
}

function CVSection({ listingId }: { listingId: string }) {
  const [cv, setCv] = useState<CVGenerationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generate = () => {
    setLoading(true);
    setError(null);
    generateCV(listingId)
      .then(setCv)
      .catch((err) => setError(errorMessage(err, "CV üretilemedi.")))
      .finally(() => setLoading(false));
  };

  return (
    <Card title="İlana Özel CV (PDF)">
      {!cv && !loading && (
        <div className="space-y-3">
          <p className="text-body-sm text-on-surface-variant">
            Profil bilgilerinden LaTeX ile derlenmiş bir PDF CV üretilir. Derleme 15
            saniyeye kadar sürebilir.
          </p>
          {error && <p className="text-body-sm text-red-600">{error}</p>}
          <Button onClick={generate}>
            <FileText className="w-4 h-4" /> CV Üret
          </Button>
        </div>
      )}
      {loading && <Spinner label="CV derleniyor (LaTeX → PDF)..." />}
      {cv && (
        <div className="space-y-3">
          <p className="text-body-sm text-on-surface">CV hazır ✓</p>
          <a href={cv.cv_url} target="_blank" rel="noopener noreferrer">
            <Button>
              <Download className="w-4 h-4" /> PDF&apos;i İndir / Aç
            </Button>
          </a>
        </div>
      )}
    </Card>
  );
}

function AnalyzeResultContent() {
  const params = useParams();
  const listingId = params.id as string;
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const data = getAnalysisResult(listingId);
    setResult(data);
    setLoading(false);
  }, [listingId]);

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

      <MatchSection listingId={listingId} />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-lg items-start">
        <CoverLetterSection listingId={listingId} />
        <CVSection listingId={listingId} />
      </div>

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
    </main>
  );
}

export default function AnalyzeResultPage() {
  return (
    <div className="min-h-screen bg-surface-bright">
      <AppHeader />
      <AuthGuard>
        <AnalyzeResultContent />
      </AuthGuard>
    </div>
  );
}
