export interface Language {
  id: string;
  user_id: string;
  name: string;
  level: string | null;
  created_at: string;
  updated_at: string;
}

export interface LanguageCreate {
  name: string;
  level?: string | null;
}

export type LanguageUpdate = Partial<LanguageCreate>;

