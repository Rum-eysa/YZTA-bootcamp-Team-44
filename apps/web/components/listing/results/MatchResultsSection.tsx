"use client";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { FormError } from "@/components/ui/FormError";
import type { ScoreBreakdown } from "@/types/match";
import { cn } from "@/lib/utils";
import { Check, RefreshCw, Search, Target, X } from "lucide-react";
import { useMemo, useState } from "react";
import { ScoreGauge } from "./ScoreGauge";
import { StaleWarningIcon } from "./StaleWarningIcon";

type SkillStatusFilter = "all" | "matched" | "missing";
type SkillCategoryFilter = "all" | "required" | "nice";

interface MatchResultsSectionProps {
  score: number | null;
  scoreBreakdown: ScoreBreakdown | null;
  requiredSkills: string[];
  niceToHaveSkills: string[];
  matchedSkills: string[];
  missingSkills: string[];
  loading: boolean;
  error?: string;
  rematching: boolean;
  rematchError?: string;
  outdated?: boolean;
  compact?: boolean;
  onCalculate: () => void;
  onRematch: () => void;
}

interface SkillRow {
  skill: string;
  matched: boolean;
  category: Exclude<SkillCategoryFilter, "all">;
}

const normalizeSkill = (skill: string) => skill.trim().toLocaleLowerCase("tr-TR");

