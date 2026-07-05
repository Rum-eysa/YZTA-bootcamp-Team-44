import { z } from "zod";

export const analysisSchema = z
  .object({
    listing_text: z.string().optional(),
    listing_url: z
      .string()
      .url("Geçerli bir URL giriniz")
      .optional()
      .or(z.literal("")),
  })
  .superRefine((data, ctx) => {
    const text = data.listing_text?.trim() ?? "";
    const url = data.listing_url?.trim() ?? "";

    if (!text && !url) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "İlan metni veya URL alanlarından en az biri doldurulmalıdır",
        path: ["listing_text"],
      });
      return;
    }

    if (text && text.length < 50) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "İlan metni en az 50 karakter olmalıdır",
        path: ["listing_text"],
      });
    }
  });

export type AnalysisFormData = z.infer<typeof analysisSchema>;
