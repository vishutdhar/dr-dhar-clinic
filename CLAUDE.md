## Maps
- Apple maps for IOS, Google maps for android

## No Workarounds Rule
- No workarounds, only long-term reliable solutions
- Understand the system properly before attempting fixes
- When something isn't working, stop and understand WHY before trying quick fixes

## Session Log (2026-02-12)

### Completed
1. Removed "Rate Us on Google" section (business owner request)
   - Removed HTML block from index.html
   - Removed all .google-reviews CSS from styles.css
   - Changed .clinic-info background from --bg-warm to --bg (white) to maintain visual rhythm
2. Google Search Console - verified via HTML tag, sitemap submitted
3. SEO audit and fixes:
   - Removed fake aggregateRating (was 5 stars/100 reviews, actual is 3.1/165)
   - Removed empty sameAs array
   - Added paymentAccepted to schema
   - Updated sitemap lastmod date
4. DNS: Changed nameservers to Vercel for all 3 domains (propagating):
   - dranilkumardhar.com (Hostinger -> vercel-dns.com)
   - vishutdhar.com (Hostinger -> vercel-dns.com)
   - mydharmapath.com (Porkbun -> vercel-dns.com)
5. Vercel Authentication: Disabled on dr-dhar-clinic (re-enable Standard Protection after DNS propagates)
6. Vercel Authentication: Enabled Standard Protection on dr-dhar-prescription (private tool)

### Scope Decision (2026-07-05, FINAL)
**Dr. Dhar DECLINED all off-page work: Google Business Profile, directory listings (Practo, Lybrate, JustDial), and the Google review strategy. Do NOT propose these again.** This site's scope is on-site SEO optimization only.

### Resume Here (Next Steps)
1. **On-site SEO only** - technical SEO, on-page content/keyword optimization, structured data, Search Console monitoring
2. **Future on-site SEO improvements:**
   - Add dedicated pages per specialty for better keyword targeting
   - Consider adding social media profiles to schema (sameAs) if any exist
