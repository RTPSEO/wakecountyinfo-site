# wakecountyinfo.com

Static site: data studies about Wake County, NC (real estate first; other topics later). Cloudflare Worker `wakecountyinfo-site`. Same stack as marketing-raleigh.com (RTPSEO/marketing-raleigh-site).

## How it deploys
- Cloudflare Workers Builds is connected to this repo. Every push to `main` runs `npx wrangler deploy`.
- DEV: only the workers.dev URL is live, and it is noindexed (X-Robots-Tag in `src/worker.js`). The home page also has `noindex: 1` until launch.
- Domain: registered at GoDaddy. Go-live = add to Cloudflare (Free plan), DNSSEC off at GoDaddy, switch nameservers, wait for Active, then uncomment `routes` in `wrangler.jsonc`. See README.

## Layout
- `build/content/`: page sources. Each file = `key: value` header, `---`, body HTML. A `.js` file with the same name is inlined as the page script.
- `build/build.py`: builds `public/` (layout, nav, footer, JSON-LD, sitemap.xml, feed/rss.xml). Run `python3 build/build.py` after any content change and commit `public/` too. Workers Builds does not run the build.
- `public/`: the deployed site. Don't hand-edit generated HTML. `public/assets/site.css`, `_headers`, `_redirects`, `robots.txt`, `favicon.svg` are hand-maintained.
- `src/worker.js`: www → bare domain 301, noindex header on workers.dev. No forms yet.
- Page kinds: `home`, `page`, `study` (a data study: needs `date`, `file_no`, `topic`, `excerpt`), `plain`. `{{STUDIES}}` / `{{RECENT_STUDIES}}` insert study cards.

## Rules
- Design: "paperwork" theme: off-white paper, manila folders, form rows, rubber-stamp labels. Courier Prime headings, Special Elite for stamps, Source Serif 4 body.
- Data: free public Wake County data first (Tax Administration real estate files, qualified sales, building permits). Every study lists its sources, pull date and method. Check licensing before using any Triangle MLS data.
- Never say or imply the site is affiliated with Wake County Government.
- Never remove a URL without adding a 301 in `public/_redirects`.
- Owner: Rob Delory (not technical). Short answers, one action per line.
