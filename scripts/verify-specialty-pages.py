#!/usr/bin/env python3
"""Read-only checks that the generated specialty pages agree with index.html
and with each other. Exit code 1 on any drift.

  python3 scripts/verify-specialty-pages.py
"""
import re, sys, json, pathlib
import importlib.util

ROOT = pathlib.Path(__file__).resolve().parent.parent

spec = importlib.util.spec_from_file_location("gen", ROOT / "scripts" / "build-specialty-pages.py")
gen = importlib.util.module_from_spec(spec); spec.loader.exec_module(gen)

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

# 6. The stylesheet version the pages request is the one index.html requests.
v_index = re.search(r'styles\.css\?v=(\d+)', index).group(1)
check(v_index == gen.CSS_VERSION, f"CSS version differs: index.html {v_index}, generator {gen.CSS_VERSION}")

if failures:
    print("\n".join(f"FAIL {f}" for f in failures)); sys.exit(1)
print(f"ok: {len(gen.PAGES)} pages verified against index.html")
