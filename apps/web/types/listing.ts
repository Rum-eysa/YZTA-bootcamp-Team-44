export type ApplicationStage =
  | "review"
  | "interview"
  | "technical_test"
  | "offer"
  | "rejected";

export interface ListingSummary {
  id: string;
  title: string | null;
  company: string | null;
  location: string | null;
  seniority: string | null;
  application_stage: ApplicationStage;
  analysis_status: string | null;
  score: number | null;
  created_at: string;
}

export interface ListingDocument {
  id: string;
  doc_type: string;
  cv_url: string | null;
  cover_letter_text: string | null;
}

export interface ListingDetail {
  id: string;
  title: string | null;
  company: string | null;
  raw_text: string | null;
  seniority: string | null;
  analysis_status: string | null;
  required_skills: string[];
  nice_to_have: string[];
  location: string | null;
  employment_type: string | null;
  company_about: string | null;
  extra_notes: string | null;
  benefits: string[];
  experience_level: string | null;
  education_level: string | null;
  military_status: string | null;
  languages: string[];
  driver_license: string | null;
  application_stage: ApplicationStage;
  score: number | null;
  matched_skills: string[];
  missing_skills: string[];
  documents: ListingDocument[];
  created_at: string;
  updated_at: string;
}

export interface ListingUpdate {
  title?: string | null;
  company?: string | null;
  raw_text?: string | null;
  location?: string | null;
  employment_type?: string | null;
  company_about?: string | null;
  extra_notes?: string | null;
  benefits?: string[];
  experience_level?: string | null;
  education_level?: string | null;
  military_status?: string | null;
  languages?: string[];
  driver_license?: string | null;
  application_stage?: ApplicationStage;
}

export const APPLICATION_STAGE_LABELS: Record<ApplicationStage, string> = {
  review: "Değerlendirmede",
  interview: "Mülakat",
  technical_test: "Teknik Test",
  offer: "Teklif",
  rejected: "Reddedildi",
};
