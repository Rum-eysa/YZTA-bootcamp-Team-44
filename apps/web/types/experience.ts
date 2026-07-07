export interface WorkExperience {
  id: string;
  user_id: string;
  company: string;
  title: string;
  start_date: string | null;
  end_date: string | null;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface WorkExperienceCreate {
  company: string;
  title: string;
  start_date?: string | null;
  end_date?: string | null;
  description?: string | null;
}

export type WorkExperienceUpdate = Partial<WorkExperienceCreate>;
