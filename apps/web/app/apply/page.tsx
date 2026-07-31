"use client";

import { AppLayout } from "@/components/layout/AppLayout";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { FormError } from "@/components/ui/FormError";
import { Modal } from "@/components/ui/Modal";
import { SectionEditButton } from "@/components/ui/SectionEditButton";
import { analyzeListing } from "@/lib/api/analysis";
import { patchProfile } from "@/lib/api/profiles";
import {
  CV_TEMPLATES,
  DEFAULT_CV_TEMPLATE,
  getCvTemplate,
  type CvTemplateId,
} from "@/lib/cv-templates";
import { cn } from "@/lib/utils";
import { analysisSchema, type AnalysisFormData } from "@/lib/validations/analysis";
import { zodResolver } from "@hookform/resolvers/zod";
import { Building2, ImagePlus } from "lucide-react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useRef, useState } from "react";
import { useForm } from "react-hook-form";

const TONE_OPTIONS = [
  { value: "professional", label: "Profesyonel" },
  { value: "casual", label: "Samimi" },
  { value: "confident", label: "Kendinden Emin" },
];

const DOCUMENT_LANGUAGE_OPTIONS = [
  { value: "tr" as const, label: "Türkçe" },
  { value: "en" as const, label: "English" },
];

function ApplyContent() {
  const router = useRouter();
  const [apiError, setApiError] = useState<string>();
  const [companyLogo, setCompanyLogo] = useState<string | null>(null);
  const [companyAbout, setCompanyAbout] = useState("");
  const [extraNotes, setExtraNotes] = useState("");
  const [tonePreference, setTonePreference] = useState(TONE_OPTIONS[0].value);
  const [documentLanguage, setDocumentLanguage] = useState<"tr" | "en">("tr");
  const [selectedCvTemplate, setSelectedCvTemplate] =
    useState<CvTemplateId>(DEFAULT_CV_TEMPLATE);
  const [cvModalOpen, setCvModalOpen] = useState(false);
  const logoInputRef = useRef<HTMLInputElement>(null);

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { isSubmitting },
  } = useForm<AnalysisFormData>({
    resolver: zodResolver(analysisSchema),
    defaultValues: {
      company_name: "",
      position_title: "",
      listing_text: "",
      listing_url: "",
    },
    mode: "onSubmit",
    reValidateMode: "onSubmit",
  });

  const companyName = watch("company_name") || "";
  const position = watch("position_title") || "";
  const listingText = watch("listing_text") || "";
  const selectedTemplate = getCvTemplate(selectedCvTemplate);

  const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => setCompanyLogo(reader.result as string);
    reader.readAsDataURL(file);
  };

  const onInvalid = () => {
    setApiError("Zorunlu alanları doldurunuz.");
  };

  const onSubmit = async (data: AnalysisFormData) => {
    setApiError(undefined);
    try {
      await patchProfile({ tone_preference: tonePreference });
      const clean = (v: string) => {
        const t = v.trim();
        return t && t !== "Seçiniz" ? t : undefined;
      };
      const result = await analyzeListing({
        listing_text: data.listing_text.trim() || undefined,
        listing_url: data.listing_url?.trim() || undefined,
        company_name: data.company_name.trim(),
        position_title: data.position_title.trim(),
        company_about: clean(companyAbout),
        extra_notes: clean(extraNotes),
        cv_template: selectedCvTemplate,
        document_language: documentLanguage,
      });
      if (companyLogo) {
        localStorage.setItem(`listing-logo:${result.listing_id}`, companyLogo);
      }
      router.push(`/listings/${result.listing_id}`);
    } catch (err: unknown) {
      const response = (err as { response?: { status?: number; data?: { detail?: string } } })
        ?.response;
      if (response?.status === 503) {
        setApiError("Analiz servisi şu an kullanılamıyor. Lütfen daha sonra tekrar deneyin.");
      } else {
        setApiError(
          typeof response?.data?.detail === "string"
            ? response.data.detail
            : "İlan oluşturulamadı. Lütfen ilan metnini kontrol edin."
        );
      }
    }
  };

  return (
    <main className="max-w-[1024px] mx-auto px-margin-mobile md:px-lg py-lg md:py-xl space-y-lg md:space-y-xl">
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
              aria-label="Şirket logosu ekle"
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

            <Button
              type="button"
              loading={isSubmitting}
              onClick={handleSubmit(onSubmit, onInvalid)}
              className="min-w-0 flex-1 px-4 py-3 text-base shadow-card hover:shadow-card-hover md:hidden"
            >
              İlanı Oluştur
            </Button>
          </div>

          <div className="w-full min-w-0 md:w-auto md:max-w-lg space-y-3">
            <div className="space-y-1">
              <label
                htmlFor="company-name"
                className="inline-flex flex-wrap items-baseline gap-x-1.5 gap-y-0.5 text-label-md text-on-surface-variant"
              >
                Şirket Adı
                <span className="text-[11px] font-medium leading-none text-error" role="status">
                  Zorunlu
                </span>
              </label>
              <input
                id="company-name"
                className="w-full min-w-0 bg-surface-container-low/60 border border-transparent rounded-lg px-3 py-2.5 text-headline-lg-mobile md:text-headline-lg font-semibold text-on-surface placeholder:text-on-surface-variant/50 focus:bg-surface-container-lowest focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                placeholder="Örn. Teknoloji A.Ş."
                value={companyName}
                onChange={(e) => {
                  setApiError(undefined);
                  setValue("company_name", e.target.value);
                }}
              />
            </div>
            <div className="space-y-1">
              <label
                htmlFor="position-title"
                className="inline-flex flex-wrap items-baseline gap-x-1.5 gap-y-0.5 text-label-md text-on-surface-variant"
              >
                Pozisyon
                <span className="text-[11px] font-medium leading-none text-error" role="status">
                  Zorunlu
                </span>
              </label>
              <input
                id="position-title"
                className="w-full min-w-0 bg-surface-container-low/60 border border-transparent rounded-lg px-3 py-2 text-body-lg text-on-surface placeholder:text-on-surface-variant/50 focus:bg-surface-container-lowest focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                placeholder="Örn. Yazılım Mühendisliği Stajyeri"
                value={position}
                onChange={(e) => {
                  setApiError(undefined);
                  setValue("position_title", e.target.value);
                }}
              />
            </div>
          </div>

          <div className="hidden md:flex md:w-auto md:flex-1 items-center justify-center">
            <Button
              type="button"
              loading={isSubmitting}
              onClick={handleSubmit(onSubmit, onInvalid)}
              className="shrink-0 px-10 py-4 text-xl shadow-card hover:shadow-card-hover"
            >
              İlanı Oluştur
            </Button>
          </div>
        </div>
      </section>

      <form onSubmit={handleSubmit(onSubmit, onInvalid)}>
        <div className="grid grid-cols-1 md:grid-cols-[1fr_300px] gap-lg items-start">
          <div className="space-y-lg">
            <FormError message={apiError} />

            <Card title="Şirket Hakkında">
              <textarea
                className="w-full h-40 bg-transparent border border-outline-variant rounded-lg p-4 text-body-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none resize-none"
                placeholder="Şirket kültürü, vizyonu ve çalışma ortamı hakkında bilgi veriniz..."
                value={companyAbout}
                onChange={(e) => setCompanyAbout(e.target.value)}
              />
            </Card>

            <Card
              title="İş İlanı Hakkında"
              titleAddon={
                <span
                  className="text-[11px] font-medium leading-snug text-error"
                  role="status"
                >
                  Zorunlu · 50 karakterden uzun olmalıdır
                </span>
              }
            >
              <textarea
                className="w-full h-48 bg-transparent border border-outline-variant rounded-lg p-4 text-body-lg focus:border-primary focus:ring-1 focus:ring-primary outline-none resize-none"
                placeholder="İş tanımı ve beklentileri buraya yazınız..."
                value={listingText}
                onChange={(e) => {
                  setApiError(undefined);
                  setValue("listing_text", e.target.value);
                }}
              />
              <input type="hidden" {...register("listing_url")} />
            </Card>

            <Card title="Ekstra Notlar">
              <textarea
                className="w-full h-24 bg-transparent border border-outline-variant rounded-lg p-3 text-body-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none resize-none"
                placeholder="Adaylara iletmek istediğiniz ek notlar..."
                value={extraNotes}
                onChange={(e) => setExtraNotes(e.target.value)}
              />
            </Card>
          </div>

          <div className="space-y-lg">
            <Card title="Belge Dili">
              <select
                id="document-language"
                aria-label="CV ve önyazı dili"
                className="input-field"
                value={documentLanguage}
                onChange={(e) =>
                  setDocumentLanguage(e.target.value === "en" ? "en" : "tr")
                }
              >
                {DOCUMENT_LANGUAGE_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
              <p className="mt-2 text-body-sm text-on-surface-variant">
                CV ve önyazı bu dilde üretilecek.
              </p>
            </Card>

            <Card title="Önyazı Tercihi">
              <select
                id="tone-preference"
                aria-label="Önyazı tonu"
                className="input-field"
                value={tonePreference}
                onChange={(e) => setTonePreference(e.target.value)}
              >
                {TONE_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </Card>

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

            <Button
              type="button"
              loading={isSubmitting}
              onClick={handleSubmit(onSubmit, onInvalid)}
              className="w-full px-6 py-3.5 text-base md:text-lg shadow-card hover:shadow-card-hover"
            >
              İlanı Oluştur
            </Button>
          </div>
        </div>
      </form>

      <Modal
        open={cvModalOpen}
        onClose={() => setCvModalOpen(false)}
        title="CV Tercihi Seç"
        className="max-w-4xl"
      >
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 md:gap-4">
          {CV_TEMPLATES.map((template) => {
            const isSelected = template.id === selectedCvTemplate;
            return (
              <button
                key={template.id}
                type="button"
                onClick={() => {
                  setSelectedCvTemplate(template.id);
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

export default function ApplyPage() {
  return (
    <AppLayout>
      <ApplyContent />
    </AppLayout>
  );
}
