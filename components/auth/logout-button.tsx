"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { authClient } from "@/lib/auth/client";
import { Button } from "@/components/ui/button";

export function LogoutButton() {
  const router = useRouter();
  const [pending, setPending] = useState(false);

  async function onLogout() {
    setPending(true);
    await authClient.signOut();
    setPending(false);
    router.push("/login");
    router.refresh();
  }

  return (
    <Button variant="outline" onClick={onLogout} disabled={pending}>
      {pending ? "Выходим…" : "Выйти"}
    </Button>
  );
}
