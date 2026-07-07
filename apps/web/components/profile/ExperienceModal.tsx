"use client";

import { Button } from "@/components/ui/Button";
import { FormError } from "@/components/ui/FormError";
import { Input } from "@/components/ui/Input";
import { MarkdownEditor } from "@/components/ui/MarkdownEditor";
import { Modal } from "@/components/ui/Modal";
import { createExperience, updateExperience } from "@/lib/api/experiences";
import { experienceSchema, type ExperienceFormData } from "@/lib/validations/experience";
import type { WorkExperience, WorkExperienceCreate } from "@/types/experience";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";

interface ExperienceModalProps {
  open: boolean;
  experience: WorkExperience | null;
  onClose: () => void;
  onSaved: () => void;
}

function toPayload(data: ExperienceFormData): WorkExperienceCreate {
  return {
    company: data.company,
    title: data.title,
    start_date: data.start_date || null,
    end_date: data.end_date || null,
    description: data.description?.trim() || null,
  };
}

export function ExperienceModal({ open, experience, onClose, onSaved }: ExperienceModalProps) {
  const [apiError, setApiError] = useState<string>();

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ExperienceFormData>({
    resolver: zodResolver(experienceSchema),
    defaultValues: { company: "", title: "", start_date: "", end_date: "", description: "" },
  });

  useEffect(() => {
    if (!open) return;
    reset({
      company: experience?.company || "",
      title: experience?.title || "",
      start_date: experience?.start_date || "",
      end_date: experience?.end_date || "",
      description: experience?.description || "",
    });
    setApiError(undefined);
  }, [open, experience, reset]);

  const onSubmit = async (data: ExperienceFormData) => {
    setApiError(undefined);
    try {
      const payload = toPayload(data);
      if (experience) {
        await updateExperience(experience.id, payload);
      } else {
        await createExperience(payload);
      }
      onSaved();
      onClose();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setApiError(typeof detail === "string" ? detail : "Kayıt başarısız. Lütfen tekrar deneyin.");
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={experience ? "İş Deneyimini Düzenle" : "İş Deneyimi Ekle"}
      footer={
        <>
          <Button type="button" variant="outline" onClick={onClose}>
            İptal
          </Button>
          <Button type="submit" form="experience-form" loading={isSubmitting}>
            Kaydet
          </Button>
        </>
      }
    >
      <form id="experience-form" onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <FormError message={apiError} />
        <Input label="Pozisyon" error={errors.title?.message} {...register("title")} />
        <Input label="Şirket" error={errors.company?.message} {...register("company")} />
        <div className="grid grid-cols-2 gap-3">
          <Input
            label="Başlangıç"
            type="date"
            error={errors.start_date?.message}
            {...register("start_date")}
          />
          <Input
            label="Bitiş"
            type="date"
            error={errors.end_date?.message}
            {...register("end_date")}
          />
        </div>
        <MarkdownEditor
          label="Açıklama"
          value={watch("description") || ""}
          onChange={(v) => setValue("description", v, { shouldValidate: true })}
          error={errors.description?.message}
          placeholder="Madde eklemek için '-' ile başlayabilirsiniz. Kalın için **metin**"
        />
      </form>
    </Modal>
  );
}
