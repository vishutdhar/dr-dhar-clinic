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

# 2. Shared contact facts, parsed from index.html independently of the generator,
#    appear on every page in the same encoded form the home page uses.
home_ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', index, re.S).group(1))
home_clinic = next(n for n in home_ld["@graph"] if n["@type"] == "MedicalClinic")
home_digits = home_clinic["telephone"].removeprefix("+91")
home_display = f"{home_digits[:5]} {home_digits[5:]}"
import html as _h
home_email = _h.unescape(re.search(r'data-obf="email">([^<]+)<', index).group(1))
ent = lambda t: "".join(f"&#{ord(c)};" for c in t)
check(gen._DIGITS == home_digits and gen.PHONE_DISPLAY == home_display and gen.EMAIL == home_email, "generator facts differ from index.html")
for page in gen.PAGES:
    html = gen.render(page)
    for token, label in [(ent(home_digits), "phone entity"), (ent(home_display), "displayed phone"), (ent(home_email), "email entity")]:
        check(token in html, f"{page['slug']}: {label} missing")

# 2b. script.js, which rewrites the contact details at runtime, carries the same
#     phone and email as the home page.
js = (ROOT / "script.js").read_text(encoding="utf-8")
codes = lambda name: "".join(chr(int(c)) for c in re.search(r"var " + name + r" = \[([\d,]+)\]", js).group(1).split(","))
check(codes("p") == home_digits, "script.js phone differs from index.html")
check(codes("e") == home_email, "script.js email differs from index.html")

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
home_phone_digits = home_digits
for page in gen.PAGES:
    html = gen.render(page)
    text = _h.unescape(re.sub(r"<[^>]+>", " ", html))
    # Fees: only the home page's amount, and only in a sentence about the check-up it prices.
    for m in re.finditer(r"(?:₹|Rs\.?|INR)\s?[\d,]+", text):
        check(m.group(0) == gen.FEE, f"{page['slug']}: fee '{m.group(0)}' is not the home page fee {gen.FEE}")
        sentence = text[text.rfind(".", 0, m.start()) + 1 : text.find(".", m.end()) + 1]
        check("check-up" in sentence.lower(), f"{page['slug']}: fee stated for something other than the check-up: '{sentence.strip()[:80]}'")
    for num in set(re.findall(r"(?<![\d])(?:\+?91[ -]?)?\d{5}[ -]?\d{5}(?![\d])", text)):
        check(re.sub(r"\D", "", num).endswith(home_phone_digits), f"{page['slug']}: phone '{num}' is not the clinic phone")
    # Hours: every clock time on the page lives inside the generated hours sentence
    # or the footer block copied from the home page; nowhere else may state hours.
    stripped = html.replace(gen.HOURS, "").replace(gen.FOOTER_HOURS_BLOCK, "")
    stray = re.findall(r"\d{1,2}(?::\d{2})? ?[AP]M", _h.unescape(re.sub(r"<[^>]+>", " ", stripped)))
    check(not stray, f"{page['slug']}: hours stated outside the home-derived sentence: {stray}")
    # Contact links: every tel/sms/wa/mailto destination decodes to the home phone or email.
    for href in re.findall(r'href="((?:tel:|sms:|https://wa\.me/|mailto:)[^"]*)"', html):
        dest = _h.unescape(href)
        if dest.startswith("mailto:"):
            check(dest.split("?")[0] == f"mailto:{home_email}", f"{page['slug']}: mailto destination {dest} is not the clinic email")
        else:
            check(re.sub(r"\D", "", dest.split("?")[0]).endswith(home_phone_digits), f"{page['slug']}: link {dest[:40]} does not dial the clinic")
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

# 7. Expectations derived from the home page alone, never from the generator.
#    (a) fee: the check-up Offer price; (b) schedule: OpeningHoursSpecification;
#    (c) address: the PostalAddress; (d) inclusions: the check-up card text;
#    (e) script.js runtime schedule and link prefixes.
_offer = next(o for o in home_clinic["hasOfferCatalog"]["itemListElement"] if o["itemOffered"]["name"] == "General Check-up")
expected_fee = f"₹{int(_offer['price']):,}"
check(gen.FEE == expected_fee, f"generator fee {gen.FEE} differs from the home Offer price {expected_fee}")
_addr = home_clinic["address"]
expected_where = f"{_addr['streetAddress']}, {_addr['addressLocality']}, J&K {_addr['postalCode']}"
_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
def _clock(t):
    h, m = (int(x) for x in t.split(":")); suffix = "AM" if h < 12 else "PM"; h12 = h % 12 or 12
    return f"{h12}:{m:02d} {suffix}" if m else f"{h12} {suffix}"
home_schedule = {d: [] for d in _days}
for spec in home_clinic["openingHoursSpecification"]:
    for d in spec["dayOfWeek"]:
        home_schedule[d].append((spec["opens"], spec["closes"]))
