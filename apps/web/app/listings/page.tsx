"use client";

import { AppLayout } from "@/components/layout/AppLayout";
import { Spinner } from "@/components/ui/Spinner";
import { listListings } from "@/lib/api/listings";
import { cn } from "@/lib/utils";
import {
  APPLICATION_STAGE_LABELS,
  type ApplicationStage,
  type ListingSummary,
} from "@/types/listing";
import { Building2, Filter, MapPin, PlusCircle, Zap } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

const STAGE_STYLES: Record<ApplicationStage, string> = {
  review: "bg-secondary-container text-on-secondary-container",
  interview: "bg-primary-container text-on-primary",
  technical_test: "bg-primary-fixed/40 text-primary",
  offer: "bg-primary text-on-primary",
  rejected: "bg-error-container/40 text-error",
};

type SortKey = "date_desc" | "date_asc" | "score_desc";
type StageFilter = "all" | ApplicationStage;

function formatDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleDateString("tr-TR", { day: "numeric", month: "short", year: "numeric" });
}

function ListingsContent() {
  const [listings, setListings] = useState<ListingSummary[] | null>(null);
  const [logos, setLogos] = useState<Record<string, string>>({});
  const [error, setError] = useState<string>();
  const [stageFilter, setStageFilter] = useState<StageFilter>("all");
  const [sortKey, setSortKey] = useState<SortKey>("date_desc");

  useEffect(() => {
    listListings()
      .then(setListings)
      .catch(() => setError("İlanlar yüklenemedi. Lütfen tekrar deneyin."));
  }, []);

  useEffect(() => {
    if (!listings) return;
    const map: Record<string, string> = {};
    for (const l of listings) {
      const logo = localStorage.getItem(`listing-logo:${l.id}`);
      if (logo) map[l.id] = logo;
    }
    setLogos(map);
  }, [listings]);

  const visible = useMemo(() => {
    if (!listings) return [];
    const filtered = listings.filter(
      (l) => stageFilter === "all" || l.application_stage === stageFilter
    );
    const sorted = [...filtered];
    sorted.sort((a, b) => {
      if (sortKey === "score_desc") return (b.score ?? -1) - (a.score ?? -1);
      const diff = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
      return sortKey === "date_asc" ? diff : -diff;
    });
    return sorted;
  }, [listings, stageFilter, sortKey]);

  return (
    <div className="max-w-[1024px] mx-auto px-margin-mobile md:px-lg py-lg md:py-xl space-y-lg">
      <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-md">
        <div>
          <h1 className="text-headline-lg-mobile md:text-headline-lg font-bold text-on-surface">
            İlanlarım
          </h1>
          <p className="text-body-sm text-on-surface-variant mt-1">
            Kariyer yolculuğunuzdaki aktif başvurularınız.
          </p>
        </div>
        <div className="flex items-center gap-sm">
          <div className="relative">
            <Filter className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-on-surface-variant pointer-events-none" />
            <select
              aria-label="Aşamaya göre filtrele"
              className="input-field pl-8 py-1.5"
              value={stageFilter}
              onChange={(e) => setStageFilter(e.target.value as StageFilter)}
            >
              <option value="all">Tümü</option>
              {(Object.keys(APPLICATION_STAGE_LABELS) as ApplicationStage[]).map((s) => (
                <option key={s} value={s}>
                  {APPLICATION_STAGE_LABELS[s]}
                </option>
              ))}
            </select>
          </div>
          <select
            aria-label="Sırala"
            className="input-field py-1.5"
            value={sortKey}
            onChange={(e) => setSortKey(e.target.value as SortKey)}
          >
            <option value="date_desc">En yeni</option>
            <option value="date_asc">En eski</option>
            <option value="score_desc">Skora göre</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="rounded-lg border border-error bg-error-container/30 px-4 py-3 text-body-sm text-error">
          {error}
        </div>
      )}

      {!listings && !error && (
        <div className="py-3xl">
          <Spinner label="İlanlar yükleniyor..." />
        </div>
      )}

      {listings && visible.length === 0 && (
        <div className="bg-surface-container-lowest rounded-xl p-8 border border-outline-variant text-center">
          <p className="text-body-lg text-on-surface mb-2">Henüz ilan yok</p>
          <p className="text-body-sm text-on-surface-variant mb-4">
            Bir iş ilanı ekleyip analiz başlatarak başlayın.
          </p>
          <Link
            href="/apply"
            className="inline-flex items-center gap-2 text-primary font-semibold text-body-sm hover:opacity-80"
          >
            <PlusCircle className="w-4 h-4" />
            İlan Ekle
          </Link>
        </div>
      )}

      <div className="space-y-md">
        {visible.map((listing) => (
          <Link
            key={listing.id}
            href={`/listings/${listing.id}`}
            className="block bg-surface-container-lowest rounded-xl p-4 md:p-5 border border-outline-variant hover:border-primary hover:shadow-card-hover transition-all"
          >
            <div className="flex flex-col md:flex-row md:items-center gap-md">
              <div className="w-12 h-12 rounded-lg overflow-hidden border border-outline-variant bg-surface flex items-center justify-center shrink-0">
                {logos[listing.id] ? (
                  <Image
                    src={logos[listing.id]}
                    alt="Şirket logosu"
                    width={48}
                    height={48}
                    className="w-full h-full object-cover"
                    unoptimized
                  />
                ) : (
                  <Building2 className="w-6 h-6 text-on-surface-variant" />
                )}
              </div>

              <div className="flex-1 min-w-0">
                <p className="text-label-md text-on-surface-variant font-semibold uppercase tracking-wide">
                  {listing.company || "Şirket belirtilmedi"}
                </p>
                <h2 className="text-title-md font-semibold text-on-surface break-words">
                  {listing.title || "Pozisyon belirtilmedi"}
                </h2>
                <div className="flex flex-wrap items-center gap-x-md gap-y-xs mt-1 text-body-sm text-on-surface-variant">
                  {listing.location && (
                    <span className="flex items-center gap-1">
                      <MapPin className="w-4 h-4" />
                      {listing.location}
                    </span>
                  )}
                  <span>Başvuru: {formatDate(listing.created_at)}</span>
                </div>
              </div>

              <div className="flex items-center gap-md md:gap-lg shrink-0">
                <div className="text-center min-w-[72px]">
                  <div className="flex items-center justify-center gap-1 text-primary font-bold">
                    <Zap className="w-4 h-4" />
                    {listing.score != null ? `%${Math.round(listing.score)}` : "—"}
                  </div>
                  <p className="text-label-md text-on-surface-variant">
                    {listing.score != null ? "Eşleşme" : "Hesaplanmadı"}
                  </p>
                </div>

                <span
                  className={cn(
                    "px-3 py-2 rounded-lg text-label-md font-semibold text-center min-w-[96px]",
                    STAGE_STYLES[listing.application_stage]
                  )}
                >
                  {APPLICATION_STAGE_LABELS[listing.application_stage]}
                </span>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

export default function ListingsPage() {
  return (
    <AppLayout>
      <ListingsContent />
    </AppLayout>
  );
}
