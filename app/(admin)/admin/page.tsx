import { requireAdminOrAuthor } from "@/lib/auth/session";

export default async function AdminPage() {
  const session = await requireAdminOrAuthor();

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold">Админ</h1>
      <p className="text-muted-foreground">
        Роль: {session.user.role}. Course Builder и управление пользователями — Phase 3–4.
      </p>
    </section>
  );
}
