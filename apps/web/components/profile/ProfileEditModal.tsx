"use client";

import { Button } from "@/components/ui/Button";
import { FormError } from "@/components/ui/FormError";
import { Input } from "@/components/ui/Input";
import { MarkdownEditor } from "@/components/ui/MarkdownEditor";
import { Modal } from "@/components/ui/Modal";
import { Select } from "@/components/ui/Select";
import { TagInput } from "@/components/ui/TagInput";
import { patchProfile } from "@/lib/api/profiles";
import { formatTRPhone } from "@/lib/phone";
import {
  COMING_SOON_SECTIONS,
  headerSchema,
  skillsSchema,
  summarySchema,
  type HeaderFormData,
  type ProfileEditSection,
  type SkillsFormData,
  type SummaryFormData,
} from "@/lib/validations/profile";
import type { UserResponse, UserUpdate } from "@/types/user";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useState } from "react";
import { Controller, useForm } from "react-hook-form";

interface ProfileEditModalProps {
  open: boolean;
  section: ProfileEditSection;
  comingSoonKey?: string;
  profile: UserResponse | null;
  onClose: () => void;
  onSaved: (user: UserResponse) => void;
}

const SENIORITY_OPTIONS = [
  { value: "", label: "Seçiniz" },
  { value: "junior", label: "Junior" },
  { value: "mid", label: "Mid" },
  { value: "senior", label: "Senior" },
];

function normalizeHeaderPayload(data: HeaderFormData): UserUpdate {
  return {
    full_name: data.full_name,
    email: data.email,
    target_position: data.target_position,
    seniority: data.seniority ? data.seniority : undefined,
    experience_years:
      data.experience_years === "" ||
      data.experience_years === undefined ||
      data.experience_years === null
        ? undefined
        : Number(data.experience_years),
    phone: data.phone?.trim() || undefined,
    location: data.location?.trim() || undefined,
    birth_year:
      data.birth_year === "" || data.birth_year === undefined || data.birth_year === null
        ? undefined
        : Number(data.birth_year),
  };
}

