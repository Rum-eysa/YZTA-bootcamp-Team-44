"use client";

import { AppLayout } from "@/components/layout/AppLayout";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { FormError } from "@/components/ui/FormError";
import { Spinner } from "@/components/ui/Spinner";
import { TagInput } from "@/components/ui/TagInput";
import { generateCoverLetter } from "@/lib/api/coverLetter";
import { generateCv } from "@/lib/api/cvGeneration";
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
  Eye,
  FileText,
  MapPin,
  RefreshCw,
  Sparkles,
  Target,
} from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

const EXPERIENCE_OPTIONS = ["Seçiniz", "Junior", "Mid", "Senior"];
const EDUCATION_OPTIONS = ["Seçiniz", "Lise", "Lisans", "Yüksek Lisans", "Doktora"];
const MILITARY_OPTIONS = ["Seçiniz", "Yapıldı", "Muaf", "Tecilli"];

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

  const [listing, setListing] = useState<ListingDetail | null>(null);
  const [form, setForm] = useState<FormState | null>(null);
  const [companyLogo, setCompanyLogo] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string>();
  const [saved, setSaved] = useState(false);

  const [matchLoading, setMatchLoading] = useState(false);
  const [matchError, setMatchError] = useState<string>();
  const [reanalyzeLoading, setReanalyzeLoading] = useState(false);
  const [reanalyzeError, setReanalyzeError] = useState<string>();
  const [rematchLoading, setRematchLoading] = useState(false);
  const [rematchError, setRematchError] = useState<string>();
  const [cvLoading, setCvLoading] = useState(false);
  const [cvError, setCvError] = useState<string>();
  const [coverLetterLoading, setCoverLetterLoading] = useState(false);
  const [coverLetterError, setCoverLetterError] = useState<string>();
  const [copiedDocId, setCopiedDocId] = useState<string>();

  useEffect(() => {
    setCompanyLogo(localStorage.getItem(`listing-logo:${listingId}`));
  }, [listingId]);

  useEffect(() => {
    getListing(listingId)
      .then((data) => {
        setListing(data);
        setForm(toForm(data));
      })
      .catch(() => setError("İlan yüklenemedi veya erişim yetkiniz yok."))
      .finally(() => setLoading(false));
  }, [listingId]);

  const update = <K extends keyof FormState>(key: K, value: FormState[K]) => {
    setForm((prev) => (prev ? { ...prev, [key]: value } : prev));
    setSaved(false);
  };

  const refreshListing = async () => {
    const data = await getListing(listingId);
    setListing(data);
  };

  const handleCopyCoverLetter = async (docId: string, text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedDocId(docId);
      setTimeout(() => setCopiedDocId(undefined), 2000);
    } catch {
      setCoverLetterError("Önyazı panoya kopyalanamadı.");
    }
  };

  const handleMatch = async () => {
    setMatchError(undefined);
    setMatchLoading(true);
    try {
      await matchListing({ listing_id: listingId });
      await refreshListing();
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
  };

  const handleReanalyze = async () => {
    setReanalyzeError(undefined);
    setReanalyzeLoading(true);
    try {
      const updated = await reanalyzeListing(listingId);
      setListing(updated);
      setForm(toForm(updated));
    } catch (err: unknown) {
      setReanalyzeError(
        getApiErrorMessage(err, "İlan yeniden analiz edilemedi. Lütfen tekrar deneyin.")
      );
    } finally {
      setReanalyzeLoading(false);
    }
  };

  const handleRematch = async () => {
    setRematchError(undefined);
    setRematchLoading(true);
    try {
      const updated = await rematchListing(listingId);
      setListing(updated);
    } catch (err: unknown) {
      setRematchError(
        getApiErrorMessage(err, "Eşleşme güncellenemedi. Lütfen tekrar deneyin.")
      );
    } finally {
      setRematchLoading(false);
    }
  };

  const handleGenerateCv = async () => {
    setCvError(undefined);
    setCvLoading(true);
    try {
      await generateCv({ listing_id: listingId });
      await refreshListing();
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
  };

  const handleGenerateCoverLetter = async () => {
    setCoverLetterError(undefined);
    setCoverLetterLoading(true);
    try {
      await generateCoverLetter({ listing_id: listingId });
      await refreshListing();
    } catch (err: unknown) {
      setCoverLetterError(
        getApiErrorMessage(err, "Önyazı oluşturulamadı. Lütfen tekrar deneyin.", {
          serviceUnavailable:
            "Önyazı servisi şu an kullanılamıyor. Lütfen daha sonra tekrar deneyin.",
        })
      );
    } finally {
      setCoverLetterLoading(false);
    }
  };

  const handleSave = async () => {
    if (!form) return;
    setSaving(true);
    setError(undefined);
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
    try {
      const updated = await updateListing(listingId, payload);
      setListing(updated);
      setForm(toForm(updated));
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch {
      setError("Değişiklikler kaydedilemedi. Lütfen tekrar deneyin.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="py-3xl">
        <Spinner label="İlan yükleniyor..." />
      </div>
    );
  }

  if (!listing || !form) {
    return (
      <main className="max-w-[1024px] mx-auto px-margin-mobile md:px-lg py-xl text-center">
        <h1 className="text-headline-lg-mobile font-semibold mb-2">İlan bulunamadı</h1>
        <p className="text-body-sm text-on-surface-variant mb-6">
          {error || "Bu ilana erişilemiyor."}
        </p>
        <Link href="/listings">
          <Button>İlanlarıma Dön</Button>
        </Link>
      </main>
    );
  }

  const matchScore =
    listing.score == null ? null : Math.min(100, Math.max(0, Math.round(listing.score)));
  const hasCv = listing.documents.some((document) => document.doc_type === "cv");
  const hasCoverLetter = listing.documents.some(
    (document) => document.doc_type === "cover_letter"
  );

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
      <div className="flex items-center justify-between gap-md">
        <Link
          href="/listings"
          className="flex items-center gap-1 text-body-sm text-on-surface-variant hover:text-primary transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          İlanlarım&apos;a Dön
        </Link>
        <div className="flex items-center gap-sm">
          <Button variant="outline" onClick={() => router.push("/listings")}>
            İptal
          </Button>
          <Button onClick={handleSave} loading={saving}>
            Değişiklikleri Kaydet
          </Button>
        </div>
      </div>

      {saved && (
        <div className="rounded-lg border border-primary bg-primary-fixed/20 px-4 py-3 text-body-sm text-primary">
          Değişiklikler kaydedildi.
        </div>
      )}
      {error && (
        <div className="rounded-lg border border-error bg-error-container/30 px-4 py-3 text-body-sm text-error">
          {error}
        </div>
      )}

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

          <div className="flex items-stretch gap-md shrink-0 w-full md:w-auto">
            <div className="flex-1 md:w-44 space-y-1">
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
            <div className="flex flex-col items-center justify-center text-center bg-primary-fixed/20 rounded-xl px-5 py-2 min-w-[104px]">
              <p className="text-[32px] leading-none font-bold text-primary">
                {matchScore != null ? `%${matchScore}` : "—"}
              </p>
              <p className="text-label-md text-on-surface-variant mt-1">Eşleşme Skoru</p>
            </div>
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

          <Card title="İlan Detayları">
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
            <div className="mt-4 flex items-center gap-3">
              <Button
                variant="outline"
                onClick={handleReanalyze}
                loading={reanalyzeLoading}
              >
                <RefreshCw className="w-4 h-4" />
                Yeniden Analiz Et
              </Button>
              <p className="text-label-md text-on-surface-variant">
                İlan metnini değiştirdiyseniz önce kaydedin, sonra yeniden analiz edin.
              </p>
            </div>
            <FormError message={reanalyzeError} />
          </Card>

          {matchScore != null && (
            <Card title="Uygunluk Sonucu" className="shadow-card-hover">
              <div className="grid grid-cols-1 items-center gap-lg lg:grid-cols-[180px_1fr]">
                <div className="flex justify-center">
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
                      <span className="text-headline-lg font-semibold text-primary">
                        %{matchScore}
                      </span>
                      <span className="text-label-md text-on-surface-variant">Eşleşme</span>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-md sm:grid-cols-2">
                  <div className="rounded-xl bg-primary-fixed/10 p-4">
                    <h3 className="mb-3 text-label-md font-semibold text-on-surface">
                      Eşleşen Beceriler
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {listing.matched_skills.length > 0 ? (
                        listing.matched_skills.map((skill) => (
                          <span
                            key={skill}
                            className="rounded bg-primary-fixed/20 px-2 py-1 text-label-md text-primary"
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
                    <h3 className="mb-3 text-label-md font-semibold text-on-surface">
                      Eksik Beceriler
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {listing.missing_skills.length > 0 ? (
                        listing.missing_skills.map((skill) => (
                          <span
                            key={skill}
                            className="rounded bg-error-container px-2 py-1 text-label-md text-on-error-container"
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
        </div>

        <div className="space-y-lg min-w-0">
          <Card
            title="AI Araçları"
            className="bg-gradient-to-br from-surface-container-lowest to-primary-fixed/10 shadow-card"
          >
            <p className="text-body-sm text-on-surface-variant mb-4">
              Profilinize göre uygunluğu hesaplayın, ilana özel CV ve önyazı oluşturun.
            </p>
            <div className="space-y-md">
              <div className="space-y-3 rounded-xl border border-outline-variant bg-surface-container-lowest p-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="flex items-center gap-2 text-label-md font-semibold">
                    <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-fixed/20 text-primary">
                      <Target className="h-4 w-4" />
                    </span>
                    Uygunluk
                  </span>
                  {matchScore != null && (
                    <span className="rounded-full bg-primary-fixed/20 px-2 py-1 text-label-md text-primary">
                      %{matchScore}
                    </span>
                  )}
                </div>
                <Button
                  onClick={handleMatch}
                  loading={matchLoading}
                  className="w-full"
                >
                  <Target className="w-4 h-4" />
                  Uygunluğumu Hesapla
                </Button>
                <FormError message={matchError} />
                {matchScore != null && (
                  <>
                    <Button
                      variant="outline"
                      onClick={handleRematch}
                      loading={rematchLoading}
                      className="w-full"
                    >
                      <RefreshCw className="w-4 h-4" />
                      Eşleşmeyi Güncelle
                    </Button>
                    <FormError message={rematchError} />
                  </>
                )}
              </div>
              <div className="space-y-3 rounded-xl border border-outline-variant bg-surface-container-lowest p-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="flex items-center gap-2 text-label-md font-semibold">
                    <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-fixed/20 text-primary">
                      <FileText className="h-4 w-4" />
                    </span>
                    CV
                  </span>
                  {hasCv && (
                    <span className="rounded-full bg-secondary-container px-2 py-1 text-label-md text-on-secondary-container">
                      Hazır
                    </span>
                  )}
                </div>
                <Button
                  onClick={handleGenerateCv}
                  loading={cvLoading}
                  variant="secondary"
                  className="w-full"
                >
                  <FileText className="w-4 h-4" />
                  CV Oluştur
                </Button>
                <FormError message={cvError} />
              </div>
              <div className="space-y-3 rounded-xl border border-outline-variant bg-surface-container-lowest p-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="flex items-center gap-2 text-label-md font-semibold">
                    <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-fixed/20 text-primary">
                      <Sparkles className="h-4 w-4" />
                    </span>
                    Önyazı
                  </span>
                  {hasCoverLetter && (
                    <span className="rounded-full bg-secondary-container px-2 py-1 text-label-md text-on-secondary-container">
                      Hazır
                    </span>
                  )}
                </div>
                <Button
                  onClick={handleGenerateCoverLetter}
                  loading={coverLetterLoading}
                  variant="secondary"
                  className="w-full"
                >
                  <Sparkles className="w-4 h-4" />
                  Önyazı Oluştur
                </Button>
                <FormError message={coverLetterError} />
              </div>
            </div>
          </Card>

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

          <Card title="Dokümanlar" className="border-primary/20 shadow-card">
            {listing.documents.length === 0 ? (
              <p className="text-body-sm text-on-surface-variant italic">Henüz doküman yok</p>
            ) : (
              <div className="space-y-sm">
                {listing.documents.map((doc) => {
                  const name =
                    doc.doc_type === "cv" ? "Güncel CV.pdf" : "Önyazı Taslağı";
                  return (
                    <div
                      key={doc.id}
                      className="space-y-2 rounded-xl border border-outline-variant bg-gradient-to-br from-surface-container-low to-primary-fixed/10 px-3 py-3"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="flex items-center gap-2 min-w-0">
                          <FileText className="w-4 h-4 text-primary shrink-0" />
                          <span className="text-body-sm text-on-surface break-all">{name}</span>
                        </span>
                        {doc.cv_url && (
                          <a
                            href={doc.cv_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-on-surface-variant hover:text-primary transition-colors shrink-0"
                            aria-label="Dokümanı görüntüle"
                          >
                            <Eye className="w-4 h-4" />
                          </a>
                        )}
                        {doc.cover_letter_text && (
                          <button
                            type="button"
                            onClick={() =>
                              handleCopyCoverLetter(doc.id, doc.cover_letter_text as string)
                            }
                            className="text-label-md text-on-surface-variant hover:text-primary transition-colors shrink-0"
                          >
                            {copiedDocId === doc.id ? "Kopyalandı" : "Kopyala"}
                          </button>
                        )}
                      </div>
                      {doc.cover_letter_text && (
                        <p className="text-body-sm text-on-surface-variant whitespace-pre-wrap max-h-40 overflow-y-auto">
                          {doc.cover_letter_text}
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </Card>
        </div>
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
