import { getSessionCookie } from "better-auth/cookies";
import { NextRequest, NextResponse } from "next/server";

const learnerPaths = ["/dashboard", "/courses", "/learn", "/weekly-review"];
const adminPaths = ["/admin"];

function isPathMatch(pathname: string, prefixes: string[]) {
  return prefixes.some(
    (prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`),
  );
}

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const hasSession = Boolean(getSessionCookie(request));

  if (pathname === "/login") {
    return NextResponse.next();
  }

  const needsSession =
    isPathMatch(pathname, learnerPaths) || isPathMatch(pathname, adminPaths);

  if (!needsSession) {
    return NextResponse.next();
  }

  if (!hasSession) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/login",
    "/dashboard/:path*",
    "/courses/:path*",
    "/learn/:path*",
    "/weekly-review/:path*",
    "/admin/:path*",
  ],
};
