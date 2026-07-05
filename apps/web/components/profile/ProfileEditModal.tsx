"use client";

import { Button } from "@/components/ui/Button";
import { FormError } from "@/components/ui/FormError";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { TagInput } from "@/components/ui/TagInput";
import { Textarea } from "@/components/ui/Textarea";
import { patchProfile } from "@/lib/api/profiles";
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

function normalizeHeaderPayload(data: HeaderFormData): UserUpdate {
  return {
    full_name: data.full_name,
    email: data.email,
    target_position: data.target_position,
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

  const headerForm = useForm<HeaderFormData>({
    resolver: zodResolver(headerSchema),
    defaultValues: {
      full_name: "",
      email: "",
      target_position: "",
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
          <Input label="Ad Soyad" error={errors.full_name?.message} {...register("full_name")} />
          <Input label="E-posta" type="email" error={errors.email?.message} {...register("email")} />
          <Input
            label="İş Unvanı"
            error={errors.target_position?.message}
            {...register("target_position")}
          />
          <Input label="Telefon" placeholder="+90 500 000 00 00" error={errors.phone?.message} {...register("phone")} />
          <Input label="Konum" placeholder="İstanbul, Türkiye" error={errors.location?.message} {...register("location")} />
          <Input
            label="Doğum Yılı"
            type="number"
            placeholder="2003"
            min="1900"
            max="2100"
            error={errors.birth_year?.message}
            {...register("birth_year")}
          />
        </form>
      );
    }

    if (section === "summary") {
      const { register, handleSubmit, formState: { errors } } = summaryForm;
      return (
        <form id="profile-edit-form" onSubmit={handleSubmit(submitUpdate)} className="space-y-4">
          <FormError message={apiError} />
          <Textarea
            label="Özgeçmiş Özeti"
            className="min-h-[160px]"
            error={errors.experience_summary?.message}
            {...register("experience_summary")}
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
                label="Beceriler"
                value={field.value}
                onChange={field.onChange}
                error={errors.skills?.message}
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
