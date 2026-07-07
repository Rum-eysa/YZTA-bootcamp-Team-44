import { z } from "zod";

export const headerSchema = z.object({
  full_name: z
    .string()
    .min(1, "Ad alanı zorunludur")
    .max(50, "Ad en fazla 50 karakter olabilir"),
  email: z.string().email("Geçerli bir e-posta adresi giriniz"),
  target_position: z
    .string()
    .min(1, "İş unvanı zorunludur")
    .max(50, "İş unvanı en fazla 50 karakter olabilir"),
  seniority: z
    .union([z.literal(""), z.enum(["junior", "mid", "senior"])])
    .optional()
    .or(z.literal("")),
  experience_years: z
    .union([
      z.literal(""),
      z.coerce
        .number()
        .min(0, "Deneyim yılı 0 veya daha büyük olmalıdır")
        .max(60, "Deneyim yılı 60'tan büyük olamaz"),
    ])
    .optional(),
  phone: z
    .string()
    .max(50, "Telefon en fazla 50 karakter olabilir")
    .optional()
    .or(z.literal(""))
    .refine(
      (v) => !v || /^\+90 \(\d{3}\) \d{3} \d{2} \d{2}$/.test(v),
      "Telefon formatı geçersiz. Örn: +90 (555) 123 45 67"
    ),
  location: z.string().max(50, "Konum en fazla 50 karakter olabilir").optional().or(z.literal("")),
  birth_year: z.union([
    z.literal(""),
    z.coerce
      .number()
      .int()
      .min(1900, "Geçerli bir doğum yılı giriniz")
      .max(new Date().getFullYear(), "Gelecek bir yıl seçemezsiniz"),
  ]).optional(),
});

export const summarySchema = z.object({
  experience_summary: z.string().optional(),
});

export const skillsSchema = z.object({
  skills: z.array(z.string().min(1)).min(1, "En az bir beceri ekleyiniz"),
});

export const profileSchema = headerSchema.merge(summarySchema).merge(skillsSchema);

export type HeaderFormData = z.infer<typeof headerSchema>;
export type SummaryFormData = z.infer<typeof summarySchema>;
export type SkillsFormData = z.infer<typeof skillsSchema>;
export type ProfileFormData = z.infer<typeof profileSchema>;

export type ProfileEditSection = "header" | "summary" | "skills" | "coming_soon";

export const COMING_SOON_SECTIONS: Record<string, string> = {
  experience: "İş Deneyimleri",
  education: "Eğitim",
  projects: "Projeler",
  about_details: "Hakkımda Detayları",
  certificates: "Sertifikalar",
  exams: "Sınavlar",
  languages: "Yabancı Dil",
  social: "Sosyal Bağlantılar",
  references: "Referanslar",
  company: "Şirket Hakkında",
  criteria: "Aday Kriterleri",
  notes: "Ekstra Notlar",
  benefits: "Yan Haklar",
};
