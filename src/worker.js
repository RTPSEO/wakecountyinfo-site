// wakecountyinfo.com: serves the static site in public/.
// - www.wakecountyinfo.com 301s to the bare domain (once routes are live).
// - The workers.dev preview gets X-Robots-Tag: noindex so it never shows up in search.
const PROD = "wakecountyinfo.com";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.hostname === "www." + PROD) {
      url.hostname = PROD;
      return Response.redirect(url.toString(), 301);
    }
    const res = await env.ASSETS.fetch(request);
    if (url.hostname.endsWith(".workers.dev")) {
      const r = new Response(res.body, res);
      r.headers.set("X-Robots-Tag", "noindex, nofollow");
      return r;
    }
    return res;
  },
};
