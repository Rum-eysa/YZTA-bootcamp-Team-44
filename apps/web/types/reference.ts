export interface Reference {
  id: string;
  user_id: string;
  name: string;
  title: string | null;
  company: string | null;
  contact: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface ReferenceCreate {
  name: string;
  title?: string | null;
  company?: string | null;
  contact?: string | null;
  notes?: string | null;
}

export type ReferenceUpdate = Partial<ReferenceCreate>;