export function MatchResultsSection({
  score,
  scoreBreakdown,
  requiredSkills,
  niceToHaveSkills,
  matchedSkills,
  missingSkills,
  loading,
  error,
  rematching,
  rematchError,
  outdated = false,
  compact = false,
  onCalculate,
  onRematch,
}: MatchResultsSectionProps) {
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<SkillStatusFilter>("all");
  const [categoryFilter, setCategoryFilter] = useState<SkillCategoryFilter>("all");

  const rows = useMemo<SkillRow[]>(() => {
    const matched = new Set(matchedSkills.map(normalizeSkill));
    const missing = new Set(missingSkills.map(normalizeSkill));
    const seen = new Set<string>();

    return [
      ...requiredSkills.map((skill) => ({ skill, category: "required" as const })),
      ...niceToHaveSkills.map((skill) => ({ skill, category: "nice" as const })),
    ]
      .filter(({ skill }) => {
        const key = normalizeSkill(skill);
        if (!key || seen.has(key)) return false;
        seen.add(key);
        return true;
      })
      .map(({ skill, category }) => ({
        skill,
        category,
        matched: matched.has(normalizeSkill(skill)) && !missing.has(normalizeSkill(skill)),
      }));
  }, [matchedSkills, missingSkills, niceToHaveSkills, requiredSkills]);

  const filteredRows = rows.filter((row) => {
    const matchesQuery = normalizeSkill(row.skill).includes(normalizeSkill(query));
    const matchesStatus =
      statusFilter === "all" ||
      (statusFilter === "matched" ? row.matched : !row.matched);
    const matchesCategory = categoryFilter === "all" || row.category === categoryFilter;
    return matchesQuery && matchesStatus && matchesCategory;
  });

  const breakdownItems = scoreBreakdown
    ? [
        { label: "Zorunlu", value: scoreBreakdown.required },
        { label: "Tercih", value: scoreBreakdown.nice_to_have },
        { label: "Kıdem", value: scoreBreakdown.seniority },
        ...(typeof scoreBreakdown.semantic_bonus === "number"
          ? [{ label: "Anlamsal", value: scoreBreakdown.semantic_bonus }]
          : []),
      ]
    : [];

  return (
    <Card
      title="Uygunluk Sonucu"
      titleAddon={
        outdated && score != null ? (
          <StaleWarningIcon message="Eşleşme skoru eski. İlan yeniden analiz edildi; Eşleşmeyi Güncelle ile yenilemenizi öneririz." />
        ) : undefined
      }
      className="shadow-card-hover"
      action={
        !loading && score != null ? (
          <Button
            type="button"
            variant="outline"
            onClick={onRematch}
            loading={rematching}
            className={cn(compact && "px-2")}
            aria-label="Eşleşmeyi Güncelle"
          >
            <RefreshCw className="h-4 w-4" />
            {!compact && "Eşleşmeyi Güncelle"}
          </Button>
        ) : undefined
      }
    >
      {loading && (
        <div className="space-y-4">
          <div
            role="status"
            aria-label="Eşleşme skoru yükleniyor"
            className="animate-pulse space-y-3"
          >
            <div className="h-5 w-1/3 rounded bg-surface-container-high" />
            <div className="h-36 rounded-xl bg-surface-container-low" />
          </div>
          <div
            role="status"
            aria-label="Beceri karşılaştırma tablosu yükleniyor"
            className="animate-pulse space-y-2"
          >
            <div className="h-10 rounded-xl bg-surface-container-low" />
            <div className="h-24 rounded-xl bg-surface-container-low" />
          </div>
        </div>
      )}
      <FormError message={error} />
      {!loading && score == null && (
        <div className="space-y-3 rounded-xl bg-surface-container-low p-4">
          <p className="text-body-sm text-on-surface-variant">
            Uygunluk skoru henüz hesaplanmadı.
          </p>
          <Button type="button" onClick={onCalculate} className="w-full">
            <Target className="h-4 w-4" />
            Uygunluğumu Hesapla
          </Button>
        </div>
      )}
      {!loading && score != null && (
        <>
          <FormError message={rematchError} />

          <div
            className={cn(
              "grid items-center gap-md",
              compact ? "grid-cols-1" : "grid-cols-1 lg:grid-cols-[160px_1fr] gap-lg"
            )}
          >
            <div className="flex justify-center">
              <ScoreGauge score={score} />
            </div>
            {breakdownItems.length > 0 && (
              <div
                className={cn(
                  "grid gap-sm",
                  compact ? "grid-cols-2" : "grid-cols-2 lg:grid-cols-4"
                )}
              >
                {breakdownItems.map((item) => (
                  <div
                    key={item.label}
                    className="rounded-xl bg-primary-fixed/10 p-3 text-center"
                  >
                    <p className="text-headline-sm font-semibold text-primary">
                      {Math.round(item.value * 10) / 10}
                    </p>
                    <p className="text-label-md text-on-surface-variant">{item.label}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="mt-5 border-t border-outline-variant pt-4">
            <div className={cn("mb-3 flex flex-col gap-2", !compact && "lg:mb-4 lg:flex-row lg:gap-3")}>
              <label className="relative flex-1">
                <span className="sr-only">Beceri ara</span>
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-on-surface-variant" />
                <input
                  type="search"
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="Beceri ara..."
                  className="input-field pl-9"
                />
              </label>
              <select
                aria-label="Duruma göre filtrele"
                value={statusFilter}
                onChange={(event) => setStatusFilter(event.target.value as SkillStatusFilter)}
                className={cn("input-field", !compact && "lg:w-44")}
              >
                <option value="all">Tüm durumlar</option>
                <option value="matched">Eşleşen</option>
                <option value="missing">Eksik</option>
              </select>
              <select
                aria-label="Kategoriye göre filtrele"
                value={categoryFilter}
                onChange={(event) =>
                  setCategoryFilter(event.target.value as SkillCategoryFilter)
                }
                className={cn("input-field", !compact && "lg:w-48")}
              >
                <option value="all">Tüm kategoriler</option>
                <option value="required">Zorunlu</option>
                <option value="nice">Tercih sebebi</option>
              </select>
            </div>

            {!compact && (
              <div className="hidden overflow-x-auto rounded-xl border border-outline-variant md:block">
                <table className="w-full text-left text-body-sm">
                  <thead className="bg-surface-container-low text-label-md text-on-surface-variant">
                    <tr>
                      <th className="px-4 py-3 font-semibold">Beceri</th>
                      <th className="px-4 py-3 font-semibold">Durum</th>
                      <th className="px-4 py-3 font-semibold">Kategori</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-outline-variant">
                    {filteredRows.map((row) => (
                      <tr key={`${row.category}-${row.skill}`}>
                        <td className="px-4 py-3 font-medium">{row.skill}</td>
                        <td className="px-4 py-3">
                          <Status matched={row.matched} />
                        </td>
                        <td className="px-4 py-3">
                          {row.category === "required" ? "Zorunlu" : "Tercih sebebi"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            <div className={cn("space-y-2", !compact && "md:hidden")}>
              {filteredRows.map((row) => (
                <div
                  key={`${row.category}-${row.skill}`}
                  className="rounded-xl border border-outline-variant p-3"
                >
                  <div className="flex items-start justify-between gap-3">
                    <p className="font-semibold text-on-surface text-body-sm break-words">
                      {row.skill}
                    </p>
                    <Status matched={row.matched} compact={compact} />
                  </div>
                  <p className="mt-1.5 text-label-md text-on-surface-variant">
                    {row.category === "required" ? "Zorunlu" : "Tercih sebebi"}
                  </p>
                </div>
              ))}
            </div>
            {filteredRows.length === 0 && (
              <p className="py-6 text-center text-body-sm text-on-surface-variant">
                Filtrelere uygun beceri bulunamadı.
              </p>
            )}
          </div>
        </>
      )}
    </Card>
  );
}

function Status({ matched, compact = false }: { matched: boolean; compact?: boolean }) {
  return matched ? (
    <span className="inline-flex shrink-0 items-center gap-1 text-green-700 text-label-md">
      <Check className="h-3.5 w-3.5" aria-hidden="true" />
      {compact ? "Var" : "Eşleşiyor"}
    </span>
  ) : (
    <span className="inline-flex shrink-0 items-center gap-1 text-red-700 text-label-md">
      <X className="h-3.5 w-3.5" aria-hidden="true" />
      Eksik
    </span>
  );
}
