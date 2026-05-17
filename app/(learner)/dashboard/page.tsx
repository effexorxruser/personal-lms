import { requireSession } from "@/lib/auth/session";

export default async function DashboardPage() {
  const session = await requireSession();

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold">Дашборд</h1>
      <p className="text-muted-foreground">
        Привет, {session.user.name}. Phase 1 foundation готов — каталог курсов появится в
        Phase 2.
      </p>
    </section>
  );
}
