#!/usr/bin/env python3
"""Read-only checks that the generated specialty pages agree with index.html
and with each other. Exit code 1 on any drift.

  python3 scripts/verify-specialty-pages.py
"""
import re, sys, json, pathlib, types

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Execute the generator's source directly rather than importing it: an import
# would go through the bytecode cache, which is keyed by mtime at one-second
# resolution, so an edit made within a second of the last run would verify
# stale code.
gen = types.ModuleType("gen")
gen.__file__ = str(ROOT / "scripts" / "build-specialty-pages.py")
exec(compile((ROOT / "scripts" / "build-specialty-pages.py").read_text(encoding="utf-8"), gen.__file__, "exec"), gen.__dict__)

index = (ROOT / "index.html").read_text(encoding="utf-8")
failures = []

def check(cond, msg):
    if not cond:
        failures.append(msg)

# 1. Committed pages are exactly what the generator produces.
for page in gen.PAGES:
    path = ROOT / f"{page['slug']}.html"
    check(path.exists(), f"{path.name} missing")
    if path.exists():
        check(path.read_text(encoding="utf-8") == gen.render(page), f"{path.name} is stale: run scripts/build-specialty-pages.py")

# 2. Shared contact and hours facts match index.html byte for byte.
for token, label in [
    (gen.PHONE_ENT, "phone entity"),
    (gen.PHONE_DISPLAY_ENT, "displayed phone"),
    (gen.EMAIL_ENT, "email entity"),
    ("House No. 48, Bhagwati Nagar, Canal Road", "street address"),
    ("9 AM - 1 PM, 4:30 - 7 PM", "weekday hours"),
    ("9 AM - 3 PM", "Sunday hours"),
    ("Tuesday: Closed", "closed day"),
    ("₹1,000", "check-up fee"),
]:
    check(token in index, f"{label} not found in index.html")
    for page in gen.PAGES:
        html = gen.render(page)
        if label in ("phone entity", "displayed phone", "email entity", "street address", "weekday hours", "Sunday hours", "closed day"):
            check(token in html, f"{page['slug']}: {label} missing")

# 3. Every service the pages describe is a service index.html lists.
for name in ["General Check-up", "Diabetes Care", "Heart & BP Care", "Vaccination", "In-house Pharmacy"]:
    check(f"<h3>{name}</h3>" in index, f"service card '{name}' not on index.html")

# 4. Links: index.html and every page link to every specialty page; sitemap lists them.
sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
for page in gen.PAGES:
    href = f'href="/{page["slug"]}"'
    check(href in index, f"index.html does not link to /{page['slug']}")
    check(f"<loc>{gen.SITE}/{page['slug']}</loc>" in sitemap, f"sitemap.xml lacks /{page['slug']}")
    for other in gen.PAGES:
        check(href in gen.render(other), f"{other['slug']} footer does not link to /{page['slug']}")

# 5. Metadata lengths and FAQ parity between visible answers and JSON-LD.
for page in gen.PAGES:
    html = gen.render(page)
    check(len(page["title"]) <= 60, f"{page['slug']}: title {len(page['title'])} chars")
    check(len(page["description"]) <= 160, f"{page['slug']}: description {len(page['description'])} chars")
    ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1))
    faq = next(n for n in ld["@graph"] if n["@type"] == "FAQPage")
    visible = re.findall(r'<summary class="faq-question">(.*?)</summary>\s*<div class="faq-answer"><p>(.*?)</p>', html, re.S)
    import html as h
    check([(h.unescape(q), h.unescape(a)) for q, a in visible] == [(e["name"], e["acceptedAnswer"]["text"]) for e in faq["mainEntity"]],
          f"{page['slug']}: visible FAQ and FAQPage differ")
    check(html.count('id="back-to-top"') == 1, f"{page['slug']}: back-to-top button missing (script.js binds it)")
    check('id="clinic-status"' in html, f"{page['slug']}: status badge missing (script.js binds it)")

# 5b. Every fee, hours string and phone number that appears on a page appears on
#     index.html too, and the page schema's clinic facts equal the home schema's.
home_ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', index, re.S).group(1))
home_clinic = next(n for n in home_ld["@graph"] if n["@type"] == "MedicalClinic")
check(gen.CLINIC["telephone"] == home_clinic["telephone"], "schema telephone differs from index.html")
for k in ("streetAddress", "addressLocality", "postalCode"):
    check(gen.CLINIC["address"][k] == home_clinic["address"][k], f"schema address {k} differs from index.html")
for page in gen.PAGES:
    html = gen.render(page)
    for fee in set(re.findall(r"₹[\d,]+", html)):
        check(fee in index, f"{page['slug']}: fee {fee} not on index.html")
    for hours in set(re.findall(r"\d{1,2}(?::\d{2})? ?[AP]M(?: - \d{1,2}(?::\d{2})? ?[AP]M)?", html)):
        check(hours in index, f"{page['slug']}: hours '{hours}' not on index.html")
    for phone in set(re.findall(r"\b\d{5} \d{5}\b", html)):
        check(phone in index, f"{page['slug']}: phone {phone} not on index.html")
    check(html.count("+919419190388") == html.count('"telephone"'), f"{page['slug']}: schema telephone changed")

# 5c. Elements and script that script.js depends on at runtime.
for page in gen.PAGES:
    html = gen.render(page)
    check('<script src="/script.js" defer></script>' in html, f"{page['slug']}: script.js not loaded")
    badge = re.search(r'<div class="status-badge" id="clinic-status">(.*?)</div>', html, re.S)
    check(badge is not None and 'class="status-dot"' in badge.group(1) and 'class="status-text"' in badge.group(1),
          f"{page['slug']}: status badge lacks .status-dot or .status-text (updateClinicStatus throws)")

# 5d. Rendered metadata: lengths and parity across title, description, OG, Twitter and JSON-LD.
import html as _h
for page in gen.PAGES:
    html = gen.render(page)
    title = _h.unescape(re.search(r"<title>(.*?)</title>", html).group(1))
    desc = _h.unescape(re.search(r'<meta name="description" content="([^"]*)"', html).group(1))
    check(len(title) <= 60, f"{page['slug']}: rendered title {len(title)} chars")
    check(len(desc) <= 160, f"{page['slug']}: rendered description {len(desc)} chars")
    for prop in ("og:title", "twitter:title"):
        m = re.search(r'(?:property|name)="' + prop + r'" content="([^"]*)"', html)
        check(m and _h.unescape(m.group(1)) == title, f"{page['slug']}: {prop} differs from <title>")
    for prop in ("og:description", "twitter:description"):
        m = re.search(r'(?:property|name)="' + prop + r'" content="([^"]*)"', html)
        check(m and _h.unescape(m.group(1)) == desc, f"{page['slug']}: {prop} differs from description")
    ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1))
    wp = next(n for n in ld["@graph"] if n["@type"] == "MedicalWebPage")
    check(wp["name"] == title and wp["description"] == desc, f"{page['slug']}: MedicalWebPage name/description differ from metadata")

# 6. The stylesheet version the pages request is the one index.html requests.
v_index = re.search(r'styles\.css\?v=(\d+)', index).group(1)
check(v_index == gen.CSS_VERSION, f"CSS version differs: index.html {v_index}, generator {gen.CSS_VERSION}")

if failures:
    print("\n".join(f"FAIL {f}" for f in failures)); sys.exit(1)
print(f"ok: {len(gen.PAGES)} pages verified against index.html")
