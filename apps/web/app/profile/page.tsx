"use client";

import { AppLayout } from "@/components/layout/AppLayout";
import { AboutDetailsModal } from "@/components/profile/AboutDetailsModal";
import { CertificateModal } from "@/components/profile/CertificateModal";
import { EducationModal } from "@/components/profile/EducationModal";
import { ExamModal } from "@/components/profile/ExamModal";
import { ExperienceModal } from "@/components/profile/ExperienceModal";
import { LanguageModal } from "@/components/profile/LanguageModal";
import { ProfileEditModal } from "@/components/profile/ProfileEditModal";
import { ProjectModal } from "@/components/profile/ProjectModal";
import { ReferenceModal } from "@/components/profile/ReferenceModal";
import { SocialLinkModal } from "@/components/profile/SocialLinkModal";
import { Card } from "@/components/ui/Card";
import { MarkdownView } from "@/components/ui/MarkdownView";
import { SectionEditButton } from "@/components/ui/SectionEditButton";
import { Spinner } from "@/components/ui/Spinner";
import { useAuth } from "@/hooks/useAuth";
import { deleteCertificate, listCertificates } from "@/lib/api/certificates";
import { deleteEducation, listEducation } from "@/lib/api/education";
import { deleteExam, listExams } from "@/lib/api/exams";
import { deleteExperience, listExperiences } from "@/lib/api/experiences";
import { deleteLanguage, listLanguages } from "@/lib/api/languages";
import { deleteProject, listProjects } from "@/lib/api/projects";
import { deleteReference, listReferences } from "@/lib/api/references";
import { deleteSocialLink, listSocialLinks } from "@/lib/api/socialLinks";
import type { ProfileEditSection } from "@/lib/validations/profile";
import type { Certificate } from "@/types/certificate";
import type { EducationRecord } from "@/types/education";
import type { Exam } from "@/types/exam";
import type { WorkExperience } from "@/types/experience";
import type { Language } from "@/types/language";
import type { Project } from "@/types/project";
import type { Reference } from "@/types/reference";
import type { SocialLink } from "@/types/socialLink";
import type { UserResponse } from "@/types/user";
import {
  Award,
  Briefcase,
  Cake,
  ClipboardList,
  Globe,
  Link2,
  Mail,
  MapPin,
  Pencil,
  Phone,
  Plus,
  Rocket,
  School,
  Trash2,
  User,
} from "lucide-react";
import Image from "next/image";
import { useCallback, useEffect, useRef, useState } from "react";

const SENIORITY_LABELS: Record<string, string> = {
  junior: "Junior",
  mid: "Mid",
  senior: "Senior",
};

function formatMonthYear(value: string | null): string | null {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString("tr-TR", { month: "long", year: "numeric" });
}

function formatPeriod(start: string | null, end: string | null): string {
  const startLabel = formatMonthYear(start);
  const endLabel = formatMonthYear(end) || "Devam Ediyor";
  if (!startLabel) return endLabel;
  return `${startLabel} - ${endLabel}`;
}

