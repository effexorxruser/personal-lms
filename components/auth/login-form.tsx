"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, useState } from "react";

import { authClient } from "@/lib/auth/client";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setError(null);

    let result;
    try {
      result = await authClient.signIn.email({
        email,
        password,
      });
    } catch {
      setPending(false);
      setError("Не удалось связаться с сервером. Проверьте, что приложение и БД запущены.");
      return;
    }

    setPending(false);

    if (result.error) {
      setError(result.error.message ?? "Не удалось войти");
      return;
    }

    const next = searchParams.get("next") ?? "/dashboard";
    router.push(next);
    router.refresh();
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>Вход</CardTitle>
        <CardDescription>
          Вход только для приглашённых пользователей. Регистрация отключена.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form className="space-y-4" onSubmit={onSubmit}>
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Пароль</Label>
            <Input
              id="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </div>
          {error ? (
            <p className="text-sm text-red-600" role="alert">
              {error}
            </p>
          ) : null}
          <Button className="w-full" type="submit" disabled={pending}>
            {pending ? "Входим…" : "Войти"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
