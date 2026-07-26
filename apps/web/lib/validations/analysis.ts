import { z } from "zod";

export const analysisSchema = z.object({
  company_name: z.string().trim().min(1),
  position_title: z.string().trim().min(1),
  listing_text: z.string().trim().min(50),
  listing_url: z.string().optional().or(z.literal("")),
});

export type AnalysisFormData = z.infer<typeof analysisSchema>;
