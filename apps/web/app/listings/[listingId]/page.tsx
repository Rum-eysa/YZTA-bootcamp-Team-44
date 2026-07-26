"use client";

import { AppLayout } from "@/components/layout/AppLayout";
import { ListingEditActions } from "@/components/listing/ListingEditActions";
import { CoverLetterResultSection } from "@/components/listing/results/CoverLetterResultSection";
import { CvResultSection } from "@/components/listing/results/CvResultSection";
import { MatchResultsSection } from "@/components/listing/results/MatchResultsSection";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { FormError } from "@/components/ui/FormError";
import { Modal } from "@/components/ui/Modal";
import { SectionEditButton } from "@/components/ui/SectionEditButton";
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
import {
  CV_TEMPLATES,
  DEFAULT_CV_TEMPLATE,
  getCvTemplate,
  type CvTemplateId,
} from "@/lib/cv-templates";
import { cn } from "@/lib/utils";
import type { ListingDetail, ListingUpdate } from "@/types/listing";
import { ArrowLeft, Building2, ImagePlus, RefreshCw } from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Image from "next/image";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

const listingQueryKey = (listingId: string) => ["listing", listingId] as const;

function daysAgo(value: string): string {
  const created = new Date(value).getTime();
  if (Number.isNaN(created)) return "";
  const diff = Math.floor((Date.now() - created) / (1000 * 60 * 60 * 24));
  if (diff <= 0) return "bugün eklendi";
  if (diff === 1) return "1 gün önce eklendi";
  return `${diff} gün önce eklendi`;
}

interface FormState {
  company: string;
  title: string;
  raw_text: string;
  company_about: string;
  extra_notes: string;
  cv_template: CvTemplateId;
}

function toForm(l: ListingDetail): FormState {
  const templateId = (l.cv_template ?? DEFAULT_CV_TEMPLATE) as CvTemplateId;
  return {
    company: l.company ?? "",
    title: l.title ?? "",
    raw_text: l.raw_text ?? "",
    company_about: l.company_about ?? "",
    extra_notes: l.extra_notes ?? "",
    cv_template: CV_TEMPLATES.some((t) => t.id === templateId)
      ? templateId
      : DEFAULT_CV_TEMPLATE,
  };
}

