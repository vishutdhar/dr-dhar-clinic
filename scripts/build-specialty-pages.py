#!/usr/bin/env python3
"""Generate the specialty pages from one template so header, footer, contact
obfuscation, styles and structured data never drift from index.html.

Run from the repo root:  python3 scripts/build-specialty-pages.py
Every claim below is drawn from index.html (services, FAQ, timings, fees).
Nothing here states an outcome or a fee the home page does not state.
"""
import json, html, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://dranilkumardhar.com"
CSS_VERSION = "20260915"
PHONE_ENT = "&#57;&#52;&#49;&#57;&#49;&#57;&#48;&#51;&#56;&#56;"          # 9419190388
PHONE_DISPLAY_ENT = "&#57;&#52;&#49;&#57;&#49;&#32;&#57;&#48;&#51;&#56;&#56;"  # 94191 90388
TODAY = datetime.date.today().isoformat()

CLINIC = {
    "@type": "MedicalClinic",
    "@id": f"{SITE}#clinic",
    "name": "Dr. Anil Kumar Dhar's Clinic",
    "url": SITE,
    "telephone": "+919419190388",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "House No. 48, Bhagwati Nagar, Canal Road",
        "addressLocality": "Jammu",
        "addressRegion": "Jammu and Kashmir",
        "postalCode": "180016",
        "addressCountry": "IN",
    },
}
PHYSICIAN = {"@type": "Physician", "@id": f"{SITE}#physician", "name": "Dr. Anil Kumar Dhar", "url": SITE}

