"use client";

import { AtsScoreGauge } from "./AtsScoreGauge";

interface AtsHeroProps {
  onCtaClick: () => void;
}

export function AtsHero({ onCtaClick }: AtsHeroProps) {
  return (
    <section className="grid items-center gap-10 lg:grid-cols-2 lg:gap-12">
      <div className="max-w-xl">
        <h1 className="text-headline-lg md:text-[44px] md:leading-[52px] font-bold text-on-surface">
          CV&rsquo;n ATS ile Uyumlu Mu?{" "}
          <span className="text-primary">Hemen Öğren</span>
        </h1>
        <p className="mt-4 text-body-lg text-on-surface-variant">
          CareerTrack ile ATS uyumluluğunu öğren, CV&rsquo;ni güçlendir ve işe alım
          sürecinde öne çık.
        </p>
        <button
          type="button"
          onClick={onCtaClick}
          className="btn-primary mt-8 px-8 py-3 text-lg"
        >
          CV&rsquo;nin ATS skorunu öğren
        </button>
      </div>

      <div className="relative mx-auto w-full max-w-md lg:max-w-none">
        <div
          aria-hidden
          className="absolute -inset-4 rounded-[2rem] bg-gradient-to-br from-primary-container/25 via-secondary-container/20 to-transparent blur-2xl"
        />
        <div className="relative grid gap-4 sm:grid-cols-[1fr_1.1fr] items-end">
          <div className="card !p-4 shadow-lg rotate-[-2deg]">
            <div className="h-2 w-16 rounded bg-primary/30 mb-3" />
            <p className="text-sm font-bold text-on-surface">Selin Aksoy</p>
            <p className="text-xs text-on-surface-variant">Mühendislik Öğrencisi</p>
            <div className="mt-4 space-y-2">
              <div className="h-2 rounded bg-surface-container-high w-full" />
              <div className="h-2 rounded bg-surface-container-high w-5/6" />
              <div className="h-2 rounded bg-surface-container-high w-4/5" />
              <div className="mt-3 h-2 rounded bg-primary-container/50 w-2/3" />
              <div className="h-2 rounded bg-surface-container-high w-3/4" />
            </div>
            <div className="mt-4 flex gap-2">
              <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-orange-100 text-xs font-bold text-orange-700">
                75
              </span>
              <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-red-100 text-xs font-bold text-red-700">
                50
              </span>
            </div>
          </div>

          <div className="card !p-5 shadow-xl">
            <p className="text-sm font-semibold text-on-surface mb-3">ATS CV Skorun</p>
            <div className="flex items-center gap-4">
              <AtsScoreGauge score={100} label="" size="md" />
              <div className="space-y-2 text-sm flex-1">
                {[
                  ["Tasarım", 100],
                  ["Düzen", 100],
                  ["İçerik", 100],
                ].map(([label, score]) => (
                  <div key={String(label)}>
                    <div className="flex justify-between text-xs text-on-surface-variant mb-1">
                      <span>{label}</span>
                      <span className="font-semibold text-primary">{score}</span>
                    </div>
                    <div className="h-1.5 rounded-full bg-surface-container-high overflow-hidden">
                      <div className="h-full w-full rounded-full bg-primary-container" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
