import type { ReactNode } from "react";
import Link from "next/link";

import { AppShell } from "@/components/layout/app-shell";
import { requireAdminOrAuthor } from "@/lib/auth/session";

export default async function AdminLayout({ children }: { children: ReactNode }) {
  await requireAdminOrAuthor();

  return (
    <AppShell
      title=""
      nav={
        <Link href="/admin" className="text-sm text-muted-foreground hover:text-foreground">
          Админ
        </Link>
      }
    >
      {children}
    </AppShell>
  );
}
