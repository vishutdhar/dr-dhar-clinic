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
checks = 0

def check(cond, msg):
    global checks
    checks += 1
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
    check(len(page["title"]) <= 63, f"{page['slug']}: title {len(page['title'])} chars")
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
    check(len(title) <= 63, f"{page['slug']}: rendered title {len(title)} chars")
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


# 8. Site-wide search signals, checked on the committed files of all five
#    indexable pages (the home page and the four specialty pages).
SITE_PAGES = {"/": index}
for page in gen.PAGES:
    path = ROOT / f"{page['slug']}.html"
    SITE_PAGES[f"/{page['slug']}"] = path.read_text(encoding="utf-8") if path.exists() else ""
text_of = lambda frag: re.sub(r"\s+", " ", _h.unescape(re.sub(r"<[^>]+>", " ", frag))).strip()
GENERIC_ANCHORS = {"learn more", "read more", "click here", "here", "more", "details"}
_FILLER = {"in", "jammu", "and", "care", "the", "a", "of", "about", "more", "learn"}
def names_target(anchor, page):
    """True when the anchor shares a meaningful word with the target page's H1."""
    words = lambda t: {w for w in re.findall(r"[a-z]+", t.lower())} - _FILLER
    return bool(words(anchor) & words(page["h1"]))

def ld_nodes(obj, out):
    """Every dict in a JSON-LD tree, depth first."""
    if isinstance(obj, dict):
        out.append(obj)
        for v in obj.values():
            ld_nodes(v, out)
    elif isinstance(obj, list):
        for v in obj:
            ld_nodes(v, out)
    return out

# 8a. The clinic phone is visible as text in the home hero, next to the Call
#     and WhatsApp buttons, in the same obfuscated form the rest of the page uses.
hero = re.search(r'<section class="hero".*?</section>', index, re.S)
check(hero is not None, "index.html: hero section missing")
if hero:
    h = hero.group(0)
    actions = re.search(r'<div class="hero-actions">(.*?)</div>', h, re.S)
    buttons = re.findall(r'<a [^>]*class="btn [^"]*"[^>]*>', actions.group(1)) if actions else []
    check(any('data-obf-href="tel"' in b for b in buttons), "index.html: hero lost its Call Clinic button")
    check(any('data-obf-href="wa"' in b for b in buttons), "index.html: hero lost its WhatsApp button")
    shown = [text_of(m) for m in re.findall(r'data-obf="phone"[^>]*>([^<]*)<', h)]
    check(home_display in shown, f"index.html: hero does not show the phone number {home_display} as text")
    check(ent(home_display) in h, "index.html: hero phone is not entity-encoded like the rest of the page")
    actions_to_phone = re.search(r'class="hero-actions".*?</div>\s*<p class="hero-phone">.*?data-obf="phone"', h, re.S)
    check(actions_to_phone is not None, "index.html: hero phone text does not sit directly under the hero buttons")

# 8a2. The stylesheet never hides the hero phone line: no rule for it sets
#      display none or visibility hidden, and the reduced-motion override that
#      makes the animated hero lines visible includes it.
css = (ROOT / "styles.css").read_text(encoding="utf-8")
for sel, body in re.findall(r"([^{}]*\.hero-phone[^{}]*)\{([^{}]*)\}", css):
    check(not re.search(r"display\s*:\s*none|visibility\s*:\s*hidden|font-size\s*:\s*0(?![.\d])|clip(?:-path)?\s*:", body),
          f"styles.css: rule '{sel.strip()}' hides the hero phone")
reduced = re.search(r"@media \(prefers-reduced-motion: reduce\) \{(.*?)\n\}", css, re.S)
check(reduced is not None and re.search(r"\.hero-phone[^{]*\{\s*opacity: 1 !important;", reduced.group(1)) is not None,
      "styles.css: reduced-motion override does not make the hero phone visible")
anim = re.search(r"([^{}]*\.hero-phone[^{}]*)\{[^{}]*opacity: 0;[^{}]*animation: heroReveal[^{}]*forwards;[^{}]*\}", css)
check(anim is not None, "styles.css: hero phone does not use the heroReveal entrance")
keyframes = re.search(r"@keyframes heroReveal \{(.*?)\n\}", css, re.S)
check(keyframes is not None and re.search(r"to \{[^}]*opacity: 1;", keyframes.group(1)) is not None,
      "styles.css: heroReveal does not end at full opacity")
fixed_zero = [sel for sel, body in re.findall(r"([^{}]*\.hero-phone[^{}]*)\{([^{}]*)\}", css)
              if re.search(r"opacity\s*:\s*0(?![.\d])", body) and not re.search(r"animation: heroReveal [^;]*forwards;", body)]
check(not fixed_zero, f"styles.css: hero phone left at opacity 0 by {fixed_zero}")