PAGES = [
    {
        "slug": "general-physician-jammu",
        "title": "General Physician in Jammu | Dr. Anil Kumar Dhar",
        "description": "Dr. Anil Kumar Dhar, MBBS MD DNB, general physician in Jammu with 30+ years in internal medicine. Fever, infections, BP, sugar and check-ups. Canal Road clinic.",
        "h1": "General Physician in Jammu",
        "lede": "Dr. Anil Kumar Dhar is an internal medicine physician (MBBS, MD, DNB) who has practised in Jammu for more than 30 years. His clinic on Canal Road, Bhagwati Nagar, sees adults for everyday illness, long-term conditions and full health check-ups, with a pharmacy on site.",
        "about_condition": None,
        "sections": [
            ("What a general physician treats",
             "<p>An internal medicine physician looks after the health of adults as a whole rather than one organ. At this clinic that means fever and infections, respiratory problems such as cough and breathlessness, thyroid disorders, blood pressure, diabetes, heart-related risk, and the general complaints that do not fit a neat label: tiredness, weight change, poor sleep, aches that will not settle.</p><p>Because the same doctor follows you over time, a problem is seen in the context of your history, your reports and your other medicines, which is the main advantage of having one physician rather than a different doctor for each complaint.</p>"),
            ("The general check-up",
             "<p>The clinic's general check-up costs <strong>₹1,000</strong> and includes a physical examination, blood pressure measurement, fasting and post-meal blood sugar testing, cholesterol screening and a detailed consultation with personalised advice. It is the right starting point if you have not seen a doctor in a while, have a family history of diabetes or heart disease, or simply want a baseline.</p>"),
            ("What to bring",
             "<p>Any previous medical reports, a list of the medicines you take (or the strips themselves), and, if you have them, recent blood test results. If you are coming for a check-up that includes fasting blood sugar, come without breakfast; the post-meal reading is taken after you eat.</p>"),
            ("When not to wait for an appointment",
             "<p>Chest pain, sudden weakness or numbness on one side, difficulty speaking, severe breathlessness, or a very high fever with confusion are emergencies. Go to the nearest hospital emergency department rather than waiting for a clinic slot.</p>"),
        ],
        "faqs": [
            ("Do I need a referral to see Dr. Dhar?", "No. Anyone can book directly by phone, WhatsApp or SMS on 94191 90388."),
            ("What does the general check-up cost?", "₹1,000. It includes the examination, blood pressure, fasting and post-meal blood sugar, cholesterol screening and the consultation."),
            ("Which days is the clinic open?", "Monday and Wednesday to Saturday, 9 AM to 1 PM and 4:30 PM to 7 PM; Sunday 9 AM to 3 PM. The clinic is closed on Tuesdays."),
        ],
        "specialty": "InternalMedicine",
    },
    {
        "slug": "diabetes-doctor-jammu",
        "title": "Diabetes Doctor in Jammu | Dr. Anil Kumar Dhar",
        "description": "Diabetes care in Jammu with Dr. Anil Kumar Dhar, MBBS MD DNB: Type 1 and 2 management, HbA1c tracking, diet plans, insulin adjustment, complication prevention.",
        "h1": "Diabetes Doctor in Jammu",
        "lede": "Dr. Anil Kumar Dhar manages Type 1 and Type 2 diabetes at his clinic on Canal Road, Jammu: regular HbA1c tracking, fasting blood sugar monitoring, a diet plan built around what you actually eat, insulin adjustment when it is needed, and long-term prevention of complications.",
        "about_condition": "Diabetes mellitus",
        "sections": [
            ("What diabetes care involves here",
             "<p>Diabetes is managed over years, not in one visit. The clinic tracks <strong>HbA1c</strong> (the three-month average of your blood sugar) at regular intervals, checks fasting and post-meal sugar, reviews your medicines and adjusts insulin doses when readings call for it. Diet advice is personalised rather than a printed sheet, because a plan you cannot follow is not a plan.</p><p>Just as important is watching for complications early: blood pressure and cholesterol, kidney function, and the eye and foot problems that diabetes can cause when sugar stays high for a long time. Catching these early is the point of regular follow-up.</p>"),
            ("Who should come",
             "<p>Anyone already diagnosed with diabetes who wants one doctor to follow their control over time. Anyone with symptoms that suggest it: unusual thirst, passing urine often, tiredness, blurred vision, wounds that heal slowly, or unexplained weight loss. And anyone with a strong family history who wants to be screened; the general check-up includes fasting and post-meal blood sugar.</p>"),
            ("What to bring",
             "<p>Your glucometer log if you keep one, recent HbA1c and blood reports, the medicines or insulin you use with their doses, and a note of any low-sugar episodes. If your visit includes a fasting test, come without breakfast and bring something to eat afterwards.</p>"),
            ("The pharmacy on site",
             "<p>Prescribed medicines and insulin are available from the clinic's own pharmacy immediately after the consultation, so a change in dose does not mean a second trip.</p>"),
        ],
        "faqs": [
            ("Does Dr. Dhar treat Type 1 as well as Type 2 diabetes?", "Yes. The clinic manages both, including insulin adjustment for patients who use it."),
            ("How often should HbA1c be checked?", "That depends on how stable your control is; the doctor sets the interval at your visit. The clinic tracks it regularly as part of ongoing care."),
            ("What does a diabetes consultation cost?", "Ask when you book on 94191 90388. The general check-up, which includes fasting and post-meal blood sugar, is ₹1,000."),
        ],
        "specialty": "Diabetology",
    },
    {
        "slug": "bp-and-heart-care-jammu",
        "title": "Blood Pressure and Heart Care in Jammu | Dr. Anil Kumar Dhar",
        "description": "Hypertension treatment and heart risk care in Jammu with Dr. Anil Kumar Dhar, MBBS MD DNB: BP monitoring, cholesterol management, cardiovascular risk assessment.",
        "h1": "Blood Pressure and Heart Care in Jammu",
        "lede": "High blood pressure rarely announces itself, which is why it is measured at every visit here. Dr. Anil Kumar Dhar treats hypertension, manages cholesterol and assesses cardiovascular risk at his internal medicine clinic on Canal Road, Jammu, with medication chosen on evidence-based protocols.",
        "about_condition": "Hypertension",
        "sections": [
            ("What blood pressure care involves here",
             "<p>Blood pressure is measured properly, seated and rested, and compared with your readings at home if you take them. If treatment is needed, the doctor starts or adjusts medicines and follows up until the numbers are where they should be. Cholesterol is checked and managed alongside, because blood pressure and cholesterol together decide most of the risk to the heart.</p><p>A cardiovascular risk assessment puts these together with your age, sugar, weight, smoking and family history to estimate where you stand and what would change it most.</p>"),
            ("Who should come",
             "<p>Anyone told their blood pressure is high, anyone on blood pressure or cholesterol medicine who wants it reviewed, and anyone with a family history of heart disease, stroke or diabetes who has not been assessed. Headaches, breathlessness on exertion, or swelling of the feet are worth a visit.</p>"),
            ("What to bring",
             "<p>Your home blood pressure readings if you have them, any ECG, echo or blood reports, and the medicines you take. Avoid tea, coffee or smoking in the half hour before the visit so the reading is a fair one.</p>"),
            ("When it is an emergency",
             "<p>Chest pain or pressure, pain spreading to the arm or jaw, sudden breathlessness, or sudden weakness or slurred speech are not clinic matters. Go to the nearest hospital emergency department at once.</p>"),
        ],
        "faqs": [
            ("Does the clinic do ECGs?", "Ask when you book on 94191 90388. The clinic offers lab collection on site; the doctor will tell you which tests you need and where."),
            ("Can I stop my blood pressure medicine if my readings are normal?", "Not on your own. Readings are normal because the medicine is working; any change should be made by the doctor after a review."),
            ("What does a consultation cost?", "Ask when you book. The general check-up, which includes blood pressure and cholesterol screening, is ₹1,000."),
        ],
        "specialty": "InternalMedicine",
    },
    {
        "slug": "vaccination-jammu",
        "title": "Adult Vaccination in Jammu | Dr. Anil Kumar Dhar",
        "description": "Adult vaccination in Jammu at Dr. Anil Kumar Dhar's clinic: annual flu, pneumonia, hepatitis B, typhoid and other recommended vaccines under proper cold chain.",
        "h1": "Adult Vaccination in Jammu",
        "lede": "Vaccines are not only for children. Dr. Anil Kumar Dhar's clinic on Canal Road, Jammu, offers adult immunisation including the annual flu vaccine, pneumonia vaccine, hepatitis B, typhoid and other recommended vaccines, stored under proper cold chain and given by the clinic.",
        "about_condition": None,
        "sections": [
            ("Vaccines offered",
             "<p>The annual <strong>influenza</strong> vaccine, the <strong>pneumonia</strong> vaccine, <strong>hepatitis B</strong>, <strong>typhoid</strong>, and other vaccines recommended for adults according to age, health conditions and travel. The doctor advises which apply to you; not everyone needs every vaccine.</p>"),
            ("Who benefits most",
             "<p>Adults over 60, people with diabetes, heart or lung disease, or a weakened immune system, for whom flu and pneumonia are far more dangerous than for a healthy young adult. People who missed hepatitis B as children. Anyone travelling to areas where typhoid is common. And anyone who simply wants their adult vaccinations up to date.</p>"),
            ("What to bring",
             "<p>Any record of previous vaccinations, and a note of allergies or reactions to past vaccines. Tell the doctor if you are unwell on the day, pregnant, or on medicines that affect immunity; the vaccine may be given or deferred accordingly.</p>"),
            ("Cold chain",
             "<p>A vaccine that has been warm is a vaccine that may not work. The clinic stores its vaccines under proper cold chain so that what you receive is effective.</p>"),
        ],
        "faqs": [
            ("When should I get the flu vaccine?", "Once a year. Ask the clinic about timing for the current season when you book on 94191 90388."),
            ("Do I need an appointment for a vaccine?", "Yes. Book by phone, WhatsApp or SMS so the right vaccine is ready for you."),
            ("What do vaccines cost?", "Prices differ by vaccine. Ask when you book."),
        ],
        "specialty": "InternalMedicine",
    },
]


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def json_ld(page: dict) -> str:
    url = f"{SITE}/{page['slug']}"
    graph = [
        {
            "@type": "MedicalWebPage",
            "@id": f"{url}#webpage",
            "url": url,
            "name": page["title"],
            "description": page["description"],
            "isPartOf": {"@id": f"{SITE}#website"},
            "about": {"@id": f"{SITE}#clinic"},
            "inLanguage": "en-IN",
            "medicalAudience": {"@type": "MedicalAudience", "audienceType": "Patient"},
        },
        CLINIC,
        PHYSICIAN,
        {
            "@type": "BreadcrumbList",
            "@id": f"{url}#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": page["h1"], "item": url},
            ],
        },
        {
            "@type": "FAQPage",
            "@id": f"{url}#faq",
            "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in page["faqs"]
            ],
        },
    ]
    if page["about_condition"]:
        graph[0]["about"] = [{"@id": f"{SITE}#clinic"}, {"@type": "MedicalCondition", "name": page["about_condition"]}]
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False).replace("<", "\\u003c")


