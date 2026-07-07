"use client";

import { Button } from "@/components/ui/Button";
import { FormError } from "@/components/ui/FormError";
import { Input } from "@/components/ui/Input";
import { MarkdownEditor } from "@/components/ui/MarkdownEditor";
import { Modal } from "@/components/ui/Modal";
import { TagInput } from "@/components/ui/TagInput";
import { createProject, updateProject } from "@/lib/api/projects";
import { projectSchema, type ProjectFormData } from "@/lib/validations/project";
import type { Project, ProjectCreate } from "@/types/project";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useState } from "react";
import { Controller, useForm } from "react-hook-form";

interface ProjectModalProps {
  open: boolean;
  project: Project | null;
  onClose: () => void;
  onSaved: () => void;
}

function normalizeProjectUrl(value: string | null | undefined): string | null {
  const trimmed = value?.trim();
  if (!trimmed) return null;
  if (/^https?:\/\//i.test(trimmed)) return trimmed;
  if (/^www\./i.test(trimmed)) return `https://${trimmed}`;
  return trimmed;
}

function toPayload(data: ProjectFormData): ProjectCreate {
  return {
    title: data.title,
    description: data.description?.trim() || null,
    tech_stack: data.tech_stack ?? [],
    url: normalizeProjectUrl(data.url),
  };
}

export function ProjectModal({ open, project, onClose, onSaved }: ProjectModalProps) {
  const [apiError, setApiError] = useState<string>();

  const {
    register,
    control,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
    defaultValues: { title: "", description: "", tech_stack: [], url: "" },
  });

  useEffect(() => {
    if (!open) return;
    reset({
      title: project?.title || "",
      description: project?.description || "",
      tech_stack: project?.tech_stack || [],
      url: project?.url || "",
    });
    setApiError(undefined);
  }, [open, project, reset]);

  const onSubmit = async (data: ProjectFormData) => {
    setApiError(undefined);
    try {
      const payload = toPayload(data);
      if (project) {
        await updateProject(project.id, payload);
      } else {
        await createProject(payload);
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
      title={project ? "Projeyi Düzenle" : "Proje Ekle"}
      footer={
        <>
          <Button type="button" variant="outline" onClick={onClose}>
            İptal
          </Button>
          <Button type="submit" form="project-form" loading={isSubmitting}>
            Kaydet
          </Button>
        </>
      }
    >
      <form id="project-form" onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <FormError message={apiError} />
        <Input label="Proje Adı" error={errors.title?.message} {...register("title")} />
        <MarkdownEditor
          label="Açıklama"
          value={watch("description") || ""}
          onChange={(v) => setValue("description", v, { shouldValidate: true })}
          error={errors.description?.message}
          placeholder="Madde eklemek için '-' ile başlayabilirsiniz. Kalın için **metin**"
        />
        <Controller
          name="tech_stack"
          control={control}
          render={({ field }) => (
            <TagInput
              label="Teknolojiler"
              value={field.value || []}
              onChange={field.onChange}
              placeholder="Teknoloji ekleyip Enter'a basın"
              error={errors.tech_stack?.message}
            />
          )}
        />
        <Input
          label="Proje Bağlantısı"
          placeholder="https://... veya www.ornek.com"
          error={errors.url?.message}
          {...register("url")}
        />
      </form>
    </Modal>
  );
}
