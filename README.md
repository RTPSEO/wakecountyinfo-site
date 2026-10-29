# wakecountyinfo.com — static site on Cloudflare Workers

**Deploys automatically:** every push to `main` on GitHub (RTPSEO/wakecountyinfo-site) is deployed by Cloudflare Workers Builds (Worker `wakecountyinfo-site`).

Edit pages in `build/content/`, run `python3 build/build.py`, commit everything (including `public/`).

## 1. Dev site (now)
Live on the workers.dev URL only. Search engines are told not to index it.

## 2. Move wakecountyinfo.com to Cloudflare
1. Cloudflare dashboard > Add a domain > wakecountyinfo.com > Free plan.
2. GoDaddy > wakecountyinfo.com > DNS > DNSSEC: turn it off if it is on.
3. GoDaddy > Nameservers > "I'll use my own nameservers" > paste the two Cloudflare nameservers.
4. Wait for Cloudflare to show the domain as Active (minutes to a day).

## 3. Go live
Uncomment the `routes` block in `wrangler.jsonc` and push to `main`.
Remove `noindex: 1` from pages that should be indexed, rebuild, push.
Then submit https://wakecountyinfo.com/sitemap.xml in Google Search Console.
