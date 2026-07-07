import api from "../api";
import type { Project, ProjectCreate, ProjectUpdate } from "@/types/project";

export async function listProjects(): Promise<Project[]> {
  const { data } = await api.get<Project[]>("/api/profiles/me/projects");
  return data;
}

export async function createProject(payload: ProjectCreate): Promise<Project> {
  const { data } = await api.post<Project>("/api/profiles/me/projects", payload);
  return data;
}

export async function updateProject(
  id: string,
  payload: ProjectUpdate
): Promise<Project> {
  const { data } = await api.patch<Project>(`/api/profiles/me/projects/${id}`, payload);
  return data;
}

export async function deleteProject(id: string): Promise<void> {
  await api.delete(`/api/profiles/me/projects/${id}`);
}
