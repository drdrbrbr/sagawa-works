export const config = {
  matcher: ["/:path*"],
};

export default function middleware(req) {
  const basicAuth = req.headers.get("authorization");

  if (basicAuth) {
    const [scheme, encoded] = basicAuth.split(" ");
    if (scheme === "Basic") {
      const decoded = atob(encoded);
      const [user, password] = decoded.split(":");
      if (user === "portfolio" && password === "tyuhbnm") {
        return;
      }
    }
  }

  return new Response("Unauthorized", {
    status: 401,
    headers: {
      "WWW-Authenticate": 'Basic realm="Secure Area"',
    },
  });
}