def render(page: dict) -> str:
    url = f"{SITE}/{page['slug']}"
    sections = "\n".join(
        f'            <section class="article-section">\n                <h2>{esc(h)}</h2>\n                {b}\n            </section>'
        for h, b in page["sections"]
    )
    faqs = "\n".join(
        f'            <details class="faq-item">\n                <summary class="faq-question">{esc(q)}</summary>\n                <div class="faq-answer"><p>{esc(a)}</p></div>\n            </details>'
        for q, a in page["faqs"]
    )
    return f"""<!DOCTYPE html>
<html lang="en-IN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(page['title'])}</title>
    <meta name="description" content="{esc(page['description'])}">
    <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
    <link rel="canonical" href="{url}">

    <meta property="og:title" content="{esc(page['title'])}">
    <meta property="og:description" content="{esc(page['description'])}">
    <meta property="og:url" content="{url}">
    <meta property="og:type" content="article">
    <meta property="og:site_name" content="Dr. Anil Kumar Dhar's Clinic">
    <meta property="og:locale" content="en_IN">
    <meta property="og:image" content="{SITE}/og-image.jpg">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:image:alt" content="Dr. Anil Kumar Dhar - Internal Medicine Specialist in Jammu">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{esc(page['title'])}">
    <meta name="twitter:description" content="{esc(page['description'])}">
    <meta name="twitter:image" content="{SITE}/og-image.jpg">
    <meta name="theme-color" content="#0a0f1c">

    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">

    <link rel="preload" href="/assets/fonts/plus-jakarta-sans-v12-latin-300-700.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="preload" href="/assets/fonts/instrument-serif-v5-latin.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="stylesheet" href="/styles.css?v={CSS_VERSION}">

    <script type="application/ld+json">{json_ld(page)}</script>
</head>
<body>
    <a href="#main" class="skip-link">Skip to main content</a>
    <header class="header" role="banner">
        <div class="header-content">
            <a class="logo" href="/">
                <svg class="logo-icon" width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                    <rect x="10" y="2" width="4" height="20" rx="1"/>
                    <rect x="2" y="10" width="20" height="4" rx="1"/>
                </svg>
                <span>Dr. Dhar's Clinic</span>
            </a>
            <nav class="header-nav" aria-label="Main navigation">
                <a href="/#services">Specialties</a>
                <a href="/#about">Our Team</a>
                <a href="/#faq">FAQ</a>
                <a href="/#booking">Book Appointment</a>
            </nav>
            <div class="status-badge" id="clinic-status">
                <span class="status-dot"></span>
                <span class="status-text">Checking...</span>
            </div>
        </div>
    </header>

    <main id="main" tabindex="-1">
        <article class="article">
            <nav class="breadcrumb" aria-label="Breadcrumb">
                <a href="/">Home</a><span aria-hidden="true">/</span><span aria-current="page">{esc(page['h1'])}</span>
            </nav>
            <h1>{esc(page['h1'])}</h1>
            <p class="article-lede">{esc(page['lede'])}</p>
            <div class="hero-actions article-actions">
                <a href="https://wa.me/91{PHONE_ENT}" data-obf-href="wa" class="btn btn-whatsapp whatsapp">WhatsApp to Book</a>
                <a href="tel:+91{PHONE_ENT}" data-obf-href="tel" class="btn btn-dark">Call Clinic</a>
            </div>

{sections}

            <section class="article-section visit-card">
                <h2>Visiting the clinic</h2>
                <p><strong>Where:</strong> House No. 48, Bhagwati Nagar, Canal Road, Jammu, J&amp;K 180016.</p>
                <p><strong>When:</strong> Monday and Wednesday to Saturday, 9 AM to 1 PM and 4:30 PM to 7 PM. Sunday 9 AM to 3 PM. Closed on Tuesdays.</p>
                <p><strong>Booking:</strong> call or WhatsApp <a href="tel:+91{PHONE_ENT}" data-obf-href="tel" data-obf="phone">{PHONE_DISPLAY_ENT}</a>, or send an SMS with your name and preferred time. Cash and all UPI apps accepted. In-house pharmacy and lab collection on site.</p>
            </section>

            <section class="article-section" aria-labelledby="faq-heading">
                <h2 id="faq-heading">Frequently asked questions</h2>
                <div class="faq-container">
{faqs}
                </div>
            </section>

            <p class="disclaimer">This page describes the services of Dr. Anil Kumar Dhar's clinic and is general information, not medical advice for your situation. For advice about your own health, consult the doctor.</p>
        </article>
    </main>

    <footer>
        <div class="footer-content">
            <div class="footer-grid">
                <div class="footer-brand">
                    <div class="footer-logo">
                        <svg class="footer-logo-icon" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                            <rect x="10" y="2" width="4" height="20" rx="1"/>
                            <rect x="2" y="10" width="20" height="4" rx="1"/>
                        </svg>
                        Dr. Dhar's Clinic
                    </div>
                    <p class="footer-tagline">Comprehensive Healthcare in Jammu</p>
                    <p class="footer-phone"><a href="tel:+91{PHONE_ENT}" data-obf-href="tel" data-obf="phone">{PHONE_DISPLAY_ENT}</a></p>
                </div>
                <div class="footer-col">
                    <h4>Specialties</h4>
                    <ul class="footer-links">
                        <li><a href="/general-physician-jammu">General Physician</a></li>
                        <li><a href="/diabetes-doctor-jammu">Diabetes Care</a></li>
                        <li><a href="/bp-and-heart-care-jammu">Heart &amp; BP Care</a></li>
                        <li><a href="/vaccination-jammu">Vaccination</a></li>
                        <li><a href="/#services">Longevity Care</a></li>
                        <li><a href="/#services">In-house Pharmacy</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h4>Quick Links</h4>
                    <ul class="footer-links">
                        <li><a href="/#services">Our Services</a></li>
                        <li><a href="/#about">Our Team</a></li>
                        <li><a href="/#faq">FAQ</a></li>
                        <li><a href="/#booking">Book Appointment</a></li>
                        <li><a href="/#clinic-info">Clinic Timings</a></li>
                        <li><a href="/#contact">Contact Us</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h4>Clinic Hours</h4>
                    <p class="footer-hours">Mon, Wed-Sat</p>
                    <p class="footer-hours-detail">9 AM - 1 PM, 4:30 - 7 PM</p>
                    <p class="footer-hours">Sunday</p>
                    <p class="footer-hours-detail">9 AM - 3 PM</p>
                    <p class="footer-hours footer-closed">Tuesday: Closed</p>
                </div>
            </div>
            <div class="footer-bottom">
                <p class="footer-copyright">&copy; 2026 Dr. Anil Kumar Dhar's Clinic. All rights reserved.</p>
                <p class="footer-attribution">Built by Vishut Dhar</p>
            </div>
        </div>
    </footer>

    <button id="back-to-top" class="back-to-top" aria-label="Back to top">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M7.41 15.41L12 10.83l4.59 4.58L18 14l-6-6-6 6z"/>
        </svg>
    </button>

    <script src="/script.js" defer></script>
    <noscript>
        <div class="noscript-banner">
            To book an appointment, call <strong>94191 90388</strong> or email <strong>anil7dhar@gmail.com</strong>
        </div>
    </noscript>
</body>
</html>
"""


def main() -> None:
    for page in PAGES:
        out = ROOT / f"{page['slug']}.html"
        out.write_text(render(page), encoding="utf-8")
        print(f"wrote {out.name} ({len(out.read_text().split())} words)")


if __name__ == "__main__":
    main()
