"use client";

import { AppHeader } from "@/components/layout/AppHeader";
import { AuthGuard } from "@/components/auth/AuthGuard";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { FormError } from "@/components/ui/FormError";
import { SectionEditButton } from "@/components/ui/SectionEditButton";
import { analyzeListing, saveAnalysisResult } from "@/lib/api/analysis";
import { analysisSchema, type AnalysisFormData } from "@/lib/validations/analysis";
import { zodResolver } from "@hookform/resolvers/zod";
import { Building2, ImagePlus, PlusCircle, X } from "lucide-react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useRef, useState } from "react";
import { useForm } from "react-hook-form";

const CITIES = ["İl Seçiniz", "İstanbul", "Ankara", "İzmir", "Bursa", "Antalya"];
const DISTRICTS = ["İlçe Seçiniz", "Kadıköy", "Beşiktaş", "Çankaya", "Konak", "Nilüfer"];

function ApplyContent() {
  const router = useRouter();
  const [apiError, setApiError] = useState<string>();
  const [companyLogo, setCompanyLogo] = useState<string | null>(null);
  const [companyName, setCompanyName] = useState("");
  const [position, setPosition] = useState("");
  const [city, setCity] = useState(CITIES[0]);
  const [district, setDistrict] = useState(DISTRICTS[0]);
  const [companyAbout, setCompanyAbout] = useState("");
  const [extraNotes, setExtraNotes] = useState("");
  const [experienceLevel, setExperienceLevel] = useState("Seçiniz");
  const [educationLevel, setEducationLevel] = useState("Seçiniz");
  const [militaryStatus, setMilitaryStatus] = useState("Seçiniz");
  const [language, setLanguage] = useState("Seçiniz");
  const [driverLicense, setDriverLicense] = useState("Seçiniz");
  const [benefits, setBenefits] = useState<string[]>(["Yemek Kartı", "Özel Sağlık Sigortası"]);
  const [benefitInput, setBenefitInput] = useState("");
  const [sectionSaved, setSectionSaved] = useState<string | null>(null);
  const logoInputRef = useRef<HTMLInputElement>(null);

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<AnalysisFormData>({
    resolver: zodResolver(analysisSchema),
    defaultValues: { listing_text: "", listing_url: "" },
  });

  const listingText = watch("listing_text") || "";

  const showSaved = (key: string) => {
    setSectionSaved(key);
    setTimeout(() => setSectionSaved(null), 2000);
  };

  const addBenefit = () => {
    const trimmed = benefitInput.trim();
    if (!trimmed || benefits.includes(trimmed)) return;
    setBenefits([...benefits, trimmed]);
    setBenefitInput("");
  };

  const removeBenefit = (item: string) => {
    setBenefits(benefits.filter((b) => b !== item));
  };

  const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => setCompanyLogo(reader.result as string);
    reader.readAsDataURL(file);
  };

  const onSubmit = async (data: AnalysisFormData) => {
    setApiError(undefined);
    try {
      const result = await analyzeListing({
        listing_text: data.listing_text?.trim() || undefined,
        listing_url: data.listing_url?.trim() || undefined,
      });
      saveAnalysisResult(result);
      router.push(`/analyze/${result.listing_id}`);
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
      <section className="bg-surface-container-lowest rounded-xl p-4 md:p-6 border border-outline-variant">
        <div className="flex flex-col md:flex-row gap-md items-start">
          <div className="relative shrink-0">
            <div className="w-24 h-24 md:w-32 md:h-32 rounded-lg overflow-hidden border border-outline-variant bg-surface flex items-center justify-center">
              {companyLogo ? (
                <Image
                  src={companyLogo}
                  alt="Şirket logosu"
                  width={128}
                  height={128}
                  className="w-full h-full object-cover"
                  unoptimized
                />
              ) : (
                <Building2 className="w-10 h-10 text-outline-variant" />
              )}
            </div>
            <button
              type="button"
              onClick={() => logoInputRef.current?.click()}
              className="absolute -bottom-2 -right-2 bg-surface-container-lowest rounded-full p-1 border border-outline-variant text-on-surface-variant hover:text-primary transition-colors"
              aria-label="Şirket logosu ekle"
            >
              <ImagePlus className="w-3.5 h-3.5" />
            </button>
            <input
              ref={logoInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleLogoChange}
            />
          </div>

          <div className="flex-1 w-full">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-sm gap-4">
              <div className="w-full md:max-w-md space-y-2">
                <input
                  className="w-full bg-transparent border border-outline-variant rounded-lg px-3 py-2 text-headline-lg-mobile md:text-headline-lg font-semibold text-on-surface focus:border-primary focus:ring-1 focus:ring-primary outline-none"
                  placeholder="Şirket Adı"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                />
                <input
                  className="w-full bg-transparent border border-outline-variant rounded-lg px-3 py-2 text-body-lg text-on-surface-variant focus:border-primary focus:ring-1 focus:ring-primary outline-none"
                  placeholder="Pozisyon"
                  value={position}
                  onChange={(e) => setPosition(e.target.value)}
                />
              </div>
              <Button
                type="button"
                loading={isSubmitting}
                onClick={handleSubmit(onSubmit)}
                className="shrink-0"
              >
                İlanı Oluştur
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-sm mt-md">
              <select
                className="input-field py-1.5"
                value={city}
                onChange={(e) => setCity(e.target.value)}
              >
                {CITIES.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
              <select
                className="input-field py-1.5"
                value={district}
                onChange={(e) => setDistrict(e.target.value)}
              >
                {DISTRICTS.map((d) => (
                  <option key={d} value={d}>
                    {d}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </section>

      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="grid grid-cols-1 md:grid-cols-[1fr_300px] gap-lg items-start">
          <div className="space-y-lg">
            <FormError message={apiError} />

            <Card
              title="Şirket Hakkında"
              action={
                <SectionEditButton
                  label="Şirket Bilgisini Kaydet"
                  onClick={() => showSaved("company")}
                />
              }
            >
              {sectionSaved === "company" && (
                <p className="text-body-sm text-primary mb-2">Şirket bilgisi kaydedildi.</p>
              )}
              <textarea
                className="w-full h-40 bg-transparent border border-outline-variant rounded-lg p-4 text-body-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none resize-none"
                placeholder="Şirket kültürü, vizyonu ve çalışma ortamı hakkında bilgi veriniz..."
                value={companyAbout}
                onChange={(e) => setCompanyAbout(e.target.value)}
              />
            </Card>

            <Card
              title="İş İlanı Hakkında"
              action={
                <SectionEditButton
                  label="İlan Hakkında Metnini Kaydet"
                  onClick={() => showSaved("listing")}
                />
              }
            >
              {sectionSaved === "listing" && (
                <p className="text-body-sm text-primary mb-2">İlan metni kaydedildi.</p>
              )}
              <textarea
                className="w-full h-48 bg-transparent border border-outline-variant rounded-lg p-4 text-body-lg focus:border-primary focus:ring-1 focus:ring-primary outline-none resize-none"
                placeholder="İş tanımı ve beklentileri buraya yazınız..."
                value={listingText}
                onChange={(e) => setValue("listing_text", e.target.value, { shouldValidate: true })}
              />
              {errors.listing_text && (
                <p className="text-body-sm text-error mt-2">{errors.listing_text.message}</p>
              )}
              <input type="hidden" {...register("listing_url")} />
            </Card>

            <Card
              title="Ekstra Notlar"
              action={
                <SectionEditButton label="Notları Kaydet" onClick={() => showSaved("notes")} />
              }
            >
              {sectionSaved === "notes" && (
                <p className="text-body-sm text-primary mb-2">Notlar kaydedildi.</p>
              )}
              <textarea
                className="w-full h-24 bg-transparent border border-outline-variant rounded-lg p-3 text-body-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none resize-none"
                placeholder="Adaylara iletmek istediğiniz ek notlar..."
                value={extraNotes}
                onChange={(e) => setExtraNotes(e.target.value)}
              />
            </Card>
          </div>

          <div className="space-y-lg">
            <Card title="Aday Kriterleri">
              <div className="space-y-md">
                <div className="space-y-1">
                  <label className="text-label-md text-on-surface-variant">Deneyim Seviyesi</label>
                  <select
                    className="input-field"
                    value={experienceLevel}
                    onChange={(e) => setExperienceLevel(e.target.value)}
                  >
                    {["Seçiniz", "Junior", "Mid", "Senior"].map((o) => (
                      <option key={o}>{o}</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="text-label-md text-on-surface-variant">Eğitim Seviyesi</label>
                  <select
                    className="input-field"
                    value={educationLevel}
                    onChange={(e) => setEducationLevel(e.target.value)}
                  >
                    {["Seçiniz", "Lisans", "Yüksek Lisans", "Doktora"].map((o) => (
                      <option key={o}>{o}</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="text-label-md text-on-surface-variant">Askerlik Durumu</label>
                  <select
                    className="input-field"
                    value={militaryStatus}
                    onChange={(e) => setMilitaryStatus(e.target.value)}
                  >
                    {["Seçiniz", "Yapıldı", "Muaf", "Tecilli"].map((o) => (
                      <option key={o}>{o}</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="text-label-md text-on-surface-variant">Yabancı Dil</label>
                  <select
                    className="input-field"
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                  >
                    {["Seçiniz", "İngilizce", "Almanca", "Fransızca"].map((o) => (
                      <option key={o}>{o}</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="text-label-md text-on-surface-variant">Sürücü Belgesi</label>
                  <select
                    className="input-field"
                    value={driverLicense}
                    onChange={(e) => setDriverLicense(e.target.value)}
                  >
                    {["Seçiniz", "B Sınıfı", "A Sınıfı", "Yok"].map((o) => (
                      <option key={o}>{o}</option>
                    ))}
                  </select>
                </div>
              </div>
            </Card>

            <Card title="Yan Haklar">
              <div className="flex flex-wrap gap-sm mb-md">
                {benefits.map((benefit) => (
                  <span
                    key={benefit}
                    className="inline-flex items-center gap-1 bg-secondary-container text-on-secondary-container px-2 py-1 rounded-full text-label-md"
                  >
                    {benefit}
                    <button
                      type="button"
                      onClick={() => removeBenefit(benefit)}
                      className="hover:text-error transition-colors"
                      aria-label={`${benefit} kaldır`}
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </span>
                ))}
              </div>
              <div className="relative">
                <input
                  type="text"
                  className="input-field pr-10"
                  placeholder="Yan hak ekle..."
                  value={benefitInput}
                  onChange={(e) => setBenefitInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      addBenefit();
                    }
                  }}
                />
                <button
                  type="button"
                  onClick={addBenefit}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-primary"
                  aria-label="Yan hak ekle"
                >
                  <PlusCircle className="w-5 h-5" />
                </button>
              </div>
            </Card>

            <Button type="submit" loading={isSubmitting} className="w-full md:hidden">
              İlanı Oluştur
            </Button>
          </div>
        </div>
      </form>
    </main>
  );
}

export default function ApplyPage() {
  return (
    <div className="min-h-screen bg-surface-bright">
      <AppHeader />
      <AuthGuard>
        <ApplyContent />
      </AuthGuard>
    </div>
  );
}