# 8b. Home links every specialty page from the services section and from the
#     footer, each with descriptive anchor text.
services = re.search(r'<section class="services" id="services">.*?</section>', index, re.S)
footer = re.search(r"<footer>.*?</footer>", index, re.S)
check(services is not None and footer is not None, "index.html: services section or footer missing")
for page in gen.PAGES:
    for label, block in (("services section", services), ("footer", footer)):
        if not block:
            continue
        anchors = [text_of(t) for t in re.findall(r'<a [^>]*href="/' + page["slug"] + r'"[^>]*>(.*?)</a>', block.group(0), re.S)]
        check(anchors, f"index.html: {label} does not link /{page['slug']}")
        for a in anchors:
            check(a.lower() not in GENERIC_ANCHORS and len(a.split()) >= 2 and names_target(a, page),
                  f"index.html: {label} anchor '{a}' for /{page['slug']} does not describe the page")

# 8c. Every specialty page links the other three from a Related care block in
#     the article body, with the target page's H1 as anchor text, and not itself.
for page in gen.PAGES:
    html = SITE_PAGES[f"/{page['slug']}"]
    related = re.search(r'<section class="article-section related-care" aria-labelledby="related-heading">.*?</section>', html, re.S)
    check(related is not None, f"{page['slug']}: no Related care block")
    if not related:
        continue
    block = related.group(0)
    check(f'href="/{page["slug"]}"' not in block, f"{page['slug']}: Related care links the page to itself")
    for other in gen.PAGES:
        if other is page:
            continue
        anchors = [text_of(t) for t in re.findall(r'<a [^>]*href="/' + other["slug"] + r'"[^>]*>(.*?)</a>', block, re.S)]
        check(other["h1"] in anchors, f"{page['slug']}: Related care does not link /{other['slug']} as '{other['h1']}'")
    check(block.count("<a ") == len(gen.PAGES) - 1, f"{page['slug']}: Related care has links other than the three sibling pages")

# 8d. Per-page metadata and structured data on all five pages.
ROBOTS_REQUIRED = {"index", "follow", "max-image-preview:large", "max-snippet:-1"}
for route, html in SITE_PAGES.items():
    url = gen.SITE + route
    check(html != "", f"{route}: page missing")
    if not html:
        continue
    title = _h.unescape(re.search(r"<title>(.*?)</title>", html).group(1))
    desc = _h.unescape(re.search(r'<meta name="description" content="([^"]*)"', html).group(1))
    check(len(title) <= 63, f"{route}: title {len(title)} chars (max 63)")
    check(len(desc) <= 160, f"{route}: description {len(desc)} chars (max 160)")
    for prop in ("og:description", "twitter:description"):
        m = re.search(r'(?:property|name)="' + prop + r'" content="([^"]*)"', html)
        check(m is not None and len(_h.unescape(m.group(1))) <= 160, f"{route}: {prop} missing or over 160 chars")
    loc = re.search(r'<meta property="og:locale" content="([^"]*)"', html)
    check(loc is not None and loc.group(1) == "en_IN", f"{route}: og:locale is not en_IN")
    site_name = re.search(r'<meta property="og:site_name" content="([^"]*)"', html)
    check(site_name is not None and _h.unescape(site_name.group(1)) == gen._HOME_WEBSITE["name"], f"{route}: og:site_name is not the site name")
    robots = re.search(r'<meta name="robots" content="([^"]*)"', html)
    check(robots is not None and ROBOTS_REQUIRED <= {d.strip() for d in robots.group(1).split(",")},
          f"{route}: robots meta lacks {sorted(ROBOTS_REQUIRED)}")
    canon = re.search(r'<link rel="canonical" href="([^"]*)"', html)
    ogurl = re.search(r'<meta property="og:url" content="([^"]*)"', html)
    check(canon is not None and ogurl is not None and canon.group(1) == ogurl.group(1) and canon.group(1).startswith(gen.SITE),
          f"{route}: canonical and og:url differ or are not absolute")
    check(len(re.findall(r"<h1[\s>]", html)) == 1, f"{route}: not exactly one H1")
    # Structured data: every block parses and every bare {"@id": ...} reference
    # resolves to a node defined on this same page.
    defined, refs = set(), []
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            data = json.loads(raw)
        except ValueError as e:
            check(False, f"{route}: JSON-LD does not parse ({e})")
            continue
        for node in ld_nodes(data, []):
            if "@id" in node and len(node) == 1:
                refs.append(node["@id"])
            elif "@id" in node:
                defined.add(node["@id"])
    check(defined, f"{route}: no JSON-LD nodes")
    for r in refs:
        check(r in defined, f"{route}: JSON-LD reference {r} is not defined on this page")
    check('"priceRange": "$' not in html and '"priceRange":"$' not in html, f"{route}: priceRange uses a dollar sign")

