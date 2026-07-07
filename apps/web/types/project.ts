export interface Project {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  tech_stack: string[] | null;
  url: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  title: string;
  description?: string | null;
  tech_stack?: string[];
  url?: string | null;
}

export type ProjectUpdate = Partial<ProjectCreate>;
