import { betterAuth } from "better-auth";
import { prismaAdapter } from "better-auth/adapters/prisma";
import { APIError, createAuthMiddleware } from "better-auth/api";

import { prisma } from "@/lib/db/prisma";

const devTrustedOrigins =
  process.env.NODE_ENV === "development"
    ? ["http://localhost:3000", "http://127.0.0.1:3000"]
    : [];

export const auth = betterAuth({
  database: prismaAdapter(prisma, {
    provider: "postgresql",
  }),
  trustedOrigins: [
    process.env.BETTER_AUTH_URL,
    process.env.NEXT_PUBLIC_BETTER_AUTH_URL,
    ...devTrustedOrigins,
  ].filter((origin): origin is string => Boolean(origin)),
  emailAndPassword: {
    enabled: true,
    disableSignUp: true,
  },
  user: {
    additionalFields: {
      role: {
        type: ["admin", "author", "learner"] as const,
        required: true,
        defaultValue: "learner",
        input: false,
      },
      isActive: {
        type: "boolean",
        required: true,
        defaultValue: true,
        input: false,
      },
    },
  },
  secret: process.env.BETTER_AUTH_SECRET,
  baseURL: process.env.BETTER_AUTH_URL,
  hooks: {
    before: createAuthMiddleware(async (ctx) => {
      if (ctx.path !== "/sign-in/email") {
        return;
      }

      const email = ctx.body?.email;
      if (typeof email !== "string") {
        return;
      }

      const user = await prisma.user.findUnique({
        where: { email },
        select: { isActive: true },
      });

      if (user && !user.isActive) {
        throw new APIError("FORBIDDEN", {
          message: "Аккаунт деактивирован. Обратитесь к администратору.",
        });
      }
    }),
  },
});

export type Session = typeof auth.$Infer.Session;
export type User = Session["user"];