# 8e. Home structured data: dateModified is the home page's sitemap lastmod,
#     and priceRange, if present, is stated in rupees.
home_nodes = ld_nodes(home_ld, [])
home_wp = next(n for n in home_nodes if n.get("@type") == "MedicalWebPage")
sm_urls = {m.group(1): m.group(0) for m in re.finditer(r"<url>\s*<loc>([^<]+)</loc>.*?</url>", sitemap, re.S)}
home_entry = sm_urls.get(gen.SITE + "/", "")
home_lastmod = re.search(r"<lastmod>([^<]+)</lastmod>", home_entry)
check(home_lastmod is not None and home_wp.get("dateModified") == home_lastmod.group(1),
      f"index.html: MedicalWebPage dateModified {home_wp.get('dateModified')} is not the sitemap lastmod")
# priceRange stays out: the site publishes one fee, for the check-up, and the
# check-up Offer already carries it; a range would state fees the site does not.
check(not any("priceRange" in n for n in home_nodes), "index.html: priceRange present; the site publishes no fee range")

# 8e2. Opening hours are the clinic's published schedule, pinned literally so
#      no edit can change them without changing this line on purpose.
PUBLISHED_HOURS = [
    (["Monday", "Wednesday", "Thursday", "Friday", "Saturday"], "09:00", "13:00"),
    (["Monday", "Wednesday", "Thursday", "Friday", "Saturday"], "16:30", "19:00"),
    (["Sunday"], "09:00", "15:00"),
]
check([(s_["dayOfWeek"], s_["opens"], s_["closes"]) for s_ in home_clinic["openingHoursSpecification"]] == PUBLISHED_HOURS,
      "index.html: openingHoursSpecification differs from the published schedule")

# 8e3. Dates track content. For each page, find the last commit that moved its
#      lastmod. If the page file has changed since that commit, its lastmod
#      must be today (the change is being made now). No lastmod may move
#      backwards from the committed sitemap or sit in the future. The home
#      dateModified equals the home lastmod (8e). Every comparison is against
#      git history, so a squash merge made on a later day still passes: the
#      squash commit moves the lastmod and changes the page together.
import subprocess, datetime as _dt
def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)
def lastmods(xml):
    return {m.group(1): m.group(2) for m in re.finditer(r"<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>", xml)}
today = _dt.date.today().isoformat()
now_lm = lastmods(sitemap)
sm_history = git("log", "--format=%H", "--", "sitemap.xml").stdout.split()
check(sm_history != [], "git history for sitemap.xml unavailable")
if sm_history:
    snap = {c: lastmods(git("show", f"{c}:sitemap.xml").stdout) for c in sm_history}
    at_head = lastmods(git("show", "HEAD:sitemap.xml").stdout)
    route_file = {"/": "index.html", **{f"/{p['slug']}": f"{p['slug']}.html" for p in gen.PAGES}}
    for route, name in route_file.items():
        loc_ = gen.SITE + route
        moved = None
        for i, c in enumerate(sm_history):
            before = snap[sm_history[i + 1]] if i + 1 < len(sm_history) else {}
            if snap[c].get(loc_) != before.get(loc_):
                moved = c
                break
        changed_since = moved is None or git("diff", "--quiet", moved, "--", name).returncode == 1
        check(not changed_since or now_lm.get(loc_) == today,
              f"sitemap.xml: {name} changed after its lastmod was last moved, so its lastmod must be today ({today})")
        check(loc_ not in at_head or now_lm.get(loc_, "") >= at_head[loc_],
              f"sitemap.xml: lastmod for {route} moved backwards from the committed {at_head.get(loc_)}")
        check(now_lm.get(loc_, "9999") <= today, f"sitemap.xml: lastmod for {route} is in the future")

# 8f. Sitemap: exactly the five pages, each with an ISO lastmod, and the home
#     entry keeps its image extension entry for the doctor's photo.
expected_locs = {gen.SITE + "/"} | {f"{gen.SITE}/{p['slug']}" for p in gen.PAGES}
check(set(sm_urls) == expected_locs, f"sitemap.xml lists {sorted(set(sm_urls) ^ expected_locs)} unexpectedly")
for loc_, entry in sm_urls.items():
    check(re.search(r"<lastmod>\d{4}-\d{2}-\d{2}</lastmod>", entry) is not None, f"sitemap.xml: {loc_} has no ISO lastmod")
import xml.etree.ElementTree as ET
_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9", "image": "http://www.google.com/schemas/sitemap-image/1.1"}
try:
    _tree = ET.fromstring(sitemap.encode("utf-8"))
except ET.ParseError as e:
    _tree = None
    check(False, f"sitemap.xml does not parse ({e})")
if _tree is not None:
    home_url = [u for u in _tree.findall("sm:url", _NS) if (u.findtext("sm:loc", "", _NS) or "").strip() == gen.SITE + "/"]
    images = [i.findtext("image:loc", "", _NS).strip() for u in home_url for i in u.findall("image:image", _NS)]
    check(f"{gen.SITE}/doctor-photo.jpg" in images, "sitemap.xml: home url lacks an image:image entry for the doctor's photo")

if failures:
    print("\n".join(f"FAIL {f}" for f in failures))
    print(f"{len(failures)} of {checks} checks failed"); sys.exit(1)
print(f"ok: {checks} checks passed; {len(gen.PAGES)} specialty pages and the home page verified against index.html")
