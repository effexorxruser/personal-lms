import type { ReactNode } from "react";
import Link from "next/link";

import { LogoutButton } from "@/components/auth/logout-button";

type AppShellProps = {
  children: ReactNode;
  title: string;
  nav?: ReactNode;
};

export function AppShell({ children, title, nav }: AppShellProps) {
  return (
    <div className="min-h-screen">
      <header className="border-b">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-6 py-4">
          <div className="flex items-center gap-6">
            <Link href="/dashboard" className="font-semibold">
              personal-lms
            </Link>
            {nav}
          </div>
          <LogoutButton />
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-6 py-8">
        {title ? <h1 className="mb-6 text-2xl font-semibold">{title}</h1> : null}
        {children}
      </main>
    </div>
  );
}
