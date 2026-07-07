export interface Exam {
  id: string;
  user_id: string;
  name: string;
  score: string | null;
  exam_date: string | null;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface ExamCreate {
  name: string;
  score?: string | null;
  exam_date?: string | null;
  description?: string | null;
}

export type ExamUpdate = Partial<ExamCreate>;

