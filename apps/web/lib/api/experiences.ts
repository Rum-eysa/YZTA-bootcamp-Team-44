import api from "../api";
import type {
  WorkExperience,
  WorkExperienceCreate,
  WorkExperienceUpdate,
} from "@/types/experience";

export async function listExperiences(): Promise<WorkExperience[]> {
  const { data } = await api.get<WorkExperience[]>("/api/profiles/me/experiences");
  return data;
}

export async function createExperience(
  payload: WorkExperienceCreate
): Promise<WorkExperience> {
  const { data } = await api.post<WorkExperience>("/api/profiles/me/experiences", payload);
  return data;
}

export async function updateExperience(
  id: string,
  payload: WorkExperienceUpdate
): Promise<WorkExperience> {
  const { data } = await api.patch<WorkExperience>(
    `/api/profiles/me/experiences/${id}`,
    payload
  );
  return data;
}

export async function deleteExperience(id: string): Promise<void> {
  await api.delete(`/api/profiles/me/experiences/${id}`);
}
