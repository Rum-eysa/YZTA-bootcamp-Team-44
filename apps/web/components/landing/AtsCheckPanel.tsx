"use client";

import Link from "next/link";
import { useCallback, useRef, useState } from "react";
import { FileUp, Loader2, Sparkles } from "lucide-react";
import { checkAtsCompatibility } from "@/lib/api/ats-check";
import { getApiErrorMessage } from "@/lib/apiErrors";
import {
  ATS_CATEGORY_LABELS,
  ATS_RATING_LABELS,
  atsScoreColor,
} from "@/lib/atsRating";
import type { AtsCategoryKey, AtsCheckResponse } from "@/types/atsCheck";
import { AtsScoreGauge } from "./AtsScoreGauge";

const CATEGORY_ORDER: AtsCategoryKey[] = ["tasarim", "duzen", "icerik"];

export function AtsCheckPanel() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [limitReached, setLimitReached] = useState(false);
  const [result, setResult] = useState<AtsCheckResponse | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);

  const runCheck = useCallback(async (file: File) => {
    setError(null);
    setLimitReached(false);
    setResult(null);
    setFileName(file.name);
    setLoading(true);
    try {
      const data = await checkAtsCompatibility(file);
      setResult(data);
    } catch (err) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      if (status === 429) {
        setLimitReached(true);
        setError(
          "Bugünkü ücretsiz ATS kontrol hakkınızı kullandınız. Yarın tekrar deneyin veya kayıt olarak her ilana özel ATS CV üretin."
        );
      } else {
        setError(getApiErrorMessage(err, "ATS analizi başarısız oldu"));
      }
    } finally {
      setLoading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }, []);

  const onFile = (file: File | undefined | null) => {
    if (!file || loading) return;
    void runCheck(file);
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap justify-end">
        <span className="inline-flex items-center gap-1.5 text-body-sm font-semibold text-primary bg-primary-container/40 px-3 py-1 rounded-full">
          <Sparkles className="w-4 h-4" />
          Günlük 1 hak
        </span>
      </div>

      <div
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            inputRef.current?.click();
          }
        }}
        onClick={() => !loading && inputRef.current?.click()}
        onDragEnter={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={(e) => {
          e.preventDefault();
          setDragging(false);
        }}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          onFile(e.dataTransfer.files?.[0]);
        }}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-10 transition-colors ${
          dragging
            ? "border-primary bg-primary-container/20"
            : "border-outline-variant bg-surface-container-low/60 hover:border-primary/60"
        } ${loading ? "pointer-events-none opacity-70" : ""}`}
      >
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf,.pdf"
          className="hidden"
          onChange={(e) => onFile(e.target.files?.[0])}
        />
        {loading ? (
          <>
            <Loader2 className="h-10 w-10 animate-spin text-primary" />
            <p className="mt-3 text-body-sm font-semibold text-on-surface">
              CV analiz ediliyor…
            </p>
            {fileName && (
              <p className="mt-1 text-label-md text-on-surface-variant">{fileName}</p>
            )}
          </>
        ) : (
          <>
            <FileUp className="h-10 w-10 text-primary" />
            <p className="mt-3 text-body-sm font-semibold text-on-surface">
              PDF sürükleyin veya seçin
            </p>
            <p className="mt-1 text-label-md text-on-surface-variant">
              Maksimum 5 MB · Dosyanız saklanmaz
            </p>
          </>
        )}
      </div>

      {error && (
        <div
          className={`rounded-lg px-4 py-3 text-body-sm ${
            limitReached
              ? "bg-secondary-container/50 text-on-secondary-container"
              : "bg-error-container text-on-error-container"
          }`}
        >
          <p>{error}</p>
          {limitReached && (
            <Link
              href="/register"
              className="mt-2 inline-block font-semibold text-primary underline"
            >
              Kayıt ol →
            </Link>
          )}
        </div>
      )}

      {result && (
        <div className="space-y-6 pt-2">
          <div className="flex flex-col items-center gap-6 sm:flex-row sm:items-start">
            <AtsScoreGauge score={result.overall_score} />
            <div className="flex-1 text-center sm:text-left">
              <p className="text-title-md font-bold text-on-surface">
                Genel: {ATS_RATING_LABELS[result.overall_rating]}
              </p>
              {result.summary && (
                <p className="mt-2 text-body-sm text-on-surface-variant">{result.summary}</p>
              )}
              <Link
                href="/register"
                className="btn-primary mt-4 inline-flex px-5 py-2 text-sm"
              >
                Her ilana özel ATS CV üretmek için kayıt ol
              </Link>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            {CATEGORY_ORDER.map((key) => {
              const cat = result.categories[key];
              if (!cat) return null;
              const color = atsScoreColor(cat.score);
              return (
                <div
                  key={key}
                  className="rounded-xl border border-outline-variant bg-surface-bright p-4"
                >
                  <div className="flex items-center justify-between gap-2">
                    <h3 className="text-sm font-semibold text-on-surface">
                      {ATS_CATEGORY_LABELS[key]}
                    </h3>
                    <span
                      className="rounded-full px-2 py-0.5 text-xs font-semibold text-white"
                      style={{ backgroundColor: color }}
                    >
                      {ATS_RATING_LABELS[cat.rating]}
                    </span>
                  </div>
                  <p className="mt-2 text-2xl font-bold" style={{ color }}>
                    {cat.score}
                  </p>
                  <div className="mt-2 h-2 overflow-hidden rounded-full bg-surface-container-high">
                    <div
                      className="h-full rounded-full transition-all"
                      style={{ width: `${cat.score}%`, backgroundColor: color }}
                    />
                  </div>
                  {cat.feedback && (
                    <p className="mt-3 text-label-md text-on-surface-variant">
                      {cat.feedback}
                    </p>
                  )}
                </div>
              );
            })}
          </div>

          {result.suggestions.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-on-surface">Öneriler</h3>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-body-sm text-on-surface-variant">
                {result.suggestions.map((s) => (
                  <li key={s}>{s}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
