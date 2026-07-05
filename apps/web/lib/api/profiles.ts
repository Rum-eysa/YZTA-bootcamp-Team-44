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
