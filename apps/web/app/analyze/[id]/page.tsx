"use client";

import { AppHeader } from "@/components/layout/AppHeader";
import { AuthGuard } from "@/components/auth/AuthGuard";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { getAnalysisResult } from "@/lib/api/analysis";
import type { AnalyzeResponse } from "@/types/analysis";
import { ArrowLeft, CheckCircle2 } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

function AnalyzeResultContent() {
  const params = useParams();
  const listingId = params.id as string;
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const data = getAnalysisResult(listingId);
    setResult(data);
    setLoading(false);
  }, [listingId]);

  if (loading) {
    return (
      <div className="py-3xl">
        <Spinner label="Sonuçlar yükleniyor..." />
      </div>
    );
  }

  if (!result) {
    return (
      <main className="max-w-[1024px] mx-auto px-margin-mobile md:px-lg py-xl text-center">
        <h1 className="text-headline-lg-mobile font-semibold mb-2">Sonuç bulunamadı</h1>
        <p className="text-body-sm text-on-surface-variant mb-6">
          Analiz sonucu oturumda bulunamadı. Lütfen yeni bir analiz başlatın.
        </p>
        <Link href="/apply">
          <Button>Yeni Analiz Başlat</Button>
        </Link>
      </main>
    );
  }

  const confidencePercent = Math.round(result.confidence * 100);

  return (
    <main className="max-w-[1024px] mx-auto px-margin-mobile md:px-lg py-lg md:py-xl space-y-lg">
      <div className="flex items-center gap-2 text-primary">
        <CheckCircle2 className="w-5 h-5" />
        <span className="text-body-sm font-semibold">Analiz tamamlandı</span>
      </div>

      <Card>
        <h1 className="text-headline-lg-mobile md:text-headline-lg font-semibold text-on-surface mb-2">
          {result.position_title || "Pozisyon"}
        </h1>
        <div className="flex flex-wrap gap-2 mb-4">
          <span className="bg-primary-fixed/20 text-primary px-3 py-1 rounded-full text-label-md capitalize">
            {result.seniority || "Belirsiz"}
          </span>
          <span className="bg-secondary-container text-on-secondary-container px-3 py-1 rounded-full text-label-md">
            Güven: %{confidencePercent}
          </span>
        </div>
        <p className="text-body-sm text-on-surface-variant">İlan ID: {result.listing_id}</p>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-lg">
        <Card title="Zorunlu Beceriler">
          <div className="flex flex-wrap gap-2">
            {result.required_skills.length > 0 ? (
              result.required_skills.map((skill) => (
                <span
                  key={skill}
                  className="bg-primary-fixed/20 text-primary px-2 py-1 rounded font-label-md"
                >
                  {skill}
                </span>
              ))
            ) : (
              <p className="text-body-sm text-on-surface-variant">Belirlenemedi</p>
            )}
          </div>
        </Card>

        <Card title="Tercih Edilen Beceriler">
          <div className="flex flex-wrap gap-2">
            {result.nice_to_have.length > 0 ? (
              result.nice_to_have.map((skill) => (
                <span
                  key={skill}
                  className="bg-secondary-container text-on-secondary-container px-2 py-1 rounded font-label-md"
                >
                  {skill}
                </span>
              ))
            ) : (
              <p className="text-body-sm text-on-surface-variant">Belirlenemedi</p>
            )}
          </div>
        </Card>
      </div>

      <div className="flex gap-3">
        <Link href="/apply">
          <Button variant="outline">
            <ArrowLeft className="w-4 h-4" />
            Yeni Analiz
          </Button>
        </Link>
        <Link href="/profile">
          <Button>Profile Git</Button>
        </Link>
      </div>
    </main>
  );
}

export default function AnalyzeResultPage() {
  return (
    <div className="min-h-screen bg-surface-bright">
      <AppHeader />
      <AuthGuard>
        <AnalyzeResultContent />
      </AuthGuard>
    </div>
  );
}
