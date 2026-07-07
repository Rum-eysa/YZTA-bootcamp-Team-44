"use client";

import { Button } from "@/components/ui/Button";
import { FormError } from "@/components/ui/FormError";
import { Input } from "@/components/ui/Input";
import { MarkdownEditor } from "@/components/ui/MarkdownEditor";
import { Modal } from "@/components/ui/Modal";
import { createEducation, updateEducation } from "@/lib/api/education";
import { educationSchema, type EducationFormData } from "@/lib/validations/education";
import type { EducationCreate, EducationRecord } from "@/types/education";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";

interface EducationModalProps {
  open: boolean;
  education: EducationRecord | null;
  onClose: () => void;
  onSaved: () => void;
}

function toPayload(data: EducationFormData): EducationCreate {
  return {
    school: data.school,
    degree: data.degree?.trim() || null,
    field_of_study: data.field_of_study?.trim() || null,
    start_date: data.start_date || null,
    end_date: data.end_date || null,
    description: data.description?.trim() || null,
  };
}

export function EducationModal({ open, education, onClose, onSaved }: EducationModalProps) {
  const [apiError, setApiError] = useState<string>();

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<EducationFormData>({
    resolver: zodResolver(educationSchema),
    defaultValues: {
      school: "",
      degree: "",
      field_of_study: "",
      start_date: "",
      end_date: "",
      description: "",
    },
  });

  useEffect(() => {
    if (!open) return;
    reset({
      school: education?.school || "",
      degree: education?.degree || "",
      field_of_study: education?.field_of_study || "",
      start_date: education?.start_date || "",
      end_date: education?.end_date || "",
      description: education?.description || "",
    });
    setApiError(undefined);
  }, [open, education, reset]);

  const onSubmit = async (data: EducationFormData) => {
    setApiError(undefined);
    try {
      const payload = toPayload(data);
      if (education) await updateEducation(education.id, payload);
      else await createEducation(payload);
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
      title={education ? "Eğitimi Düzenle" : "Eğitim Ekle"}
      footer={
        <>
          <Button type="button" variant="outline" onClick={onClose}>
            İptal
          </Button>
          <Button type="submit" form="education-form" loading={isSubmitting}>
            Kaydet
          </Button>
        </>
      }
    >
      <form id="education-form" onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <FormError message={apiError} />
        <Input label="Okul" error={errors.school?.message} {...register("school")} />
        <Input label="Derece" placeholder="Lisans / Lise / ..." error={errors.degree?.message} {...register("degree")} />
        <Input
          label="Bölüm"
          placeholder="Bilgisayar Mühendisliği"
          error={errors.field_of_study?.message}
          {...register("field_of_study")}
        />
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

