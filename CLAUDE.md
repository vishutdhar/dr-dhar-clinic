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

### Resume Here (Next Steps)
1. **Google Analytics 4** - User needs to create a GA4 property at analytics.google.com, get the Measurement ID (G-XXXXXX), then add the tracking script to index.html
2. **DNS propagation check** - Run `dig NS dranilkumardhar.com +short` to verify nameservers changed to vercel-dns.com. Once confirmed, re-enable Standard Protection on Vercel for dr-dhar-clinic
3. **Waiting on business owner (Dr. Dhar) response for:**
   - Google Business Profile setup (needs his consent + verification call to clinic)
   - Directory listings on Practo, Lybrate, JustDial (needs his consent)
   - Google review improvement strategy (3.1 stars -> target 4.0+)
4. **Future SEO improvements:**
   - Add dedicated pages per specialty for better keyword targeting
   - Add Google Analytics to understand visitor behavior
   - Consider adding social media profiles to schema (sameAs) if any exist
