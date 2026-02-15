# Dr. Anil Kumar Dhar's Clinic Website

A modern, responsive, single-page website for Dr. Anil Kumar Dhar's medical clinic in Jammu. Built with performance, SEO, and user experience at its core.

**Live:** [https://dranilkumardhar.com](https://dranilkumardhar.com)

## Technology Stack

- **HTML5** - Semantic markup with structured data (JSON-LD)
- **CSS3** - CSS Grid, Flexbox, custom properties, animations
- **Vanilla JavaScript** - No frameworks or dependencies
- **Vercel** - Hosting with automatic deployments from GitHub
- **Zero Build Process** - No compilation or bundling required

## Project Structure

```
dr-dhar-clinic/
├── index.html                  # Main website
├── styles.css                  # All styling
├── 404.html                    # Custom error page
├── robots.txt                  # Search engine crawl directives
├── sitemap.xml                 # Page index for search engines
├── vercel.json                 # Cache headers configuration
├── doctor-photo.jpg            # Hero image (57KB, 600x900)
├── doctor-photo.webp           # WebP variant (32KB, 600x900)
├── doctor-photo-400w.jpg       # Mobile variant (31KB, 400x600)
├── doctor-photo-400w.webp      # Mobile WebP variant (19KB, 400x600)
├── og-image.jpg                # Social sharing image (67KB, 1200x630)
├── favicon.ico                 # Browser tab icon
├── favicon-32x32.png           # High-res favicon
├── favicon-16x16.png           # Standard favicon
├── apple-touch-icon.png        # iOS home screen icon
├── README.md                   # This file
├── test-status.html            # Clinic status debugger (dev only)
├── verify-schedule.html        # Schedule verification (dev only)
├── comprehensive-test-report.html  # Test report (dev only)
└── mobile-test.html            # Mobile testing page (dev only)
```

## Features

### Real-time Clinic Status
- Live open/closed indicator in the header using IST timezone
- Shows next opening time when closed
- Auto-refreshes every 60 seconds

### SEO (Lighthouse Score: 100/100)
- 3 JSON-LD schema blocks: MedicalClinic + Physician, MedicalBusiness with services, FAQPage
- Complete meta tags: Open Graph, Twitter Card, canonical URL, theme-color
- robots.txt and sitemap.xml
- Optimized title, description, and heading hierarchy
- `lang="en-IN"` for regional targeting

### Performance (Lighthouse Score: 88/100)
- Doctor photo optimized from 2.16MB to 32KB WebP (98.5% reduction)
- Responsive `<picture>` elements with WebP/JPEG srcset and mobile variants
- `fetchpriority="high"` on hero image, `loading="lazy"` on below-fold images
- Vercel cache headers: 1 year for images, 1 week for CSS
- Image `width`/`height` attributes to prevent layout shift

### Accessibility (Lighthouse Score: 94/100)
- Skip-to-content link (hidden with `translateY(-100%)`, visible on focus)
- Proper ARIA labels, roles, and landmarks
- Keyboard navigation support
- Semantic HTML5 structure

### Contact & Booking
- 3 booking channels: Phone call, WhatsApp (pre-filled message), SMS
- Contact info (phone, email, registration numbers) obfuscated from bot scraping using JavaScript char codes
- Schema markup left readable for Google crawlers

### Visual Design
- Dark hero and booking sections for visual anchoring
- Gradient backgrounds and dot textures on light sections
- Subtle card elevation with hover states
- FAQ section using native `<details>/<summary>` elements

## Clinic Information

**Address:** House No. 48, Bhagwati Nagar, Canal Road, Jammu, J&K - 180016
**Phone:** 94191 90388
**Email:** anil7dhar@gmail.com

### Hours
| Day | Hours |
|-----|-------|
| Monday | 9 AM - 1 PM, 4:30 - 7 PM |
| Tuesday | CLOSED |
| Wednesday - Saturday | 9 AM - 1 PM, 4:30 - 7 PM |
| Sunday | 9 AM - 3 PM |

## Deployment

The site auto-deploys from the `main` branch on GitHub to Vercel.

1. Push changes to `main`
2. Vercel builds and deploys automatically
3. Live at dranilkumardhar.com within ~1 minute

### Local Development
1. Clone the repository
2. Open `index.html` in a browser (or use Live Server in VS Code)
3. No build step or server required

## Off-Page SEO Status (Updated: 2026-02-12)

- [x] Google Search Console - verified (HTML tag method), sitemap submitted (2026-02-12)
- [ ] Google Analytics 4 - property needs to be created, then tracking script added to index.html
- [ ] Google Business Profile - needs business owner's consent and verification (email sent 2026-02-12)
- [ ] Directory listings (Practo, Lybrate, JustDial) - needs business owner's consent
- [ ] Google review strategy - current rating is 3.1 stars / 165 reviews, needs improvement to 4.0+

## DNS & Hosting Status (Updated: 2026-02-12)

- **Registrar:** Hostinger
- **Nameservers:** Changed to `ns1.vercel-dns.com` / `ns2.vercel-dns.com` (2026-02-12, propagating)
- **Hosting:** Vercel (auto-deploy from GitHub main branch)
- **Vercel Authentication:** Disabled (re-enable with Standard Protection after DNS propagation completes)
- **SSL:** Managed by Vercel

## License

(c) 2026 Dr. Anil Kumar Dhar's Clinic. All rights reserved.

---

Built by Vishut Dhar
