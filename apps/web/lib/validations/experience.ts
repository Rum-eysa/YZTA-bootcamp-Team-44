import { z } from "zod";

export const experienceSchema = z
  .object({
    company: z
      .string()
      .min(1, "Şirket adı zorunludur")
      .max(255, "Şirket adı en fazla 255 karakter olabilir"),
    title: z
      .string()
      .min(1, "Pozisyon zorunludur")
      .max(255, "Pozisyon en fazla 255 karakter olabilir"),
    start_date: z.string().optional().or(z.literal("")),
    end_date: z.string().optional().or(z.literal("")),
    description: z.string().optional().or(z.literal("")),
  })
  .superRefine((data, ctx) => {
    if (data.start_date && data.end_date && data.end_date < data.start_date) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Bitiş tarihi başlangıç tarihinden önce olamaz",
        path: ["end_date"],
      });
    }
  });

export type ExperienceFormData = z.infer<typeof experienceSchema>;
