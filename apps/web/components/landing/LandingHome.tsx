"use client";

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
