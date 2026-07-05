"use client";

import { AppHeader } from "@/components/layout/AppHeader";
import { AuthGuard } from "@/components/auth/AuthGuard";
import { ProfileEditModal } from "@/components/profile/ProfileEditModal";
import { Card } from "@/components/ui/Card";
import { SectionEditButton } from "@/components/ui/SectionEditButton";
import { Spinner } from "@/components/ui/Spinner";
import { useAuth } from "@/hooks/useAuth";
import type { ProfileEditSection } from "@/lib/validations/profile";
import type { UserResponse } from "@/types/user";
import {
  Award,
  Briefcase,
  Cake,
  Globe,
  Link2,
  Mail,
  MapPin,
  Pencil,
  Phone,
  Rocket,
  School,
  User,
} from "lucide-react";
import Image from "next/image";
import { useEffect, useRef, useState } from "react";

const PLACEHOLDER_ABOUT_DETAILS = [
  { label: "CİNSİYET", value: "Erkek" },
  { label: "UYRUK", value: "T.C." },
  { label: "SÜRÜCÜ BELGESİ", value: "B Sınıfı" },
  { label: "ASKERLİK DURUMU", value: "Tecilli" },
];

const PLACEHOLDER_EXPERIENCES = [
  {
    title: "Proje ve Teknik Ekip Üyesi",
    company: "Yapay Zeka ve Veri Bilimi Topluluğu",
    period: "Ekim 2023 - Devam Ediyor",
    description:
      "Topluluk bünyesinde oluşturulan proje ekibinde görev alarak kampüs içi nesne tanıma amaçlı bir görüntü işleme prototipinin geliştirilmesine katkı sağladım.",
  },
  {
    title: "Bilgisayarlı Görü Eğitim Programı Katılımcısı",
    company: "Vizyon Akademi",
    period: "Temmuz 2025 - Eylül 2025",
    description:
      "Sektör mentorlarının eşlik ettiği 8 haftalık yoğunlaştırılmış programda, gerçek zamanlı nesne tespiti yapan uçtan uca bir uygulama geliştirdim.",
  },
];

const PLACEHOLDER_PROJECTS = [
  {
    title: "Görme Engelliler için Gerçek Zamanlı Çevre Tanıma Asistanı",
    description:
      "Telefon kamerasından alınan görüntüyü OpenCV ile ön işleyip YOLOv8 tabanlı modelle gerçek zamanlı nesne tespiti yapıyor.",
    tags: ["Python", "OpenCV", "YOLOv8"],
  },
  {
    title: "Erken Evre Bitki Hastalığı Tespit Sistemi",
    description:
      "Yaprak fotoğraflarından yaygın hastalıkları yaklaşık %89 doğrulukla tespit eden bir model eğittim.",
    tags: ["Python", "TensorFlow", "FastAPI"],
  },
];

