import api from "../api";
import type { Exam, ExamCreate, ExamUpdate } from "@/types/exam";

export async function listExams(): Promise<Exam[]> {
  const { data } = await api.get<Exam[]>("/api/profiles/me/exams");
  return data;
}

export async function createExam(payload: ExamCreate): Promise<Exam> {
  const { data } = await api.post<Exam>("/api/profiles/me/exams", payload);
  return data;
}

export async function updateExam(id: string, payload: ExamUpdate): Promise<Exam> {
  const { data } = await api.patch<Exam>(`/api/profiles/me/exams/${id}`, payload);
  return data;
}

export async function deleteExam(id: string): Promise<void> {
  await api.delete(`/api/profiles/me/exams/${id}`);
}