export function ProfileEditModal({
  open,
  section,
  comingSoonKey,
  profile,
  onClose,
  onSaved,
}: ProfileEditModalProps) {
  const [apiError, setApiError] = useState<string>();
  const currentYear = new Date().getFullYear();

  const headerForm = useForm<HeaderFormData>({
    resolver: zodResolver(headerSchema),
    defaultValues: {
      full_name: "",
      email: "",
      target_position: "",
      seniority: "",
      experience_years: "",
      phone: "",
      location: "",
      birth_year: "",
    },
  });

  const summaryForm = useForm<SummaryFormData>({
    resolver: zodResolver(summarySchema),
    defaultValues: { experience_summary: "" },
  });

  const skillsForm = useForm<SkillsFormData>({
    resolver: zodResolver(skillsSchema),
    defaultValues: { skills: [] },
  });

  useEffect(() => {
    if (!open || !profile) return;

    if (section === "header") {
      headerForm.reset({
        full_name: profile.full_name || "",
        email: profile.email,
        target_position: profile.target_position || "",
        seniority: (profile.seniority as HeaderFormData["seniority"]) || "",
        experience_years: profile.experience_years ?? "",
        phone: profile.phone || "",
        location: profile.location || "",
        birth_year: profile.birth_year ?? "",
      });
    } else if (section === "summary") {
      summaryForm.reset({ experience_summary: profile.experience_summary || "" });
    } else if (section === "skills") {
      skillsForm.reset({ skills: profile.skills || [] });
    }
    setApiError(undefined);
  }, [open, section, profile, headerForm, summaryForm, skillsForm]);

  const submitUpdate = async (data: UserUpdate) => {
    setApiError(undefined);
    try {
      const updated = await patchProfile(data);
      onSaved(updated);
      onClose();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data
        ?.detail;
      setApiError(
        typeof detail === "string" ? detail : "Kayıt başarısız. Lütfen alanları kontrol edin."
      );
    }
  };

  const titles: Record<ProfileEditSection, string> = {
    header: "Profil Bilgilerini Düzenle",
    summary: "Özgeçmiş Özetini Düzenle",
    skills: "Yetenekleri Düzenle",
    coming_soon: comingSoonKey
      ? `${COMING_SOON_SECTIONS[comingSoonKey] || "Bölüm"} Düzenle`
      : "Yakında",
  };

  const isSubmitting =
    headerForm.formState.isSubmitting ||
    summaryForm.formState.isSubmitting ||
    skillsForm.formState.isSubmitting;

  const renderContent = () => {
    if (section === "coming_soon") {
      return (
        <p className="text-body-sm text-on-surface-variant">
          {comingSoonKey && COMING_SOON_SECTIONS[comingSoonKey]
            ? `${COMING_SOON_SECTIONS[comingSoonKey]} düzenleme özelliği yakında eklenecektir.`
            : "Bu özellik yakında eklenecektir."}
        </p>
      );
    }

    if (section === "header") {
      const { register, handleSubmit, formState: { errors } } = headerForm;
      return (
        <form
          id="profile-edit-form"
          onSubmit={handleSubmit((data) => submitUpdate(normalizeHeaderPayload(data)))}
          className="space-y-4"
        >
          <FormError message={apiError} />
          <Input label="Ad Soyad" maxLength={50} error={errors.full_name?.message} {...register("full_name")} />
          <Input label="E-posta" type="email" maxLength={255} error={errors.email?.message} {...register("email")} />
          <Input
            label="İş Unvanı"
            maxLength={50}
            error={errors.target_position?.message}
            {...register("target_position")}
          />
          <Select
            label="Deneyim Seviyesi"
            options={SENIORITY_OPTIONS}
            error={errors.seniority?.message}
            {...register("seniority")}
          />
          <Input
            label="Deneyim Yılı"
            type="number"
            placeholder="3"
            min="0"
            max="60"
            step="0.5"
            error={errors.experience_years?.message}
            {...register("experience_years")}
          />
          <Input
            label="Telefon"
            placeholder="+90 (555) 123 45 67"
            inputMode="tel"
            error={errors.phone?.message}
            {...register("phone", {
              onChange: (e) => {
                headerForm.setValue("phone", formatTRPhone(e.target.value), { shouldValidate: true });
              },
            })}
          />
          <Input label="Konum" placeholder="İstanbul, Türkiye" maxLength={50} error={errors.location?.message} {...register("location")} />
          <Input
            label="Doğum Yılı"
            type="number"
            placeholder="2003"
            min="1900"
            max={String(currentYear)}
            error={errors.birth_year?.message}
            {...register("birth_year")}
          />
        </form>
      );
    }

    if (section === "summary") {
      const {
        handleSubmit,
        watch,
        setValue,
        formState: { errors },
      } = summaryForm;
      return (
        <form id="profile-edit-form" onSubmit={handleSubmit(submitUpdate)} className="space-y-4">
          <FormError message={apiError} />
          <MarkdownEditor
            label="Özgeçmiş Özeti"
            value={watch("experience_summary") || ""}
            onChange={(v) => setValue("experience_summary", v, { shouldValidate: true })}
            error={errors.experience_summary?.message}
            placeholder="Madde eklemek için '-' ile başlayabilirsiniz. Kalın için **metin**"
          />
        </form>
      );
    }

    if (section === "skills") {
      const { control, handleSubmit, formState: { errors } } = skillsForm;
      return (
        <form id="profile-edit-form" onSubmit={handleSubmit(submitUpdate)} className="space-y-4">
          <FormError message={apiError} />
          <Controller
            name="skills"
            control={control}
            render={({ field }) => (
              <TagInput
                label="Yetenekler"
                value={field.value}
                onChange={field.onChange}
                error={errors.skills?.message}
                placeholder="Yetenek ekleyip Enter'a basın"
              />
            )}
          />
        </form>
      );
    }

    return null;
  };

  const footer =
    section === "coming_soon" ? (
      <Button type="button" onClick={onClose}>
        Kapat
      </Button>
    ) : (
      <>
        <Button type="button" variant="outline" onClick={onClose}>
          İptal
        </Button>
        <Button type="submit" form="profile-edit-form" loading={isSubmitting}>
          Kaydet
        </Button>
      </>
    );

  return (
    <Modal open={open} onClose={onClose} title={titles[section]} footer={footer}>
      {renderContent()}
    </Modal>
  );
}
