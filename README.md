# Dr. Anil Kumar Dhar's Clinic Website

A modern, responsive, single-page website for Dr. Anil Kumar Dhar's medical clinic in Jammu. Built with performance and user experience at its core, featuring real-time clinic status tracking, seamless appointment booking, and comprehensive medical service information.

🌐 **Live Demo**: [https://vishutdhar.github.io/dr-dhar-clinic/](https://vishutdhar.github.io/dr-dhar-clinic/)

## 🚀 Latest Updates (v2.0)

### Clinic Status Indicator Fix
- **Fixed timezone calculation**: Replaced manual UTC offset with native JavaScript timezone API for accurate IST (Indian Standard Time) display
- **Updated Sunday hours**: Corrected clinic hours from 9 AM - 1 PM to 9 AM - 3 PM to match actual operating hours
- **Enhanced reliability**: Status now updates correctly regardless of user's local timezone

## ✨ Key Features

### Real-time Clinic Status
- **Live Status Badge**: Displays "Open Now" with green indicator or "Closed" with red indicator
- **Smart Scheduling**: Automatically calculates open/closed status based on current IST time
- **Next Opening Time**: Shows when clinic will open next when currently closed
- **Auto-refresh**: Status updates every minute without page reload

### Responsive & Accessible Design
- **Mobile-First**: Optimized for all devices (phones, tablets, desktops)
- **Accessibility**: WCAG 2.1 AA compliant with:
  - Proper ARIA labels and roles
  - Keyboard navigation support
  - Skip-to-content link
  - High contrast ratios
  - Screen reader friendly

### Performance Optimized
- **Lightning Fast**: < 2 second load time on 3G networks
- **Optimized Images**: 84% size reduction (239KB → 38KB)
- **External CSS**: Browser caching for repeat visits
- **Lazy Loading**: Images load as needed
- **Minimal Dependencies**: Pure HTML/CSS/JS - no frameworks

### Contact & Booking Options
- **Multi-channel Booking**:
  - Direct phone call integration
  - WhatsApp with pre-filled appointment template
  - SMS booking option
  - Email support
- **One-Click Actions**: All contact methods work with single tap/click

### SEO & Marketing
- **Structured Data**: Schema.org medical clinic markup
- **Meta Tags**: Optimized for search engines and social media
- **Local SEO**: Google Maps integration and local business signals
- **Social Proof**: Google Reviews integration

## 🛠️ Technology Stack

- **HTML5**: Semantic markup with structured data
- **CSS3**: Modern styling with CSS Grid, Flexbox, and animations
- **Vanilla JavaScript**: No dependencies, pure ES6+
- **Progressive Enhancement**: Works without JavaScript
- **Zero Build Process**: No compilation or bundling required

## 📁 Project Structure

```
dr-dhar-clinic/
├── index.html                 # Main website (single-page application)
├── styles.css                 # External stylesheet for caching
├── doctor-photo.jpg           # Optimized hero image (38KB)
├── doctor-photo-original.jpg  # Original high-resolution backup
├── README.md                  # This file - project documentation
├── OPTIMIZATION_GUIDE.md      # Performance optimization details
├── HOSTINGER_DEPLOYMENT.md    # Hosting deployment guide
├── test-status.html           # Clinic status debugger (development)
└── verify-schedule.html       # Schedule verification tool (development)
```

## 🕐 Clinic Hours & Status Logic

### Operating Hours
**Monday, Wednesday-Saturday:**
- Morning: 9:00 AM - 1:00 PM
- Evening: 4:30 PM - 7:00 PM

**Tuesday:** CLOSED

**Sunday:** 9:00 AM - 3:00 PM

### Status Indicator Behavior
The clinic status indicator in the header shows:
- 🟢 **Green dot + "Open Now"**: During operating hours
- 🔴 **Red dot + "Closed • Opens at [time]"**: Outside operating hours
- Automatically detects Indian Standard Time (IST/UTC+5:30)
- Updates every 60 seconds without page refresh
- Shows next opening time when closed

## 📱 Features in Detail

### 1. Smart Header
- Sticky navigation that follows scroll
- Live clinic status with pulsing animation when open
- Responsive logo with medical caduceus symbol
- Backdrop blur effect for modern aesthetic

### 2. Hero Section
- Professional doctor photo with credentials
- Key achievements badges (30+ years, 500K+ patients)
- Smooth scroll indicator animation
- Responsive layout for all screen sizes

### 3. Quick Actions Bar
- Three primary CTAs: Book Appointment, WhatsApp, Call
- Color-coded buttons for visual hierarchy
- Pre-filled WhatsApp message template
- Direct tel: and sms: protocol integration

### 4. Services Grid
- Six core services with icons
- Hover effects and smooth transitions
- Pricing information where applicable
- Responsive grid layout (auto-fit)

### 5. Clinic Information
- Comprehensive timing table with visual highlighting
- Accepted payment methods
- Available facilities and amenities
- Special Sunday hours emphasis

### 6. Booking Section
- Multiple booking channels with priority indication
- Step-by-step booking preparation guide
- Visual hierarchy: Phone (primary) → WhatsApp → SMS
- Clear closed day warning (Tuesday)

### 7. Footer & Extras
- Back-to-top button with smooth scroll
- Contact information redundancy
- Google Maps integration
- Personal touch attribution

## 🚀 Deployment Guide

### Quick Deploy
1. Upload `index.html`, `styles.css`, and `doctor-photo.jpg` to your web server
2. No build process or compilation needed
3. Works on any static hosting (GitHub Pages, Netlify, Vercel, Hostinger)

### Hostinger Specific
See `HOSTINGER_DEPLOYMENT.md` for detailed Hostinger setup instructions.

### GitHub Pages
1. Push to repository
2. Enable Pages in Settings → Pages
3. Select main branch and root folder
4. Site will be live at `https://[username].github.io/[repo-name]/`

## 🌐 Browser Compatibility

| Browser | Version | Support |
|---------|---------|---------|
| Chrome | 90+ | ✅ Full |
| Firefox | 88+ | ✅ Full |
| Safari | 14+ | ✅ Full |
| Edge | 90+ | ✅ Full |
| Mobile Safari | iOS 14+ | ✅ Full |
| Chrome Mobile | Android 10+ | ✅ Full |
| Samsung Internet | 14+ | ✅ Full |

**Note**: Basic functionality works on all modern browsers. Advanced features (backdrop-filter, smooth scroll) gracefully degrade on older browsers.

## 🔧 Development

### Local Development
1. Clone the repository
2. Open `index.html` in a browser
3. No server required for basic testing
4. Use Live Server extension in VS Code for auto-reload

### Testing Tools
- `test-status.html`: Debug clinic status calculations
- `verify-schedule.html`: Verify schedule logic and time zones
- Browser DevTools for responsive testing

### Code Style
- Semantic HTML5 elements
- BEM-inspired CSS naming
- ES6+ JavaScript features
- Comprehensive code comments

## 📈 Performance Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| First Contentful Paint | < 1.5s | 0.8s |
| Largest Contentful Paint | < 2.5s | 1.2s |
| Time to Interactive | < 3.5s | 1.5s |
| Cumulative Layout Shift | < 0.1 | 0.02 |
| Total Page Size | < 500KB | 195KB |
| Lighthouse Score | > 90 | 96 |

## 🔒 Security & Privacy

- No cookies or tracking
- No external scripts or analytics
- All resources served over HTTPS
- No user data collection
- Contact links use native protocols

## 🤝 Contributing

This is a proprietary website for Dr. Anil Kumar Dhar's clinic. For updates or modifications, please contact the clinic administration.

## 📄 License

© 2024 Dr. Anil Kumar Dhar's Clinic. All rights reserved.

This website and its contents are proprietary to Dr. Anil Kumar Dhar's medical practice. Unauthorized copying, modification, or distribution is prohibited.

## 📞 Support

**For Medical Appointments:**
- Phone: +91 94191 90388
- WhatsApp: +91 94191 90388
- Email: anil7dhar@gmail.com

**For Technical Issues:**
Contact the clinic administration.

---

💻 **Developed with ❤️ by Vishut Dhar**

*Last Updated: December 2024*