function ListingDetailContent() {
  const params = useParams();
  const router = useRouter();
  const listingId = params.listingId as string;
  const queryClient = useQueryClient();
  const logoInputRef = useRef<HTMLInputElement>(null);

  const [form, setForm] = useState<FormState | null>(null);
  const [companyLogo, setCompanyLogo] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [cvModalOpen, setCvModalOpen] = useState(false);

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
      queryClient.setQueryData<ListingDetail>(
        listingQueryKey(listingId),
        (current) =>
          current
            ? {
                ...current,
                score: result.score,
                score_breakdown: result.score_breakdown,
                matched_skills: result.matched_skills,
                missing_skills: result.missing_skills,
              }
            : current,
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
    mutationFn: (extraPrompt?: string) =>
      generateCv({ listing_id: listingId, extra_prompt: extraPrompt }),
    onSuccess: async (result) => {
      queryClient.setQueryData<ListingDetail>(
        listingQueryKey(listingId),
        (current) =>
          current
            ? {
                ...current,
                documents: [
                  ...current.documents.filter(
                    (document) => document.id !== result.document_id,
                  ),
                  {
                    id: result.document_id,
                    doc_type: "cv",
                    cv_url: result.cv_url,
                    cover_letter_text: null,
                  },
                ],
              }
            : current,
      );
      await invalidateListing();
    },
  });

  const coverLetterMutation = useMutation({
    mutationFn: (extraPrompt?: string) =>
      generateCoverLetter({ listing_id: listingId, extra_prompt: extraPrompt }),
    onSuccess: async (result) => {
      queryClient.setQueryData<ListingDetail>(
        listingQueryKey(listingId),
        (current) =>
          current
            ? {
                ...current,
                documents: [
                  ...current.documents.filter(
                    (document) => document.id !== result.document_id,
                  ),
                  {
                    id: result.document_id,
                    doc_type: "cover_letter",
                    cv_url: null,
                    cover_letter_text: result.cover_letter_text,
                  },
                ],
              }
            : current,
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

  const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result as string;
      setCompanyLogo(dataUrl);
      localStorage.setItem(`listing-logo:${listingId}`, dataUrl);
    };
    reader.readAsDataURL(file);
  };

  const listingDetailsUnsaved = Boolean(
    form && listing && form.raw_text !== (listing.raw_text ?? ""),
  );
  const companyAboutUnsaved = Boolean(
    form && listing && form.company_about !== (listing.company_about ?? ""),
  );

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

  const handleGenerateCv = (extraPrompt?: string) => {
    cvMutation.reset();
    cvMutation.mutate(extraPrompt);
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
    const clean = (v: string) => (v.trim() === "" ? null : v.trim());
    const payload: ListingUpdate = {
      company: clean(form.company),
      title: clean(form.title),
      raw_text: form.raw_text.trim(),
      company_about: clean(form.company_about),
      extra_notes: clean(form.extra_notes),
      cv_template: form.cv_template,
    };
    updateMutation.mutate(payload);
  };

  const matchError = matchMutation.isError
    ? getApiErrorMessage(
        matchMutation.error,
        "Uygunluk hesaplanamadı. Lütfen profilinizi kontrol edip tekrar deneyin.",
      )
    : undefined;
  const rematchError = rematchMutation.isError
    ? getApiErrorMessage(
        rematchMutation.error,
        "Eşleşme güncellenemedi. Lütfen tekrar deneyin.",
      )
    : undefined;
  const cvError = cvMutation.isError
    ? getApiErrorMessage(
        cvMutation.error,
        "CV oluşturulamadı. Lütfen tekrar deneyin.",
        {
          serviceUnavailable:
            "CV oluşturma servisi şu an kullanılamıyor. Lütfen daha sonra tekrar deneyin.",
        },
      )
    : undefined;
  const coverLetterError = coverLetterMutation.isError
    ? getApiErrorMessage(
        coverLetterMutation.error,
        "Önyazı oluşturulamadı. Lütfen tekrar deneyin.",
        {
          serviceUnavailable:
            "Önyazı servisi şu an kullanılamıyor. Lütfen daha sonra tekrar deneyin.",
        },
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
          compact
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
        <h1 className="text-headline-lg-mobile font-semibold mb-2">
          İlan bulunamadı
        </h1>
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
    listing.score == null
      ? null
      : Math.min(100, Math.max(0, Math.round(listing.score)));

  const selectedTemplate = getCvTemplate(form.cv_template);

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

      <section className="relative bg-surface-container-lowest rounded-xl p-4 md:p-6 border border-outline-variant shadow-card">
        <div
          className="pointer-events-none absolute inset-x-0 top-0 h-1 overflow-hidden rounded-t-xl bg-gradient-to-r from-primary via-primary-container to-primary/40"
          aria-hidden="true"
        />
        <div className="flex flex-col gap-4 pt-1 md:flex-row md:flex-nowrap md:items-center md:gap-lg">
          <div className="flex w-full items-center gap-3 md:contents">
            <button
              type="button"
              onClick={() => logoInputRef.current?.click()}
              className="relative shrink-0 group rounded-xl focus:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
              aria-label="Şirket logosunu güncelle"
            >
              <div
                className={cn(
                  "w-24 h-24 md:w-28 md:h-28 rounded-xl overflow-hidden border border-outline-variant flex items-center justify-center transition-colors",
                  companyLogo
                    ? "bg-surface"
                    : "bg-primary-container/15 group-hover:bg-primary-container/25"
                )}
              >
                {companyLogo ? (
                  <Image
                    src={companyLogo}
                    alt="Şirket logosu"
                    width={112}
                    height={112}
                    className="w-full h-full object-cover"
                    unoptimized
                  />
                ) : (
                  <Building2 className="w-9 h-9 text-primary/70 group-hover:text-primary transition-colors" />
                )}
              </div>
              <span className="absolute -bottom-1.5 -right-1.5 flex h-8 w-8 items-center justify-center rounded-full bg-primary-container text-on-primary shadow-card border border-primary-container/30 group-hover:opacity-90 transition-opacity">
                <ImagePlus className="w-3.5 h-3.5" />
              </span>
              <input
                ref={logoInputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={handleLogoChange}
              />
            </button>

            <div className="min-w-0 flex-1 md:hidden">
              <ListingEditActions
                onCancel={handleCancel}
                onSave={handleSave}
                isSaving={updateMutation.isPending}
                sticky={false}
                layout="stack"
                compact
                className="min-w-0"
              />
            </div>
          </div>

          <div className="w-full min-w-0 md:w-auto md:max-w-lg space-y-3">
            <div className="space-y-1">
              <label
                htmlFor="listing-company"
                className="text-label-md text-on-surface-variant"
              >
                Şirket Adı
              </label>
              <input
                id="listing-company"
                className="w-full min-w-0 bg-surface-container-low/60 border border-transparent rounded-lg px-3 py-2.5 text-headline-lg-mobile md:text-headline-lg font-semibold text-on-surface placeholder:text-on-surface-variant/50 focus:bg-surface-container-lowest focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                placeholder="Örn. Teknoloji A.Ş."
                value={form.company}
                onChange={(e) => update("company", e.target.value)}
              />
            </div>
            <div className="space-y-1">
              <label
                htmlFor="listing-title"
                className="text-label-md text-on-surface-variant"
              >
                Pozisyon
              </label>
              <input
                id="listing-title"
                className="w-full min-w-0 bg-surface-container-low/60 border border-transparent rounded-lg px-3 py-2 text-body-lg text-on-surface placeholder:text-on-surface-variant/50 focus:bg-surface-container-lowest focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                placeholder="Örn. Yazılım Mühendisliği Stajyeri"
                value={form.title}
                onChange={(e) => update("title", e.target.value)}
              />
            </div>
            <p className="text-label-md text-on-surface-variant">
              {daysAgo(listing.created_at)}
            </p>
          </div>

          <div className="hidden md:flex md:w-auto md:flex-1 items-center justify-center">
            <ListingEditActions
              onCancel={handleCancel}
              onSave={handleSave}
              isSaving={updateMutation.isPending}
              sticky={false}
              layout="stack"
            />
          </div>
        </div>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-[1fr_300px] gap-lg items-start">
        <div className="contents min-w-0 md:flex md:flex-col md:gap-lg md:col-start-1 md:row-start-1">
          <div className="order-1 md:order-none">
            <Card
              title="Şirket Hakkında"
              titleAddon={
                companyAboutUnsaved ? (
                  <span
                    className="shrink-0 text-[11px] font-medium leading-none text-error"
                    role="status"
                  >
                    Kaydedilmedi
                  </span>
                ) : undefined
              }
            >
              <textarea
                className="w-full h-32 bg-transparent border border-outline-variant rounded-lg p-4 text-body-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none resize-none"
                placeholder="Şirket kültürü, vizyonu ve çalışma ortamı hakkında bilgi..."
                value={form.company_about}
                onChange={(e) => update("company_about", e.target.value)}
              />
            </Card>
          </div>

          <div className="order-2 md:order-none">
            <Card
              title="İlan Detayları"
              titleAddon={
                listingDetailsUnsaved ? (
                  <span
                    className="shrink-0 text-[11px] font-medium leading-none text-error"
                    role="status"
                  >
                    Kaydedilmedi
                  </span>
                ) : undefined
              }
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
                İlan metnini değiştirdiyseniz önce kaydedin, sonra yeniden analiz
                edin.
              </p>
              <textarea
                className="w-full h-48 bg-transparent border border-outline-variant rounded-lg p-4 text-body-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none resize-none"
                placeholder="İş tanımı ve beklentileri..."
                value={form.raw_text}
                onChange={(e) => update("raw_text", e.target.value)}
              />
              {listing.required_skills.length > 0 && (
                <div className="mt-4">
                  <p className="text-label-md text-on-surface-variant mb-2">
                    ZORUNLU BECERİLER
                  </p>
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
                  <p className="text-label-md text-on-surface-variant mb-2">
                    TERCİH SEBEBİ
                  </p>
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
                        "İlan yeniden analiz edilemedi. Lütfen tekrar deneyin.",
                      )
                    : undefined
                }
              />
            </Card>
          </div>

          <div className="order-4 md:order-none">
            <CoverLetterResultSection
              documents={listing.documents}
              score={matchScore}
              loading={coverLetterMutation.isPending}
              error={coverLetterError}
              outdated={Boolean(listing.cover_letter_outdated)}
              onGenerate={handleGenerateCoverLetter}
            />
          </div>

          <div className="order-5 md:order-none">
            <CvResultSection
              documents={listing.documents}
              loading={cvMutation.isPending}
              error={cvError}
              outdated={Boolean(listing.cv_outdated)}
              onGenerate={handleGenerateCv}
            />
          </div>
        </div>

        <div className="contents min-w-0 md:flex md:flex-col md:gap-lg md:col-start-2 md:row-start-1">
          <div className="order-3 md:order-none">
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
              compact
              onCalculate={handleMatch}
              onRematch={handleRematch}
            />
          </div>

          <div className="order-6 md:order-none">
            <Card
              title="CV Tercihi"
              action={
                <SectionEditButton
                  label="Değiştir"
                  onClick={() => setCvModalOpen(true)}
                />
              }
            >
              <button
                type="button"
                onClick={() => setCvModalOpen(true)}
                className="w-full text-left space-y-2 group"
                aria-label={`${selectedTemplate.label} seçili. Değiştirmek için tıklayın.`}
              >
                <div className="relative w-full overflow-hidden rounded-lg border border-outline-variant bg-surface aspect-[3/4]">
                  <Image
                    src={selectedTemplate.src}
                    alt={selectedTemplate.label}
                    fill
                    className="object-contain object-top group-hover:opacity-95 transition-opacity"
                    sizes="300px"
                  />
                </div>
                <p className="text-label-md font-semibold text-on-surface">
                  {selectedTemplate.label}
                </p>
              </button>
            </Card>
          </div>

          <div className="order-7 md:order-none">
            <Card title="Ekstra Notlar">
              <textarea
                className="w-full h-24 bg-transparent border border-outline-variant rounded-lg p-3 text-body-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none resize-none"
                placeholder="Bu başvuruyla ilgili notlarınız..."
                value={form.extra_notes}
                onChange={(e) => update("extra_notes", e.target.value)}
              />
            </Card>
          </div>
        </div>
      </div>

      <div className="border-t border-outline-variant pt-lg">
        <ListingEditActions
          onCancel={handleCancel}
          onSave={handleSave}
          isSaving={updateMutation.isPending}
        />
      </div>

      <Modal
        open={cvModalOpen}
        onClose={() => setCvModalOpen(false)}
        title="CV Tercihi Seç"
        className="max-w-4xl"
      >
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 md:gap-4">
          {CV_TEMPLATES.map((template) => {
            const isSelected = template.id === form.cv_template;
            return (
              <button
                key={template.id}
                type="button"
                onClick={() => {
                  update("cv_template", template.id);
                  setCvModalOpen(false);
                }}
                className={cn(
                  "text-left rounded-lg border overflow-hidden transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-primary",
                  isSelected
                    ? "border-primary ring-2 ring-primary"
                    : "border-outline-variant hover:border-primary/60"
                )}
              >
                <div className="relative w-full aspect-[3/4] bg-surface">
                  <Image
                    src={template.src}
                    alt={template.label}
                    fill
                    className="object-contain object-top"
                    sizes="(max-width: 768px) 45vw, 360px"
                  />
                </div>
                <div className="px-3 py-2 border-t border-outline-variant">
                  <p
                    className={cn(
                      "text-label-md font-semibold",
                      isSelected ? "text-primary" : "text-on-surface"
                    )}
                  >
                    {template.label}
                  </p>
                </div>
              </button>
            );
          })}
        </div>
      </Modal>
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
