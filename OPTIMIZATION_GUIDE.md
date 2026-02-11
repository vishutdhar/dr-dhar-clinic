# Optimization Guide

Documents all optimizations applied to dranilkumardhar.com.

## Current Lighthouse Scores (February 2026)

| Category | Score |
|----------|-------|
| SEO | 100/100 |
| Best Practices | 100/100 |
| Accessibility | 94/100 |
| Performance | 88/100 |

## Image Optimization

The doctor photo was the single biggest performance issue. Original file was a 2.16MB PNG saved with a `.jpg` extension.

| Variant | Dimensions | Size | Use |
|---------|-----------|------|-----|
| doctor-photo.webp | 600x900 | 32KB | Hero and About (modern browsers) |
| doctor-photo.jpg | 600x900 | 57KB | Hero and About (fallback) |
| doctor-photo-400w.webp | 400x600 | 19KB | Mobile (modern browsers) |
| doctor-photo-400w.jpg | 400x600 | 31KB | Mobile (fallback) |
| og-image.jpg | 1200x630 | 67KB | Social sharing previews |

**Total reduction:** 2.16MB to 32KB (98.5% reduction for primary image)

Images use `<picture>` elements with WebP/JPEG srcset. Hero image has `fetchpriority="high"`, About image has `loading="lazy"`.

## SEO Optimizations

### Schema Markup (3 JSON-LD blocks)
1. **MedicalClinic + Physician** - clinic details, address (NAP), hours, doctor credentials (MBBS/MD/DNB), registration numbers, geo coordinates
2. **MedicalBusiness** - service catalog with 6 services and pricing
3. **FAQPage** - 6 frequently asked questions

### Meta Tags
- Open Graph (title, description, image, URL, type, locale)
- Twitter Card (summary_large_image)
- Canonical URL
- Theme color (#0a0f1c)
- Language: en-IN

### Technical SEO Files
- `robots.txt` - allows all crawlers, references sitemap
- `sitemap.xml` - single URL entry for homepage
- `404.html` - branded error page with clinic contact info
- Favicons (ico, 32x32, 16x16, apple-touch-icon) - shown in Google search results

### Contact Obfuscation
Phone numbers, email, and registration numbers are injected via JavaScript using character codes. This prevents bot scraping while keeping the data readable for users and in schema markup for Google.

## Performance Optimizations

### Caching (vercel.json)
- Images (.jpg, .webp, .png, .ico): 1 year, immutable
- CSS: 1 week

### Layout Shift Prevention
- All images have explicit `width` and `height` attributes
- Fonts preconnected to Google Fonts

### Remaining Performance Notes
- **FCP/LCP: 2.8s** - caused by render-blocking Google Fonts CSS (~2s). Acceptable tradeoff for typography quality.
- **Speed Index: 4.6s** - primarily font loading on slower connections.

## Accessibility

- Skip-to-content link (hidden with `transform: translateY(-100%)`)
- ARIA labels on all interactive elements
- Keyboard navigation support
- Semantic HTML5 landmarks
- FAQ uses native `<details>/<summary>` (built-in accessibility)

### Known Issues
- Minor contrast ratio issue on subtitle text in dark hero section
- Heading order not perfectly sequential in footer (h4 without preceding h3)

## CSS Architecture

Sections use distinct visual treatments to avoid monotony:
- **Hero:** Dark background with dot texture
- **Services:** Cool gradient (blue-grey to white) with dot texture and elevated cards
- **About:** White background
- **Google Reviews:** Blue tint (`--accent-soft`)
- **Clinic Info:** Warm grey (`--bg-warm`)
- **Booking:** Dark theme (matches hero)
- **Location/Contact:** White with radial blue glow (contact has `overflow: hidden`)
- **FAQ:** Warm grey with white cards
- **Footer:** Dark theme
