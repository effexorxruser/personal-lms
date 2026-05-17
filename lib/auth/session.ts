import { headers } from "next/headers";
import { redirect } from "next/navigation";

import { auth, type Session, type User } from "@/lib/auth";

export async function getSession(): Promise<Session | null> {
  return auth.api.getSession({
    headers: await headers(),
  });
}

export async function requireSession(): Promise<Session> {
  const session = await getSession();
  if (!session) {
    redirect("/login");
  }
  return session;
}

export type AppRole = User["role"];

export async function requireRole(...roles: AppRole[]): Promise<Session> {
  const session = await requireSession();
  if (!roles.includes(session.user.role)) {
    redirect("/dashboard");
  }
  return session;
}

export async function requireAdmin(): Promise<Session> {
  return requireRole("admin");
}

export async function requireAdminOrAuthor(): Promise<Session> {
  return requireRole("admin", "author");
}
