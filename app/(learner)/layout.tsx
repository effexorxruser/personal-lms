import type { ReactNode } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { requireSession } from "@/lib/auth/session";

export default async function LearnerLayout({ children }: { children: ReactNode }) {
  await requireSession();

  return <AppShell title="">{children}</AppShell>;
}
