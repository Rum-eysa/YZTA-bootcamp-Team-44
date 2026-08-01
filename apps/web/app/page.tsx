import { AppLayout } from "@/components/layout/AppLayout";
import { LandingHome } from "@/components/landing/LandingHome";

export default function Home() {
  return (
    <AppLayout guard={false}>
      <LandingHome />
    </AppLayout>
  );
}
