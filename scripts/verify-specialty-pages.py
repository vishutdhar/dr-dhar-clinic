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

# 5e. No fee, phone number, hours or address component other than the home page's.
home_phone_digits = gen._DIGITS
for page in gen.PAGES:
    html = gen.render(page)
    text = _h.unescape(re.sub(r"<[^>]+>", " ", html))
    for fee in set(re.findall(r"(?:₹|Rs\.?|INR)\s?[\d,]+", text)):
        check(fee == gen.FEE, f"{page['slug']}: fee '{fee}' is not the home page fee {gen.FEE}")
    for num in set(re.findall(r"(?<![\d])(?:\+?91[ -]?)?\d{5}[ -]?\d{5}(?![\d])", text)):
        check(re.sub(r"\D", "", num).endswith(home_phone_digits), f"{page['slug']}: phone '{num}' is not the clinic phone")
    for t in set(re.findall(r"\d{1,2}(?::\d{2})? ?[AP]M", text)):
        check(t in gen.HOURS or t in index, f"{page['slug']}: time '{t}' not in the home page hours")
    when = re.search(r"<strong>When:</strong> (.*?)</p>", html).group(1)
    check(when == gen.HOURS, f"{page['slug']}: visit hours differ from the home schema")
    where = _h.unescape(re.search(r"<strong>Where:</strong> (.*?)\.</p>", html).group(1))
    check(where == gen.ADDRESS_LINE, f"{page['slug']}: visit address differs from the home schema")
    ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1))
    clinic = next(n for n in ld["@graph"] if n["@type"] == "MedicalClinic")
    check(clinic["address"] == home_clinic["address"], f"{page['slug']}: schema address differs from index.html")
    check(clinic["telephone"] == home_clinic["telephone"], f"{page['slug']}: schema telephone differs from index.html")
    for d in gen._DAYS:
        if d in text:
            pass  # day names are allowed; their hours are pinned by the When line above
    # 5f. Indexable, and every self-reference names this page.
    url = f"{gen.SITE}/{page['slug']}"
    robots = re.search(r'<meta name="robots" content="([^"]*)"', html)
    check(robots and "index" in robots.group(1).split(", ") and "noindex" not in robots.group(1), f"{page['slug']}: robots must allow indexing")
    check(re.search(r'<link rel="canonical" href="([^"]*)"', html).group(1) == url, f"{page['slug']}: canonical is not {url}")
    check(re.search(r'property="og:url" content="([^"]*)"', html).group(1) == url, f"{page['slug']}: og:url is not {url}")
    wp = next(n for n in ld["@graph"] if n["@type"] == "MedicalWebPage")
    check(wp["url"] == url and wp["@id"] == f"{url}#webpage", f"{page['slug']}: MedicalWebPage url/id differ")
    crumbs = next(n for n in ld["@graph"] if n["@type"] == "BreadcrumbList")
    check(crumbs["itemListElement"][-1]["item"] == url, f"{page['slug']}: breadcrumb does not end at {url}")
    # 5g. No rating or review markup: the home page carries none, and none may be invented.
    for banned in ("AggregateRating", "ratingValue", "reviewCount", '"Review"', "reviewRating"):
        check(banned not in html, f"{page['slug']}: contains {banned}, which index.html does not support")
    check("aggregateRating" not in html, f"{page['slug']}: contains aggregateRating")

# 5h. The generator source carries no literal fee or phone of its own, and the
#     footer hours block is the home page's block verbatim.
src = (ROOT / "scripts" / "build-specialty-pages.py").read_text(encoding="utf-8")
check(not re.search(r"₹[\d,]+", src), "generator hardcodes a fee; it must come from index.html")
check(gen.PHONE_DISPLAY not in src and gen._DIGITS not in src.replace("# +919419190388", "").replace("# 9419190388", ""),
      "generator hardcodes the phone; it must come from index.html")
home_hours_block = re.search(r'<h4>Clinic Hours</h4>(.*?)</div>', index, re.S).group(1).strip()
for page in gen.PAGES:
    html = gen.render(page)
    block = re.search(r'<h3 class="footer-heading">Clinic Hours</h3>(.*?)</div>', html, re.S).group(1).strip()
    check(block == home_hours_block, f"{page['slug']}: footer hours block differs from index.html")

# 6. The stylesheet version the pages request is the one index.html requests.
v_index = re.search(r'styles\.css\?v=(\d+)', index).group(1)
check(v_index == gen.CSS_VERSION, f"CSS version differs: index.html {v_index}, generator {gen.CSS_VERSION}")

if failures:
    print("\n".join(f"FAIL {f}" for f in failures)); sys.exit(1)
print(f"ok: {len(gen.PAGES)} pages verified against index.html")
