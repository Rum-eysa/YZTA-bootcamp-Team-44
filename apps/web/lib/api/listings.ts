import api from "../api";
import type { ListingDetail, ListingSummary, ListingUpdate } from "@/types/listing";

export async function listListings(): Promise<ListingSummary[]> {
  const { data } = await api.get<ListingSummary[]>("/api/listings");
  return data;
}

export async function getListing(id: string): Promise<ListingDetail> {
  const { data } = await api.get<ListingDetail>(`/api/listings/${id}`);
  return data;
}

export async function updateListing(
  id: string,
  payload: ListingUpdate
): Promise<ListingDetail> {
  const { data } = await api.patch<ListingDetail>(`/api/listings/${id}`, payload);
  return data;
}

export async function reanalyzeListing(id: string): Promise<ListingDetail> {
  const { data } = await api.post<ListingDetail>(`/api/listings/${id}/reanalyze`, {});
  return data;
}

export async function rematchListing(id: string): Promise<ListingDetail> {
  const { data } = await api.post<ListingDetail>(`/api/listings/${id}/rematch`, {});
  return data;
}
