import { z } from "zod";

function normalizeUrl(value: unknown): unknown {
  if (typeof value !== "string") return value;
  const trimmed = value.trim();
  if (!trimmed) return trimmed;
  if (/^https?:\/\//i.test(trimmed)) return trimmed;
  if (/^www\./i.test(trimmed)) return `https://${trimmed}`;
  return trimmed;
}

export const projectSchema = z.object({
  title: z
    .string()
    .min(1, "Proje adı zorunludur")
    .max(255, "Proje adı en fazla 255 karakter olabilir"),
  description: z.string().optional().or(z.literal("")),
  tech_stack: z.array(z.string().min(1)).optional(),
  url: z.union([
    z.literal(""),
    z.preprocess(
      normalizeUrl,
      z.string().url("Geçerli bir URL giriniz").max(1000, "URL en fazla 1000 karakter olabilir")
    ),
  ]),
});

export type ProjectFormData = z.infer<typeof projectSchema>;
