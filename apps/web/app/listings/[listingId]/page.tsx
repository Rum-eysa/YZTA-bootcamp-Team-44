"use client";

import { AppLayout } from "@/components/layout/AppLayout";
import { ListingEditActions } from "@/components/listing/ListingEditActions";
import { CoverLetterResultSection } from "@/components/listing/results/CoverLetterResultSection";
import { CvResultSection } from "@/components/listing/results/CvResultSection";
import { MatchResultsSection } from "@/components/listing/results/MatchResultsSection";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { FormError } from "@/components/ui/FormError";
import { TagInput } from "@/components/ui/TagInput";
import { generateCoverLetter } from "@/lib/api/cover-letter";
import { generateCv } from "@/lib/api/generate-cv";
import {
  getListing,
  reanalyzeListing,
  rematchListing,
  updateListing,
} from "@/lib/api/listings";
import { matchListing } from "@/lib/api/match";
import { getApiErrorMessage } from "@/lib/apiErrors";
import { cn } from "@/lib/utils";
import {
  APPLICATION_STAGE_LABELS,
  type ApplicationStage,
  type ListingDetail,
  type ListingUpdate,
} from "@/types/listing";
import {
  ArrowLeft,
  Building2,
  CheckCircle2,
  Circle,
  Clock,
  MapPin,
  RefreshCw,
} from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Image from "next/image";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

const EXPERIENCE_OPTIONS = ["Seçiniz", "Junior", "Mid", "Senior"];
const EDUCATION_OPTIONS = ["Seçiniz", "Lise", "Lisans", "Yüksek Lisans", "Doktora"];
const MILITARY_OPTIONS = ["Seçiniz", "Yapıldı", "Muaf", "Tecilli"];

const listingQueryKey = (listingId: string) => ["listing", listingId] as const;

function daysAgo(value: string): string {
  const created = new Date(value).getTime();
  if (Number.isNaN(created)) return "";
  const diff = Math.floor((Date.now() - created) / (1000 * 60 * 60 * 24));
  if (diff <= 0) return "bugün eklendi";
  if (diff === 1) return "1 gün önce eklendi";
  return `${diff} gün önce eklendi`;
}

function scoreSummaryClasses(score: number | null): string {
  if (score == null) return "bg-primary-fixed/20 text-primary";
  if (score < 40) return "bg-error-container/40 text-error";
  if (score < 70) return "bg-yellow-50 text-yellow-800";
  return "bg-green-50 text-green-700";
}

interface FormState {
  company: string;
  title: string;
  raw_text: string;
  location: string;
  company_about: string;
  extra_notes: string;
  benefits: string[];
  experience_level: string;
  education_level: string;
  military_status: string;
  languages: string[];
  application_stage: ApplicationStage;
}

function toForm(l: ListingDetail): FormState {
  return {
    company: l.company ?? "",
    title: l.title ?? "",
    raw_text: l.raw_text ?? "",
    location: l.location ?? "",
    company_about: l.company_about ?? "",
    extra_notes: l.extra_notes ?? "",
    benefits: l.benefits ?? [],
    experience_level: l.experience_level ?? "Seçiniz",
    education_level: l.education_level ?? "Seçiniz",
    military_status: l.military_status ?? "Seçiniz",
    languages: l.languages ?? [],
    application_stage: l.application_stage,
  };
}

