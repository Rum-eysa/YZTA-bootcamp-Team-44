import api from "../api";
import type { UserResponse, UserUpdate } from "@/types/user";

export async function getMe(): Promise<UserResponse> {
  const { data } = await api.get<UserResponse>("/api/users/me");
  return data;
}

export async function patchProfile(update: UserUpdate): Promise<UserResponse> {
  const { data } = await api.patch<UserResponse>("/api/profiles/me", update);
  return data;
}

export async function uploadAvatar(file: File): Promise<UserResponse> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post<UserResponse>("/api/profiles/me/avatar", form);
  return data;
}

export async function deleteAvatar(): Promise<UserResponse> {
  const { data } = await api.delete<UserResponse>("/api/profiles/me/avatar");
  return data;
}
