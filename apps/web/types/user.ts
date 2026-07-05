export interface UserResponse {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  target_position: string | null;
  seniority: string | null;
  experience_years: number | null;
  skills: string[] | null;
  experience_summary: string | null;
  phone: string | null;
  location: string | null;
  birth_year: number | null;
  tone_preference: string | null;
  created_at: string;
  updated_at: string;
}

export interface UserUpdate {
  full_name?: string;
  email?: string;
  target_position?: string;
  seniority?: string;
  experience_years?: number;
  skills?: string[];
  experience_summary?: string;
  phone?: string;
  location?: string;
  birth_year?: number;
  tone_preference?: string;
}

export interface UserCreate {
  email: string;
  full_name?: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}