function ProfileContent() {
  const { user, loading, refreshUser } = useAuth();
  const [profile, setProfile] = useState<UserResponse | null>(null);
  const [editSection, setEditSection] = useState<ProfileEditSection | null>(null);
  const [comingSoonKey, setComingSoonKey] = useState<string>();
  const [successMessage, setSuccessMessage] = useState<string>();
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const displayProfile = profile || user;

  useEffect(() => {
    if (!displayProfile?.id) return;
    const saved = localStorage.getItem(`avatar:${displayProfile.id}`);
    setAvatarUrl(saved);
  }, [displayProfile?.id]);

  const openEdit = (section: ProfileEditSection, soonKey?: string) => {
    setComingSoonKey(soonKey);
    setEditSection(section);
  };

  const closeEdit = () => {
    setEditSection(null);
    setComingSoonKey(undefined);
  };

  const handleSaved = async (updated: UserResponse) => {
    setProfile(updated);
    setSuccessMessage("Değişiklikler kaydedildi.");
    await refreshUser();
    setTimeout(() => setSuccessMessage(undefined), 3000);
  };

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !displayProfile?.id) return;
    const reader = new FileReader();
    reader.onload = () => {
      const data = reader.result as string;
      localStorage.setItem(`avatar:${displayProfile.id}`, data);
      setAvatarUrl(data);
    };
    reader.readAsDataURL(file);
  };

  if (loading || !displayProfile) {
    return (
      <div className="py-3xl">
        <Spinner label="Profil yükleniyor..." />
      </div>
    );
  }

  return (
    <main className="max-w-[1024px] mx-auto px-margin-mobile md:px-lg py-lg md:py-xl space-y-lg md:space-y-xl">
      {successMessage && (
        <div className="rounded-lg border border-primary bg-primary-fixed/20 px-4 py-3 text-body-sm text-primary">
          {successMessage}
        </div>
      )}

      <section className="bg-surface-container-lowest rounded-xl p-4 md:p-6 border border-outline-variant">
        <div className="flex flex-col md:flex-row gap-md items-start">
          <div className="relative shrink-0">
            <div className="w-24 h-24 md:w-32 md:h-32 rounded-lg overflow-hidden border border-outline-variant bg-surface-container-low flex items-center justify-center">
              {avatarUrl ? (
                <Image
                  src={avatarUrl}
                  alt={displayProfile.full_name || "Profil"}
                  width={128}
                  height={128}
                  className="w-full h-full object-cover"
                  unoptimized
                />
              ) : (
                <User className="w-12 h-12 text-outline-variant" />
              )}
            </div>
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="absolute -bottom-2 -right-2 bg-surface-container-lowest rounded-full p-1 border border-outline-variant text-on-surface-variant hover:text-primary transition-colors"
              aria-label="Profil fotoğrafını düzenle"
            >
              <Pencil className="w-3.5 h-3.5" />
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleAvatarChange}
            />
          </div>

          <div className="flex-1 w-full">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-sm gap-4">
              <div>
                <h1 className="text-headline-lg-mobile md:text-headline-lg font-semibold text-on-surface mb-xs">
                  {displayProfile.full_name || "Profil"}
                </h1>
                <p className="text-body-lg text-on-surface-variant">
                  {displayProfile.target_position || "İş unvanı belirtilmedi"}
                </p>
              </div>
              <button
                type="button"
                onClick={() => openEdit("header")}
                className="border border-primary text-primary px-4 py-1 rounded font-label-md text-label-md hover:bg-primary hover:text-on-primary transition-colors shrink-0"
              >
                Düzenle
              </button>
            </div>

            <div className="flex flex-wrap items-center gap-x-sm gap-y-xs mt-md text-on-surface-variant text-body-sm">
              {displayProfile.birth_year && (
                <>
                  <div className="flex items-center gap-xs">
                    <Cake className="w-4 h-4" />
                    <span>{displayProfile.birth_year}</span>
                  </div>
                  <span className="text-outline-variant hidden md:inline">•</span>
                </>
              )}
              <div className="flex items-center gap-xs">
                <Mail className="w-4 h-4" />
                <span>{displayProfile.email}</span>
              </div>
              {displayProfile.location && (
                <>
                  <span className="text-outline-variant hidden md:inline">•</span>
                  <div className="flex items-center gap-xs">
                    <MapPin className="w-4 h-4" />
                    <span>{displayProfile.location}</span>
                  </div>
                </>
              )}
              {displayProfile.phone && (
                <>
                  <span className="text-outline-variant hidden md:inline">•</span>
                  <div className="flex items-center gap-xs">
                    <Phone className="w-4 h-4" />
                    <span>{displayProfile.phone}</span>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-[1fr_300px] gap-lg items-start">
        <div className="space-y-lg">
          <Card
            title="Özgeçmiş Özeti"
            action={<SectionEditButton onClick={() => openEdit("summary")} />}
          >
            <p className="text-body-lg text-on-surface-variant leading-relaxed">
              {displayProfile.experience_summary ||
                "Henüz bir özet eklenmedi. Düzenle butonuna tıklayarak özgeçmiş özetinizi ekleyebilirsiniz."}
            </p>
          </Card>

          <Card
            title="İş Deneyimlerim"
            action={<SectionEditButton onClick={() => openEdit("coming_soon", "experience")} />}
          >
            <div className="space-y-md">
              {PLACEHOLDER_EXPERIENCES.map((exp) => (
                <div
                  key={exp.title}
                  className="flex gap-md pb-md border-b border-outline-variant last:border-0"
                >
                  <div className="w-10 h-10 rounded border border-outline-variant bg-surface flex items-center justify-center shrink-0">
                    <Briefcase className="w-5 h-5 text-on-surface-variant" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-on-surface">{exp.title}</h3>
                    <p className="text-body-sm text-on-surface-variant">{exp.company}</p>
                    <span className="inline-block mt-xs text-label-md text-primary bg-primary-fixed/20 px-2 py-1 rounded">
                      {exp.period}
                    </span>
                    <p className="text-body-sm text-on-surface-variant mt-sm leading-relaxed">
                      {exp.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card
            title="Eğitim"
            action={<SectionEditButton onClick={() => openEdit("coming_soon", "education")} />}
          >
            <div className="flex gap-md">
              <div className="w-10 h-10 rounded-full border border-outline-variant bg-surface flex items-center justify-center shrink-0">
                <School className="w-5 h-5 text-on-surface-variant" />
              </div>
              <div>
                <h3 className="font-semibold text-on-surface">Bilgisayar Mühendisliği</h3>
                <p className="text-body-sm text-on-surface-variant">X Üniversitesi</p>
                <span className="inline-block mt-xs text-label-md text-primary bg-primary-fixed/20 px-2 py-1 rounded">
                  Eylül 2021 - Devam Ediyor
                </span>
              </div>
            </div>
          </Card>

          <Card
            title="Projelerim"
            action={<SectionEditButton onClick={() => openEdit("coming_soon", "projects")} />}
          >
            <div className="space-y-md">
              {PLACEHOLDER_PROJECTS.map((project) => (
                <div key={project.title} className="flex gap-md">
                  <div className="w-10 h-10 rounded border border-outline-variant bg-surface flex items-center justify-center shrink-0">
                    <Rocket className="w-5 h-5 text-on-surface-variant" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-on-surface">{project.title}</h3>
                    <p className="text-body-sm text-on-surface-variant mt-xs">{project.description}</p>
                    <div className="flex flex-wrap gap-xs mt-sm">
                      {project.tags.map((tag) => (
                        <span
                          key={tag}
                          className="bg-primary-fixed/20 text-primary px-2 py-0.5 rounded text-[10px] font-bold uppercase"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        <div className="space-y-lg md:block">
          <Card
            title="Hakkımda Detayları"
            action={<SectionEditButton onClick={() => openEdit("coming_soon", "about_details")} />}
          >
            <div className="space-y-md">
              {PLACEHOLDER_ABOUT_DETAILS.map((item) => (
                <div key={item.label}>
                  <p className="text-label-md text-on-surface-variant mb-xs">{item.label}</p>
                  <p className="text-body-sm text-on-surface">{item.value}</p>
                </div>
              ))}
            </div>
          </Card>

          <Card
            title="Yetenekler"
            action={<SectionEditButton onClick={() => openEdit("skills")} />}
          >
            <div className="flex flex-wrap gap-xs">
              {(displayProfile.skills || []).length > 0 ? (
                displayProfile.skills?.map((skill) => (
                  <span
                    key={skill}
                    className="bg-primary-fixed/20 text-primary px-2 py-1 rounded font-label-md text-label-md"
                  >
                    {skill}
                  </span>
                ))
              ) : (
                <p className="text-body-sm text-on-surface-variant">Henüz beceri eklenmedi.</p>
              )}
            </div>
          </Card>

          <Card
            title="Sertifikalar"
            action={<SectionEditButton onClick={() => openEdit("coming_soon", "certificates")} />}
          >
            <div className="flex gap-xs items-start">
              <Award className="w-4 h-4 text-primary mt-0.5 shrink-0" />
              <p className="text-body-sm text-on-surface-variant italic">Henüz eklenmedi</p>
            </div>
          </Card>

          <Card
            title="Sınavlar"
            action={<SectionEditButton onClick={() => openEdit("coming_soon", "exams")} />}
          >
            <p className="text-body-sm text-on-surface-variant italic">Henüz eklenmedi</p>
          </Card>

          <Card
            title="Yabancı Dil"
            action={<SectionEditButton onClick={() => openEdit("coming_soon", "languages")} />}
          >
            <div className="flex items-center gap-xs">
              <Globe className="w-4 h-4 text-primary" />
              <p className="text-body-sm text-on-surface-variant italic">Henüz eklenmedi</p>
            </div>
          </Card>

          <Card
            title="Sosyal Bağlantılar"
            action={<SectionEditButton onClick={() => openEdit("coming_soon", "social")} />}
          >
            <span className="flex items-center gap-xs text-body-sm text-on-surface-variant italic">
              <Link2 className="w-4 h-4" /> Henüz eklenmedi
            </span>
          </Card>

          <Card
            title="Referanslar"
            action={<SectionEditButton onClick={() => openEdit("coming_soon", "references")} />}
          >
            <p className="text-body-sm text-on-surface-variant italic">
              Talep edildiğinde sunulacaktır
            </p>
          </Card>
        </div>
      </div>

      <ProfileEditModal
        open={editSection !== null}
        section={editSection || "coming_soon"}
        comingSoonKey={comingSoonKey}
        profile={displayProfile}
        onClose={closeEdit}
        onSaved={handleSaved}
      />
    </main>
  );
}

export default function ProfilePage() {
  return (
    <div className="min-h-screen bg-surface-bright">
      <AppHeader />
      <AuthGuard>
        <ProfileContent />
      </AuthGuard>
    </div>
  );
}