function ListingDetailContent() {
  const params = useParams();
  const router = useRouter();
  const listingId = params.listingId as string;
  const queryClient = useQueryClient();

  const [form, setForm] = useState<FormState | null>(null);
  const [companyLogo, setCompanyLogo] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  const listingQuery = useQuery({
    queryKey: listingQueryKey(listingId),
    queryFn: () => getListing(listingId),
    enabled: Boolean(listingId),
  });
  const listing = listingQuery.data ?? null;

  useEffect(() => {
    setCompanyLogo(localStorage.getItem(`listing-logo:${listingId}`));
  }, [listingId]);

  useEffect(() => {
    setForm(null);
  }, [listingId]);

  useEffect(() => {
    if (listing && !form) setForm(toForm(listing));
  }, [form, listing]);

  const invalidateListing = () =>
    queryClient.invalidateQueries({ queryKey: listingQueryKey(listingId) });

  const matchMutation = useMutation({
    mutationFn: () => matchListing({ listing_id: listingId }),
    onSuccess: async (result) => {
      queryClient.setQueryData<ListingDetail>(listingQueryKey(listingId), (current) =>
        current
          ? {
              ...current,
              score: result.score,
              score_breakdown: result.score_breakdown,
              matched_skills: result.matched_skills,
              missing_skills: result.missing_skills,
            }
          : current
      );
      await invalidateListing();
    },
  });

  const reanalyzeMutation = useMutation({
    mutationFn: () => reanalyzeListing(listingId),
    onSuccess: async (updated) => {
      queryClient.setQueryData(listingQueryKey(listingId), updated);
      setForm(toForm(updated));
      await invalidateListing();
    },
  });

  const rematchMutation = useMutation({
    mutationFn: () => rematchListing(listingId),
    onSuccess: async (updated) => {
      queryClient.setQueryData(listingQueryKey(listingId), updated);
      await invalidateListing();
    },
  });

  const cvMutation = useMutation({
    mutationFn: () => generateCv({ listing_id: listingId }),
    onSuccess: async (result) => {
      queryClient.setQueryData<ListingDetail>(listingQueryKey(listingId), (current) =>
        current
          ? {
              ...current,
              documents: [
                ...current.documents.filter((document) => document.id !== result.document_id),
                {
                  id: result.document_id,
                  doc_type: "cv",
                  cv_url: result.cv_url,
                  cover_letter_text: null,
                },
              ],
            }
          : current
      );
      await invalidateListing();
    },
  });

  const coverLetterMutation = useMutation({
    mutationFn: (extraPrompt?: string) =>
      generateCoverLetter({ listing_id: listingId, extra_prompt: extraPrompt }),
    onSuccess: async (result) => {
      queryClient.setQueryData<ListingDetail>(listingQueryKey(listingId), (current) =>
        current
          ? {
              ...current,
              documents: [
                ...current.documents.filter((document) => document.id !== result.document_id),
                {
                  id: result.document_id,
                  doc_type: "cover_letter",
                  cv_url: null,
                  cover_letter_text: result.cover_letter_text,
                },
              ],
            }
          : current
      );
      await invalidateListing();
    },
  });

  const updateMutation = useMutation({
    mutationFn: (payload: ListingUpdate) => updateListing(listingId, payload),
    onSuccess: async (updated) => {
      queryClient.setQueryData(listingQueryKey(listingId), updated);
      setForm(toForm(updated));
      setSaved(true);
      window.setTimeout(() => setSaved(false), 3000);
      await invalidateListing();
    },
  });

  const update = <K extends keyof FormState>(key: K, value: FormState[K]) => {
    setForm((prev) => (prev ? { ...prev, [key]: value } : prev));
    setSaved(false);
  };

  const handleMatch = () => {
    matchMutation.reset();
    matchMutation.mutate();
  };

  const handleReanalyze = () => {
    reanalyzeMutation.reset();
    reanalyzeMutation.mutate();
  };

  const handleRematch = () => {
    rematchMutation.reset();
    rematchMutation.mutate();
  };

  const handleGenerateCv = () => {
    cvMutation.reset();
    cvMutation.mutate();
  };

  const handleGenerateCoverLetter = (extraPrompt?: string) => {
    coverLetterMutation.reset();
    coverLetterMutation.mutate(extraPrompt);
  };

  const handleCancel = () => {
    router.push("/listings");
  };

  const handleSave = () => {
    if (!form) return;
    updateMutation.reset();
    const clean = (v: string) => (v.trim() === "" || v === "Seçiniz" ? null : v.trim());
    const payload: ListingUpdate = {
      company: clean(form.company),
      title: clean(form.title),
      raw_text: form.raw_text.trim(),
      location: clean(form.location),
      company_about: clean(form.company_about),
      extra_notes: clean(form.extra_notes),
      benefits: form.benefits,
      experience_level: clean(form.experience_level),
      education_level: clean(form.education_level),
      military_status: clean(form.military_status),
      languages: form.languages,
      application_stage: form.application_stage,
    };
    updateMutation.mutate(payload);
  };

  const matchError = matchMutation.isError
    ? getApiErrorMessage(
        matchMutation.error,
        "Uygunluk hesaplanamadı. Lütfen profilinizi kontrol edip tekrar deneyin."
      )
    : undefined;
  const rematchError = rematchMutation.isError
    ? getApiErrorMessage(
        rematchMutation.error,
        "Eşleşme güncellenemedi. Lütfen tekrar deneyin."
      )
    : undefined;
  const cvError = cvMutation.isError
    ? getApiErrorMessage(cvMutation.error, "CV oluşturulamadı. Lütfen tekrar deneyin.", {
        serviceUnavailable:
          "CV oluşturma servisi şu an kullanılamıyor. Lütfen daha sonra tekrar deneyin.",
      })
    : undefined;
  const coverLetterError = coverLetterMutation.isError
    ? getApiErrorMessage(
        coverLetterMutation.error,
        "Önyazı oluşturulamadı. Lütfen tekrar deneyin.",
        {
          serviceUnavailable:
            "Önyazı servisi şu an kullanılamıyor. Lütfen daha sonra tekrar deneyin.",
        }
      )
    : undefined;

  if (listingQuery.isPending) {
    return (
      <main className="mx-auto max-w-[1024px] space-y-lg px-margin-mobile py-lg md:px-lg md:py-xl">
        <Link
          href="/listings"
          className="flex w-fit items-center gap-1 text-body-sm text-on-surface-variant transition-colors hover:text-primary"
        >
          <ArrowLeft className="h-4 w-4" />
          İlanlarım&apos;a Dön
        </Link>
        <MatchResultsSection
          score={null}
          scoreBreakdown={null}
          requiredSkills={[]}
          niceToHaveSkills={[]}
          matchedSkills={[]}
          missingSkills={[]}
          loading
          rematching={false}
          onCalculate={() => undefined}
          onRematch={() => undefined}
        />
        <CoverLetterResultSection
          documents={[]}
          score={null}
          loading
          onGenerate={() => undefined}
        />
        <CvResultSection documents={[]} loading onGenerate={() => undefined} />
      </main>
    );
  }

  if (!listing || !form) {
    return (
      <main className="max-w-[1024px] mx-auto px-margin-mobile md:px-lg py-xl text-center">
        <h1 className="text-headline-lg-mobile font-semibold mb-2">İlan bulunamadı</h1>
        <p className="text-body-sm text-on-surface-variant mb-6">
          {listingQuery.isError
            ? "İlan yüklenemedi veya erişim yetkiniz yok."
            : "Bu ilana erişilemiyor."}
        </p>
        <Link href="/listings">
          <Button>İlanlarıma Dön</Button>
        </Link>
      </main>
    );
  }

  const matchScore =
    listing.score == null ? null : Math.min(100, Math.max(0, Math.round(listing.score)));

  const steps = [
    {
      label: "İlan Analiz Edildi",
      desc: "Otomatik veri çıkarımı tamamlandı.",
      done: listing.analysis_status === "completed",
      active: false,
    },
    {
      label: "Eşleşme Skoru Hesaplandı",
      desc: listing.score != null ? `CV'niz ile ilan eşleştirildi (%${Math.round(listing.score)}).` : "Henüz hesaplanmadı.",
      done: listing.score != null,
      active: listing.score == null && listing.analysis_status === "completed",
    },
    {
      label: "Önyazı Taslağı",
      desc: "Özel yeteneklerinizi vurgulayan bir metin.",
      done: listing.documents.some((d) => d.doc_type === "cover_letter"),
      active: false,
    },
    {
      label: "Mülakat Hazırlık Paketi",
      desc: "Başvuru sonrası aktifleşir.",
      done: false,
      active: false,
    },
  ];

  return (
    <main className="max-w-[1024px] mx-auto px-margin-mobile md:px-lg py-lg md:py-xl space-y-lg">
      <Link
        href="/listings"
        className="flex w-fit items-center gap-1 text-body-sm text-on-surface-variant hover:text-primary transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        İlanlarım&apos;a Dön
      </Link>

      {saved && (
        <div
          className="rounded-lg border border-primary bg-primary-fixed/20 px-4 py-3 text-body-sm text-primary"
          role="status"
          aria-live="polite"
        >
          Değişiklikler kaydedildi.
        </div>
      )}
      <FormError
        message={
          updateMutation.isError
            ? "Değişiklikler kaydedilemedi. Lütfen tekrar deneyin."
            : undefined
        }
      />

      <section className="bg-surface-container-lowest rounded-xl p-4 md:p-6 border border-outline-variant">
        <div className="flex flex-col md:flex-row gap-lg items-start">
          <div className="flex gap-md items-start flex-1 min-w-0">
            <div className="w-20 h-20 rounded-lg overflow-hidden border border-outline-variant bg-surface flex items-center justify-center shrink-0">
              {companyLogo ? (
                <Image
                  src={companyLogo}
                  alt="Şirket logosu"
                  width={80}
                  height={80}
                  className="w-full h-full object-cover"
                  unoptimized
                />
              ) : (
                <Building2 className="w-9 h-9 text-on-surface-variant" />
              )}
            </div>

            <div className="flex-1 min-w-0 space-y-2">
              <input
                className="w-full bg-transparent border border-outline-variant rounded-lg px-3 py-1.5 text-label-md text-on-surface-variant focus:border-primary focus:ring-1 focus:ring-primary outline-none"
                placeholder="Şirket Adı"
                value={form.company}
                onChange={(e) => update("company", e.target.value)}
              />
              <input
                className="w-full bg-transparent border border-outline-variant rounded-lg px-3 py-2 text-headline-lg-mobile md:text-headline-lg font-semibold text-on-surface focus:border-primary focus:ring-1 focus:ring-primary outline-none"
                placeholder="Pozisyon"
                value={form.title}
                onChange={(e) => update("title", e.target.value)}
              />
              <div className="relative">
                <MapPin className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-on-surface-variant" />
                <input
                  className="input-field pl-8 py-1.5"
                  placeholder="Konum"
                  value={form.location}
                  onChange={(e) => update("location", e.target.value)}
                />
              </div>
              <p className="text-label-md text-on-surface-variant">{daysAgo(listing.created_at)}</p>
            </div>
          </div>

          <div className="w-full shrink-0 space-y-3 md:w-auto">
            <div className="flex items-stretch gap-md">
              <div className="flex-1 space-y-1 md:w-44">
                <label className="text-label-md text-on-surface-variant">Başvuru Aşaması</label>
                <select
                  className="input-field py-2"
                  value={form.application_stage}
                  onChange={(e) => update("application_stage", e.target.value as ApplicationStage)}
                >
                  {(Object.keys(APPLICATION_STAGE_LABELS) as ApplicationStage[]).map((s) => (
                    <option key={s} value={s}>
                      {APPLICATION_STAGE_LABELS[s]}
                    </option>
                  ))}
                </select>
              </div>
              <div
                className={cn(
                  "flex min-w-[104px] flex-col items-center justify-center rounded-xl px-5 py-2 text-center",
                  scoreSummaryClasses(matchScore)
                )}
              >
                <p className="text-[32px] font-bold leading-none">
                  {matchScore != null ? `%${matchScore}` : "—"}
                </p>
                <p className="mt-1 text-label-md opacity-80">Eşleşme Skoru</p>
              </div>
            </div>
            <ListingEditActions
              onCancel={handleCancel}
              onSave={handleSave}
              isSaving={updateMutation.isPending}
            />
          </div>
        </div>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-[1fr_300px] gap-lg items-start">
        <div className="space-y-lg min-w-0">
          <Card title="Şirket Hakkında">
            <textarea
              className="w-full h-32 bg-transparent border border-outline-variant rounded-lg p-4 text-body-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none resize-none"
              placeholder="Şirket kültürü, vizyonu ve çalışma ortamı hakkında bilgi..."
              value={form.company_about}
              onChange={(e) => update("company_about", e.target.value)}
            />
          </Card>

          <Card
            title="İlan Detayları"
            action={
              <Button
                variant="outline"
                onClick={handleReanalyze}
                loading={reanalyzeMutation.isPending}
              >
                <RefreshCw className="h-4 w-4" />
                Yeniden Analiz Et
              </Button>
            }
          >
            <p className="mb-3 text-label-md text-on-surface-variant">
              İlan metnini değiştirdiyseniz önce kaydedin, sonra yeniden analiz edin.
            </p>
            <textarea
              className="w-full h-48 bg-transparent border border-outline-variant rounded-lg p-4 text-body-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none resize-none"
              placeholder="İş tanımı ve beklentileri..."
              value={form.raw_text}
              onChange={(e) => update("raw_text", e.target.value)}
            />
            {listing.required_skills.length > 0 && (
              <div className="mt-4">
                <p className="text-label-md text-on-surface-variant mb-2">ZORUNLU BECERİLER</p>
                <div className="flex flex-wrap gap-2">
                  {listing.required_skills.map((s) => (
                    <span
                      key={s}
                      className="bg-primary-fixed/20 text-primary px-2 py-1 rounded text-label-md"
                    >
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {listing.nice_to_have.length > 0 && (
              <div className="mt-3">
                <p className="text-label-md text-on-surface-variant mb-2">TERCİH SEBEBİ</p>
                <div className="flex flex-wrap gap-2">
                  {listing.nice_to_have.map((s) => (
                    <span
                      key={s}
                      className="bg-secondary-container text-on-secondary-container px-2 py-1 rounded text-label-md"
                    >
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}
            <FormError
              message={
                reanalyzeMutation.isError
                  ? getApiErrorMessage(
                      reanalyzeMutation.error,
                      "İlan yeniden analiz edilemedi. Lütfen tekrar deneyin."
                    )
                  : undefined
              }
            />
          </Card>

          <MatchResultsSection
            score={matchScore}
            scoreBreakdown={listing.score_breakdown}
            requiredSkills={listing.required_skills}
            niceToHaveSkills={listing.nice_to_have}
            matchedSkills={listing.matched_skills}
            missingSkills={listing.missing_skills}
            loading={matchMutation.isPending}
            error={matchError}
            rematching={rematchMutation.isPending}
            rematchError={rematchError}
            outdated={Boolean(listing.match_outdated)}
            onCalculate={handleMatch}
            onRematch={handleRematch}
          />

          <CoverLetterResultSection
            documents={listing.documents}
            score={matchScore}
            loading={coverLetterMutation.isPending}
            error={coverLetterError}
            outdated={Boolean(listing.cover_letter_outdated)}
            onGenerate={handleGenerateCoverLetter}
          />

          <CvResultSection
            documents={listing.documents}
            loading={cvMutation.isPending}
            error={cvError}
            outdated={Boolean(listing.cv_outdated)}
            onGenerate={handleGenerateCv}
          />
        </div>

        <div className="space-y-lg min-w-0">
          <Card title="Aday Kriterleri">
            <div className="space-y-md">
              <div className="space-y-1">
                <label className="text-label-md text-on-surface-variant">Deneyim Seviyesi</label>
                <select
                  className="input-field"
                  value={form.experience_level}
                  onChange={(e) => update("experience_level", e.target.value)}
                >
                  {EXPERIENCE_OPTIONS.map((o) => (
                    <option key={o}>{o}</option>
                  ))}
                </select>
              </div>
              <div className="space-y-1">
                <label className="text-label-md text-on-surface-variant">Askerlik Durumu</label>
                <select
                  className="input-field"
                  value={form.military_status}
                  onChange={(e) => update("military_status", e.target.value)}
                >
                  {MILITARY_OPTIONS.map((o) => (
                    <option key={o}>{o}</option>
                  ))}
                </select>
              </div>
              <div className="space-y-1">
                <label className="text-label-md text-on-surface-variant">Eğitim Seviyesi</label>
                <select
                  className="input-field"
                  value={form.education_level}
                  onChange={(e) => update("education_level", e.target.value)}
                >
                  {EDUCATION_OPTIONS.map((o) => (
                    <option key={o}>{o}</option>
                  ))}
                </select>
              </div>
              <div className="space-y-1">
                <label className="text-label-md text-on-surface-variant">Yabancı Dil</label>
                <TagInput
                  value={form.languages}
                  onChange={(v) => update("languages", v)}
                  placeholder="Dil ekleyip Enter'a basın"
                />
              </div>
            </div>
          </Card>

          <Card title="Yan Haklar">
            <TagInput
              value={form.benefits}
              onChange={(v) => update("benefits", v)}
              placeholder="Yan hak ekleyip Enter'a basın"
            />
          </Card>

          <Card title="Ekstra Notlar">
            <textarea
              className="w-full h-24 bg-transparent border border-outline-variant rounded-lg p-3 text-body-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none resize-none"
              placeholder="Bu başvuruyla ilgili notlarınız..."
              value={form.extra_notes}
              onChange={(e) => update("extra_notes", e.target.value)}
            />
          </Card>

          <Card title="Sistem Durumu">
            <div className="space-y-md">
              {steps.map((step) => (
                <div key={step.label} className="flex gap-3">
                  <div className="shrink-0 mt-0.5">
                    {step.done ? (
                      <CheckCircle2 className="w-5 h-5 text-primary" />
                    ) : step.active ? (
                      <Clock className="w-5 h-5 text-primary" />
                    ) : (
                      <Circle className="w-5 h-5 text-outline-variant" />
                    )}
                  </div>
                  <div className="min-w-0">
                    <p
                      className={cn(
                        "text-body-sm font-semibold break-words",
                        step.done || step.active ? "text-on-surface" : "text-on-surface-variant"
                      )}
                    >
                      {step.label}
                    </p>
                    <p className="text-label-md text-on-surface-variant break-words">{step.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </Card>

        </div>
      </div>

      <div className="border-t border-outline-variant pt-lg">
        <ListingEditActions
          onCancel={handleCancel}
          onSave={handleSave}
          isSaving={updateMutation.isPending}
        />
      </div>
    </main>
  );
}

export default function ListingDetailPage() {
  return (
    <AppLayout>
      <ListingDetailContent />
    </AppLayout>
  );
}
