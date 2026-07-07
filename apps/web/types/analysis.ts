export interface AnalyzeRequest {
  listing_text?: string;
  listing_url?: string;
  company_name?: string;
  position_title?: string;
  location?: string;
  employment_type?: string;
  company_about?: string;
  extra_notes?: string;
  benefits?: string[];
  experience_level?: string;
  education_level?: string;
  military_status?: string;
  languages?: string[];
  driver_license?: string;
}

export interface AnalyzeResponse {
  listing_id: string;
  required_skills: string[];
  nice_to_have: string[];
  seniority: string;
  position_title: string;
  confidence: number;
}
