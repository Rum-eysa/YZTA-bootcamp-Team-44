import { z } from "zod";

export const educationSchema = z
  .object({
    school: z.string().min(1, "Okul adı zorunludur").max(255),
    degree: z.string().max(255).optional().or(z.literal("")),
    field_of_study: z.string().max(255).optional().or(z.literal("")),
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

export type EducationFormData = z.infer<typeof educationSchema>;

