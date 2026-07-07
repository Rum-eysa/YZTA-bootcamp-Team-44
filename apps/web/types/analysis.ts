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
// types/analysis.ts

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

export interface CoverLetterResponse {
  id: string;
  content: string;
  analysis_id: string;
  created_at: string;
  updated_at?: string;
}

export interface CVGenerationResponse {
  id: string;
  content: string;
  analysis_id: string;
  format: 'pdf' | 'docx' | 'markdown';
  created_at: string;
  updated_at?: string;
}

export interface MatchResponse {
  id: string;
  analysis_id: string;
  match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  overall_fit: 'excellent' | 'good' | 'moderate' | 'low';
  recommendations: string[];
  created_at: string;
}