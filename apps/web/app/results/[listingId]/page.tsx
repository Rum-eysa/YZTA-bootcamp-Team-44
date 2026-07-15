"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect } from "react";

/**
 * Eski sonuç sayfası — /listings/[listingId] bu sayfanın yaptığı her şeyi
 * (skor, CV, önyazı) DB'den okuyarak yapıyor; bu rota sessionStorage'a
 * dayanıyordu ve hiçbir yerden link verilmiyordu. Eski yer imleri
 * kırılmasın diye redirect olarak bırakıldı.
 */
export default function LegacyResultsRedirect() {
  const params = useParams();
  const router = useRouter();

  useEffect(() => {
    router.replace(`/listings/${params.listingId}`);
  }, [params.listingId, router]);

  return null;
}