closed_days = [d for d in _days if not home_schedule[d]]
home_checkup_text = _h.unescape(re.search(r"<h3>General Check-up</h3>\s*<p>(.*?)</p>", index, re.S).group(1)).lower()
INCLUSION_WORDS = {"blood pressure": "blood pressure", "blood sugar": "blood sugar", "cholesterol": "cholesterol", "consultation": "consultation", "physical examination": "physical examination"}

for page in gen.PAGES:
    html = gen.render(page)
    text = _h.unescape(re.sub(r"<[^>]+>", " ", html))
    text = re.sub(r"\s+", " ", text)
    # (a) fee amount on the page equals the home Offer price, and each priced
    #     sentence names the check-up and no other service.
    for m in re.finditer(r"(?:₹|Rs\.?|INR)\s?[\d,]+", text):
        check(m.group(0) == expected_fee, f"{page['slug']}: fee '{m.group(0)}' is not the home Offer price {expected_fee}")
        sentence = text[text.rfind(".", 0, m.start()) + 1 : text.find(".", m.end()) + 1].lower()
        check("check-up" in sentence, f"{page['slug']}: priced sentence does not name the check-up: '{sentence.strip()[:80]}'")
        check(not re.search(r"vaccin|diabetes consultation|consultation cost|per vaccine|heart|blood pressure care", sentence),
              f"{page['slug']}: priced sentence names another service: '{sentence.strip()[:80]}'")
    # (b) the hours sentence states every open day's intervals and every closed day,
    #     and no day name appears anywhere else on the page.
    for d in _days:
        for opens, closes in home_schedule[d]:
            check(f"{_clock(opens)} to {_clock(closes)}" in gen.HOURS, f"hours sentence lacks {d} {opens}-{closes}")
    for d in closed_days:
        check(f"Closed on {d}s" in gen.HOURS, f"hours sentence does not say closed on {d}s")
    covered = set()
    for a_day, b_day in re.findall(r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday) to (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)", gen.HOURS):
        covered.update(_days[_days.index(a_day):_days.index(b_day) + 1])
    covered.update(d for d in _days if re.search(r"\b" + d + r"\b", gen.HOURS))
    for d in [d for d in _days if home_schedule[d]]:
        check(d in covered, f"hours sentence does not cover {d}")
    stripped = re.sub(r"\s+", " ", _h.unescape(re.sub(r"<[^>]+>", " ", html.replace(gen.HOURS, "").replace(gen.FOOTER_HOURS_BLOCK, ""))))
    stray_days = [d for d in _days if re.search(r"\b" + d + r"s?\b", stripped)]
    check(not stray_days, f"{page['slug']}: day names outside the home-derived hours: {stray_days}")
    # (c) the visible address equals the home PostalAddress.
    where = _h.unescape(re.search(r"<strong>Where:</strong> (.*?)\.</p>", html).group(1))
    check(where == expected_where, f"{page['slug']}: visit address '{where}' differs from the home PostalAddress")
    # (d) every check-up inclusion the page promises is in the home check-up card.
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        s = sentence.lower()
        if "check-up" in s and ("include" in s or "includes" in s):
            for word in INCLUSION_WORDS:
                if word in s:
                    check(word in home_checkup_text, f"{page['slug']}: check-up promises '{word}', not in the home card")
    # (e) full contact destinations, country code included.
    for href in re.findall(r'href="((?:tel:|sms:|https://wa\.me/|mailto:)[^"]*)"', html):
        dest = _h.unescape(href).split("?")[0]
        if dest.startswith("tel:"):
            check(dest == f"tel:{home_clinic['telephone']}", f"{page['slug']}: {dest} is not tel:{home_clinic['telephone']}")
        elif dest.startswith("sms:"):
            check(dest == f"sms:{home_clinic['telephone']}", f"{page['slug']}: {dest} is not sms:{home_clinic['telephone']}")
        elif dest.startswith("https://wa.me/"):
            check(dest == f"https://wa.me/{home_clinic['telephone'].lstrip('+')}", f"{page['slug']}: {dest} is not the clinic WhatsApp")

# 7e. script.js: runtime link prefixes and the open/closed schedule match the home page.
cc = home_clinic["telephone"][:3]  # +91
check(f"el.href='tel:{cc}'+p" in js and f"el.href='sms:{cc}'+p" in js and f"el.href='https://wa.me/{cc.lstrip('+')}'+p" in js,
      "script.js dials a different country code than the home page")
js_sched = {}
for m in re.finditer(r"^\s*(\d): \[(.*?)\],?$", js, re.M):
    js_sched[int(m.group(1))] = [(int(a), int(b)) for a, b in re.findall(r"start: (\d+), end: (\d+)", m.group(2))]
js_day = {"Sunday": 0, "Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6}
mins = lambda t: int(t[:2]) * 60 + int(t[3:])
for d in _days:
    expected = sorted((mins(o), mins(c)) for o, c in home_schedule[d])
    check(sorted(js_sched.get(js_day[d], [])) == expected, f"script.js schedule for {d} differs from the home OpeningHoursSpecification")

if failures:
    print("\n".join(f"FAIL {f}" for f in failures)); sys.exit(1)
print(f"ok: {len(gen.PAGES)} pages verified against index.html")