function ProfileContent() {
  const { user, loading, refreshUser } = useAuth();
  const [profile, setProfile] = useState<UserResponse | null>(null);
  const [editSection, setEditSection] = useState<ProfileEditSection | null>(null);
  const [comingSoonKey, setComingSoonKey] = useState<string>();
  const [successMessage, setSuccessMessage] = useState<string>();
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [experiences, setExperiences] = useState<WorkExperience[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [education, setEducation] = useState<EducationRecord[]>([]);
  const [certificates, setCertificates] = useState<Certificate[]>([]);
  const [exams, setExams] = useState<Exam[]>([]);
  const [languages, setLanguages] = useState<Language[]>([]);
  const [socialLinks, setSocialLinks] = useState<SocialLink[]>([]);
  const [references, setReferences] = useState<Reference[]>([]);
  const [experienceModalOpen, setExperienceModalOpen] = useState(false);
  const [editingExperience, setEditingExperience] = useState<WorkExperience | null>(null);
  const [projectModalOpen, setProjectModalOpen] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [educationModalOpen, setEducationModalOpen] = useState(false);
  const [editingEducation, setEditingEducation] = useState<EducationRecord | null>(null);
  const [aboutDetailsModalOpen, setAboutDetailsModalOpen] = useState(false);
  const [certificateModalOpen, setCertificateModalOpen] = useState(false);
  const [editingCertificate, setEditingCertificate] = useState<Certificate | null>(null);
  const [examModalOpen, setExamModalOpen] = useState(false);
  const [editingExam, setEditingExam] = useState<Exam | null>(null);
  const [languageModalOpen, setLanguageModalOpen] = useState(false);
  const [editingLanguage, setEditingLanguage] = useState<Language | null>(null);
  const [socialLinkModalOpen, setSocialLinkModalOpen] = useState(false);
  const [editingSocialLink, setEditingSocialLink] = useState<SocialLink | null>(null);
  const [referenceModalOpen, setReferenceModalOpen] = useState(false);
  const [editingReference, setEditingReference] = useState<Reference | null>(null);

  const displayProfile = profile || user;

  useEffect(() => {
    if (!displayProfile?.id) return;
    const saved = localStorage.getItem(`avatar:${displayProfile.id}`);
    setAvatarUrl(saved);
  }, [displayProfile?.id]);

  const loadExperiences = useCallback(async () => {
    try {
      setExperiences(await listExperiences());
    } catch {
      setExperiences([]);
    }
  }, []);

  const loadProjects = useCallback(async () => {
    try {
      setProjects(await listProjects());
    } catch {
      setProjects([]);
    }
  }, []);

  const loadEducation = useCallback(async () => {
    try {
      setEducation(await listEducation());
    } catch {
      setEducation([]);
    }
  }, []);

  const loadCertificates = useCallback(async () => {
    try {
      setCertificates(await listCertificates());
    } catch {
      setCertificates([]);
    }
  }, []);

  const loadExams = useCallback(async () => {
    try {
      setExams(await listExams());
    } catch {
      setExams([]);
    }
  }, []);

  const loadLanguages = useCallback(async () => {
    try {
      setLanguages(await listLanguages());
    } catch {
      setLanguages([]);
    }
  }, []);

  const loadSocialLinks = useCallback(async () => {
    try {
      setSocialLinks(await listSocialLinks());
    } catch {
      setSocialLinks([]);
    }
  }, []);

  const loadReferences = useCallback(async () => {
    try {
      setReferences(await listReferences());
    } catch {
      setReferences([]);
    }
  }, []);

  useEffect(() => {
    if (!displayProfile?.id) return;
    loadExperiences();
    loadProjects();
    loadEducation();
    loadCertificates();
    loadExams();
    loadLanguages();
    loadSocialLinks();
    loadReferences();
  }, [
    displayProfile?.id,
    loadExperiences,
    loadProjects,
    loadEducation,
    loadCertificates,
    loadExams,
    loadLanguages,
    loadSocialLinks,
    loadReferences,
  ]);

  const openExperienceModal = (experience: WorkExperience | null) => {
    setEditingExperience(experience);
    setExperienceModalOpen(true);
  };

  const openProjectModal = (project: Project | null) => {
    setEditingProject(project);
    setProjectModalOpen(true);
  };

  const openEducationModal = (record: EducationRecord | null) => {
    setEditingEducation(record);
    setEducationModalOpen(true);
  };

  const openCertificateModal = (c: Certificate | null) => {
    setEditingCertificate(c);
    setCertificateModalOpen(true);
  };

  const openExamModal = (e: Exam | null) => {
    setEditingExam(e);
    setExamModalOpen(true);
  };

  const openLanguageModal = (l: Language | null) => {
    setEditingLanguage(l);
    setLanguageModalOpen(true);
  };

  const openSocialLinkModal = (s: SocialLink | null) => {
    setEditingSocialLink(s);
    setSocialLinkModalOpen(true);
  };

  const openReferenceModal = (r: Reference | null) => {
    setEditingReference(r);
    setReferenceModalOpen(true);
  };

  const handleDeleteExperience = async (id: string) => {
    if (!window.confirm("Bu iş deneyimini silmek istediğinize emin misiniz?")) return;
    await deleteExperience(id);
    await loadExperiences();
  };

  const handleDeleteProject = async (id: string) => {
    if (!window.confirm("Bu projeyi silmek istediğinize emin misiniz?")) return;
    await deleteProject(id);
    await loadProjects();
  };

  const handleDeleteEducation = async (id: string) => {
    if (!window.confirm("Bu eğitim kaydını silmek istediğinize emin misiniz?")) return;
    await deleteEducation(id);
    await loadEducation();
  };

  const handleDeleteCertificate = async (id: string) => {
    if (!window.confirm("Bu sertifikayı silmek istediğinize emin misiniz?")) return;
    await deleteCertificate(id);
    await loadCertificates();
  };

  const handleDeleteExam = async (id: string) => {
    if (!window.confirm("Bu sınavı silmek istediğinize emin misiniz?")) return;
    await deleteExam(id);
    await loadExams();
  };

  const handleDeleteLanguage = async (id: string) => {
    if (!window.confirm("Bu dili silmek istediğinize emin misiniz?")) return;
    await deleteLanguage(id);
    await loadLanguages();
  };

  const handleDeleteSocialLink = async (id: string) => {
    if (!window.confirm("Bu bağlantıyı silmek istediğinize emin misiniz?")) return;
    await deleteSocialLink(id);
    await loadSocialLinks();
  };

  const handleDeleteReference = async (id: string) => {
    if (!window.confirm("Bu referansı silmek istediğinize emin misiniz?")) return;
    await deleteReference(id);
    await loadReferences();
  };

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

          <div className="flex-1 w-full min-w-0">
            <div className="flex flex-row justify-between items-start md:items-center mb-sm gap-4">
              <div className="min-w-0 flex-1">
                <h1 className="text-headline-lg-mobile md:text-headline-lg font-semibold text-on-surface mb-xs break-words">
                  {displayProfile.full_name || "Profil"}
                </h1>
                <p className="text-body-lg text-on-surface-variant break-words">
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
              <div className="flex items-center gap-xs min-w-0 max-w-full">
                <Mail className="w-4 h-4 shrink-0" />
                <span className="break-all">{displayProfile.email}</span>
              </div>
              {displayProfile.location && (
                <>
                  <span className="text-outline-variant hidden md:inline">•</span>
                  <div className="flex items-center gap-xs min-w-0 max-w-full">
                    <MapPin className="w-4 h-4 shrink-0" />
                    <span className="break-words">{displayProfile.location}</span>
                  </div>
                </>
              )}
              {displayProfile.phone && (
                <>
                  <span className="text-outline-variant hidden md:inline">•</span>
                  <div className="flex items-center gap-xs min-w-0 max-w-full">
                    <Phone className="w-4 h-4 shrink-0" />
                    <span className="break-all">{displayProfile.phone}</span>
                  </div>
                </>
              )}
              {displayProfile.seniority && (
                <>
                  <span className="text-outline-variant hidden md:inline">•</span>
                  <div className="flex items-center gap-xs">
                    <Award className="w-4 h-4" />
                    <span>{SENIORITY_LABELS[displayProfile.seniority] || displayProfile.seniority}</span>
                  </div>
                </>
              )}
              {displayProfile.experience_years != null && (
                <>
                  <span className="text-outline-variant hidden md:inline">•</span>
                  <div className="flex items-center gap-xs">
                    <Briefcase className="w-4 h-4" />
                    <span>{displayProfile.experience_years} yıl deneyim</span>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-[1fr_300px] gap-lg items-start">
        <div className="space-y-lg min-w-0">
          <Card
            title="Özgeçmiş Özeti"
            action={<SectionEditButton onClick={() => openEdit("summary")} />}
          >
            {displayProfile.experience_summary ? (
              <MarkdownView
                source={displayProfile.experience_summary}
                className="text-body-lg text-on-surface-variant leading-relaxed break-words"
              />
            ) : (
              <p className="text-body-lg text-on-surface-variant leading-relaxed">
                Henüz bir özet eklenmedi. Düzenle butonuna tıklayarak özgeçmiş özetinizi
                ekleyebilirsiniz.
              </p>
            )}
          </Card>

          <Card
            title="İş Deneyimlerim"
            action={
              <button
                type="button"
                onClick={() => openExperienceModal(null)}
                className="flex items-center gap-1 text-primary text-label-md hover:underline"
              >
                <Plus className="w-4 h-4" /> Ekle
              </button>
            }
          >
            <div className="space-y-md">
              {experiences.length === 0 ? (
                <p className="text-body-sm text-on-surface-variant">
                  Henüz iş deneyimi eklenmedi. &quot;Ekle&quot; butonuna tıklayarak
                  ekleyebilirsiniz.
                </p>
              ) : (
                experiences.map((exp) => (
                  <div
                    key={exp.id}
                    className="flex gap-md pb-md border-b border-outline-variant last:border-0"
                  >
                    <div className="w-10 h-10 rounded border border-outline-variant bg-surface flex items-center justify-center shrink-0">
                      <Briefcase className="w-5 h-5 text-on-surface-variant" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <div className="min-w-0">
                          <h3 className="font-semibold text-on-surface break-words">{exp.title}</h3>
                          <p className="text-body-sm text-on-surface-variant break-words">{exp.company}</p>
                        </div>
                        <div className="flex gap-1 shrink-0">
                          <button
                            type="button"
                            onClick={() => openExperienceModal(exp)}
                            className="p-1 text-on-surface-variant hover:text-primary transition-colors"
                            aria-label="Düzenle"
                          >
                            <Pencil className="w-4 h-4" />
                          </button>
                          <button
                            type="button"
                            onClick={() => handleDeleteExperience(exp.id)}
                            className="p-1 text-on-surface-variant hover:text-error transition-colors"
                            aria-label="Sil"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                      <span className="inline-block mt-xs text-label-md text-primary bg-primary-fixed/20 px-2 py-1 rounded">
                        {formatPeriod(exp.start_date, exp.end_date)}
                      </span>
                      {exp.description && (
                        <MarkdownView
                          source={exp.description}
                          className="text-body-sm text-on-surface-variant mt-sm leading-relaxed break-words"
                        />
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </Card>

          <Card
            title="Eğitim"
            action={
              <button
                type="button"
                onClick={() => openEducationModal(null)}
                className="flex items-center gap-1 text-primary text-label-md hover:underline"
              >
                <Plus className="w-4 h-4" /> Ekle
              </button>
            }
          >
            <div className="space-y-md">
              {education.length === 0 ? (
                <p className="text-body-sm text-on-surface-variant">
                  Henüz eğitim bilgisi eklenmedi. &quot;Ekle&quot; butonuna tıklayarak ekleyebilirsiniz.
                </p>
              ) : (
                education.map((ed) => (
                  <div
                    key={ed.id}
                    className="flex gap-md pb-md border-b border-outline-variant last:border-0"
                  >
                    <div className="w-10 h-10 rounded-full border border-outline-variant bg-surface flex items-center justify-center shrink-0">
                      <School className="w-5 h-5 text-on-surface-variant" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <div className="min-w-0">
                          <h3 className="font-semibold text-on-surface break-words">
                            {ed.field_of_study || ed.degree || "Eğitim"}
                          </h3>
                          <p className="text-body-sm text-on-surface-variant break-words">{ed.school}</p>
                        </div>
                        <div className="flex gap-1 shrink-0">
                          <button
                            type="button"
                            onClick={() => openEducationModal(ed)}
                            className="p-1 text-on-surface-variant hover:text-primary transition-colors"
                            aria-label="Düzenle"
                          >
                            <Pencil className="w-4 h-4" />
                          </button>
                          <button
                            type="button"
                            onClick={() => handleDeleteEducation(ed.id)}
                            className="p-1 text-on-surface-variant hover:text-error transition-colors"
                            aria-label="Sil"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                      <span className="inline-block mt-xs text-label-md text-primary bg-primary-fixed/20 px-2 py-1 rounded">
                        {formatPeriod(ed.start_date, ed.end_date)}
                      </span>
                      {ed.description && (
                        <MarkdownView
                          source={ed.description}
                          className="text-body-sm text-on-surface-variant mt-sm leading-relaxed break-words"
                        />
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </Card>

          <Card
            title="Projelerim"
            action={
              <button
                type="button"
                onClick={() => openProjectModal(null)}
                className="flex items-center gap-1 text-primary text-label-md hover:underline"
              >
                <Plus className="w-4 h-4" /> Ekle
              </button>
            }
          >
            <div className="space-y-md">
              {projects.length === 0 ? (
                <p className="text-body-sm text-on-surface-variant">
                  Henüz proje eklenmedi. &quot;Ekle&quot; butonuna tıklayarak ekleyebilirsiniz.
                </p>
              ) : (
                projects.map((project) => (
                  <div key={project.id} className="flex gap-md">
                    <div className="w-10 h-10 rounded border border-outline-variant bg-surface flex items-center justify-center shrink-0">
                      <Rocket className="w-5 h-5 text-on-surface-variant" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <h3 className="font-semibold text-on-surface min-w-0 break-words">
                          {project.url ? (
                            <a
                              href={project.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="hover:text-primary hover:underline"
                            >
                              {project.title}
                            </a>
                          ) : (
                            project.title
                          )}
                        </h3>
                        <div className="flex gap-1 shrink-0">
                          <button
                            type="button"
                            onClick={() => openProjectModal(project)}
                            className="p-1 text-on-surface-variant hover:text-primary transition-colors"
                            aria-label="Düzenle"
                          >
                            <Pencil className="w-4 h-4" />
                          </button>
                          <button
                            type="button"
                            onClick={() => handleDeleteProject(project.id)}
                            className="p-1 text-on-surface-variant hover:text-error transition-colors"
                            aria-label="Sil"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                      {project.description && (
                        <MarkdownView
                          source={project.description}
                          className="text-body-sm text-on-surface-variant mt-xs break-words"
                        />
                      )}
                      {project.tech_stack && project.tech_stack.length > 0 && (
                        <div className="flex flex-wrap gap-xs mt-sm">
                          {project.tech_stack.map((tag) => (
                            <span
                              key={tag}
                              className="bg-primary-fixed/20 text-primary px-2 py-0.5 rounded text-[10px] font-bold uppercase break-all"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>

        <div className="space-y-lg md:block min-w-0">
          <Card
            title="Hakkımda Detayları"
            action={<SectionEditButton onClick={() => setAboutDetailsModalOpen(true)} />}
          >
            <div className="space-y-md">
              <div>
                <p className="text-label-md text-on-surface-variant mb-xs">CİNSİYET</p>
                <p className="text-body-sm text-on-surface break-words">
                  {displayProfile.gender || "Belirtilmedi"}
                </p>
              </div>
              <div>
                <p className="text-label-md text-on-surface-variant mb-xs">UYRUK</p>
                <p className="text-body-sm text-on-surface break-words">
                  {displayProfile.nationality || "Belirtilmedi"}
                </p>
              </div>
              <div>
                <p className="text-label-md text-on-surface-variant mb-xs">SÜRÜCÜ BELGESİ</p>
                <p className="text-body-sm text-on-surface break-words">
                  {displayProfile.driver_license || "Belirtilmedi"}
                </p>
              </div>
              {displayProfile.gender !== "Kadın" && (
                <div>
                  <p className="text-label-md text-on-surface-variant mb-xs">ASKERLİK DURUMU</p>
                  <p className="text-body-sm text-on-surface break-words">
                    {displayProfile.military_status || "Belirtilmedi"}
                  </p>
                </div>
              )}
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
                    className="bg-primary-fixed/20 text-primary px-2 py-1 rounded font-label-md text-label-md break-all max-w-full"
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
            action={
              <button
                type="button"
                onClick={() => openCertificateModal(null)}
                className="flex items-center gap-1 text-primary text-label-md hover:underline"
              >
                <Plus className="w-4 h-4" /> Ekle
              </button>
            }
          >
            {certificates.length === 0 ? (
              <p className="text-body-sm text-on-surface-variant italic">Henüz eklenmedi</p>
            ) : (
              <div className="space-y-sm">
                {certificates.map((c) => (
                  <div key={c.id} className="flex items-start justify-between gap-2">
                    <div className="flex gap-xs items-start min-w-0">
                      <Award className="w-4 h-4 text-primary mt-0.5 shrink-0" />
                      <div className="min-w-0">
                        <p className="text-body-sm text-on-surface break-words">{c.title}</p>
                        {c.issuer && (
                          <p className="text-body-sm text-on-surface-variant break-words">{c.issuer}</p>
                        )}
                        {c.issue_date && (
                          <p className="text-body-sm text-on-surface-variant">
                            {formatMonthYear(c.issue_date)}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-1 shrink-0">
                      <button
                        type="button"
                        onClick={() => openCertificateModal(c)}
                        className="p-1 text-on-surface-variant hover:text-primary transition-colors"
                        aria-label="Düzenle"
                      >
                        <Pencil className="w-4 h-4" />
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDeleteCertificate(c.id)}
                        className="p-1 text-on-surface-variant hover:text-error transition-colors"
                        aria-label="Sil"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>

          <Card
            title="Sınavlar"
            action={
              <button
                type="button"
                onClick={() => openExamModal(null)}
                className="flex items-center gap-1 text-primary text-label-md hover:underline"
              >
                <Plus className="w-4 h-4" /> Ekle
              </button>
            }
          >
            {exams.length === 0 ? (
              <p className="text-body-sm text-on-surface-variant italic">Henüz eklenmedi</p>
            ) : (
              <div className="space-y-sm">
                {exams.map((e) => (
                  <div key={e.id} className="flex items-start justify-between gap-2">
                    <div className="flex gap-xs items-start min-w-0">
                      <ClipboardList className="w-4 h-4 text-primary mt-0.5 shrink-0" />
                      <div className="min-w-0">
                        <p className="text-body-sm text-on-surface break-words">{e.name}</p>
                        {(e.score || e.exam_date) && (
                          <p className="text-body-sm text-on-surface-variant break-words">
                            {[e.score, formatMonthYear(e.exam_date)].filter(Boolean).join(" • ")}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-1 shrink-0">
                      <button
                        type="button"
                        onClick={() => openExamModal(e)}
                        className="p-1 text-on-surface-variant hover:text-primary transition-colors"
                        aria-label="Düzenle"
                      >
                        <Pencil className="w-4 h-4" />
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDeleteExam(e.id)}
                        className="p-1 text-on-surface-variant hover:text-error transition-colors"
                        aria-label="Sil"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>

          <Card
            title="Yabancı Dil"
            action={
              <button
                type="button"
                onClick={() => openLanguageModal(null)}
                className="flex items-center gap-1 text-primary text-label-md hover:underline"
              >
                <Plus className="w-4 h-4" /> Ekle
              </button>
            }
          >
            {languages.length === 0 ? (
              <p className="text-body-sm text-on-surface-variant italic">Henüz eklenmedi</p>
            ) : (
              <div className="space-y-sm">
                {languages.map((l) => (
                  <div key={l.id} className="flex items-start justify-between gap-2">
                    <div className="flex gap-xs items-start min-w-0">
                      <Globe className="w-4 h-4 text-primary mt-0.5 shrink-0" />
                      <div className="min-w-0">
                        <p className="text-body-sm text-on-surface break-words">{l.name}</p>
                        {l.level && (
                          <p className="text-body-sm text-on-surface-variant break-words">
                            {l.level}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-1 shrink-0">
                      <button
                        type="button"
                        onClick={() => openLanguageModal(l)}
                        className="p-1 text-on-surface-variant hover:text-primary transition-colors"
                        aria-label="Düzenle"
                      >
                        <Pencil className="w-4 h-4" />
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDeleteLanguage(l.id)}
                        className="p-1 text-on-surface-variant hover:text-error transition-colors"
                        aria-label="Sil"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>

          <Card
            title="Sosyal Bağlantılar"
            action={
              <button
                type="button"
                onClick={() => openSocialLinkModal(null)}
                className="flex items-center gap-1 text-primary text-label-md hover:underline"
              >
                <Plus className="w-4 h-4" /> Ekle
              </button>
            }
          >
            {socialLinks.length === 0 ? (
              <span className="flex items-center gap-xs text-body-sm text-on-surface-variant italic">
                <Link2 className="w-4 h-4" /> Henüz eklenmedi
              </span>
            ) : (
              <div className="space-y-sm">
                {socialLinks.map((s) => (
                  <div key={s.id} className="flex items-start justify-between gap-2">
                    <a
                      href={s.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-body-sm text-primary hover:underline break-all min-w-0"
                    >
                      {s.platform}
                    </a>
                    <div className="flex gap-1 shrink-0">
                      <button
                        type="button"
                        onClick={() => openSocialLinkModal(s)}
                        className="p-1 text-on-surface-variant hover:text-primary transition-colors"
                        aria-label="Düzenle"
                      >
                        <Pencil className="w-4 h-4" />
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDeleteSocialLink(s.id)}
                        className="p-1 text-on-surface-variant hover:text-error transition-colors"
                        aria-label="Sil"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>

          <Card
            title="Referanslar"
            action={
              <button
                type="button"
                onClick={() => openReferenceModal(null)}
                className="flex items-center gap-1 text-primary text-label-md hover:underline"
              >
                <Plus className="w-4 h-4" /> Ekle
              </button>
            }
          >
            {references.length === 0 ? (
              <p className="text-body-sm text-on-surface-variant italic">Henüz eklenmedi</p>
            ) : (
              <div className="space-y-sm">
                {references.map((r) => (
                  <div key={r.id} className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <p className="text-body-sm text-on-surface break-words">{r.name}</p>
                      {(r.title || r.company) && (
                        <p className="text-body-sm text-on-surface-variant break-words">
                          {[r.title, r.company].filter(Boolean).join(" • ")}
                        </p>
                      )}
                      {r.contact && (
                        <p className="flex items-center gap-xs text-body-sm text-on-surface-variant break-all">
                          <Phone className="w-3.5 h-3.5 shrink-0" />
                          {r.contact}
                        </p>
                      )}
                    </div>
                    <div className="flex gap-1 shrink-0">
                      <button
                        type="button"
                        onClick={() => openReferenceModal(r)}
                        className="p-1 text-on-surface-variant hover:text-primary transition-colors"
                        aria-label="Düzenle"
                      >
                        <Pencil className="w-4 h-4" />
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDeleteReference(r.id)}
                        className="p-1 text-on-surface-variant hover:text-error transition-colors"
                        aria-label="Sil"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
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

      <ExperienceModal
        open={experienceModalOpen}
        experience={editingExperience}
        onClose={() => setExperienceModalOpen(false)}
        onSaved={loadExperiences}
      />

      <ProjectModal
        open={projectModalOpen}
        project={editingProject}
        onClose={() => setProjectModalOpen(false)}
        onSaved={loadProjects}
      />

      <EducationModal
        open={educationModalOpen}
        education={editingEducation}
        onClose={() => setEducationModalOpen(false)}
        onSaved={loadEducation}
      />

      <AboutDetailsModal
        open={aboutDetailsModalOpen}
        profile={displayProfile}
        onClose={() => setAboutDetailsModalOpen(false)}
        onSaved={handleSaved}
      />

      <CertificateModal
        open={certificateModalOpen}
        certificate={editingCertificate}
        onClose={() => setCertificateModalOpen(false)}
        onSaved={loadCertificates}
      />

      <ExamModal
        open={examModalOpen}
        exam={editingExam}
        onClose={() => setExamModalOpen(false)}
        onSaved={loadExams}
      />

      <LanguageModal
        open={languageModalOpen}
        language={editingLanguage}
        onClose={() => setLanguageModalOpen(false)}
        onSaved={loadLanguages}
      />

      <SocialLinkModal
        open={socialLinkModalOpen}
        socialLink={editingSocialLink}
        onClose={() => setSocialLinkModalOpen(false)}
        onSaved={loadSocialLinks}
      />

      <ReferenceModal
        open={referenceModalOpen}
        reference={editingReference}
        onClose={() => setReferenceModalOpen(false)}
        onSaved={loadReferences}
      />
    </main>
  );
}

export default function ProfilePage() {
  return (
    <AppLayout>
      <ProfileContent />
    </AppLayout>
  );
}
