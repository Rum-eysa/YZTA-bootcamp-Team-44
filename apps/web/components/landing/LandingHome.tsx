"use client";

import Link from "next/link";
import { useState } from "react";
import { Modal } from "@/components/ui/Modal";
import { AtsHero } from "./AtsHero";
import { AtsCheckPanel } from "./AtsCheckPanel";
import { ValueProps } from "./ValueProps";

export function LandingHome() {
  const [atsOpen, setAtsOpen] = useState(false);

  return (
    <div className="px-margin-mobile md:px-lg py-12 md:py-16">
      <AtsHero onCtaClick={() => setAtsOpen(true)} />
      <ValueProps />

      <div className="mt-10 text-center">
        <Link
          href="/kvkk"
          className="text-body-md font-semibold text-primary hover:underline"
        >
          KVKK Aydınlatma Metni'ni okuyun
        </Link>
      </div>

      <Modal
        open={atsOpen}
        onClose={() => setAtsOpen(false)}
        title="Ücretsiz ATS Uyumluluk Kontrolü"
        className="max-w-3xl"
      >
        <AtsCheckPanel />
      </Modal>
    </div>
  );
}
