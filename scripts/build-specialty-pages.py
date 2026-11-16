#!/usr/bin/env python3
"""Generate the specialty pages from one template so header, footer, contact
obfuscation, styles and structured data never drift from index.html.

Run from the repo root:  python3 scripts/build-specialty-pages.py
Every claim below is drawn from index.html (services, FAQ, timings, fees).
Nothing here states an outcome or a fee the home page does not state.
"""
import json, html, pathlib, datetime, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://dranilkumardhar.com"
CSS_VERSION = "202611142"
JS_VERSION = "20261114"   # script.js is browser-cached for a week, like styles.css
TODAY = datetime.date.today().isoformat()

# ---- Facts come from index.html, never from this file ----------------------
# The home page's structured data is the clinic's single statement of its
# phone, address, opening hours and the one published fee. The pages below
# are rendered from those values, so a change on the home page is a change
# here on the next run, and a value that is not on the home page cannot appear.
INDEX_HTML = (ROOT / "index.html").read_text(encoding="utf-8")
_HOME_GRAPH = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', INDEX_HTML, re.S).group(1))["@graph"]
_HOME_CLINIC = next(n for n in _HOME_GRAPH if n["@type"] == "MedicalClinic")
_HOME_PHYSICIAN = next(n for n in _HOME_GRAPH if n["@type"] == "Physician")
_HOME_WEBSITE = next(n for n in _HOME_GRAPH if n["@type"] == "WebSite")

TELEPHONE = _HOME_CLINIC["telephone"]                       # +919419190388
_DIGITS = TELEPHONE.removeprefix("+91")                     # 9419190388
PHONE_DISPLAY = f"{_DIGITS[:5]} {_DIGITS[5:]}"              # five digits, space, five digits
EMAIL = html.unescape(re.search(r'data-obf="email">([^<]+)<', INDEX_HTML).group(1))


def entities(text: str) -> str:
    """Encode every character as a numeric entity, as index.html does for
    contact details, so the values are not trivially scraped from source."""
    return "".join(f"&#{ord(c)};" for c in text)


PHONE_ENT = entities(_DIGITS)
PHONE_DISPLAY_ENT = entities(PHONE_DISPLAY)
EMAIL_ENT = entities(EMAIL)

_GENERAL_OFFER = next(
    o for o in _HOME_CLINIC["hasOfferCatalog"]["itemListElement"]
    if o["itemOffered"]["name"] == "General Check-up"
)
FEE = f"₹{int(_GENERAL_OFFER['price']):,}"                 # formatted from the Offer price

_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _clock(t: str) -> str:
    h, m = (int(x) for x in t.split(":"))
    suffix = "AM" if h < 12 else "PM"
    h12 = h % 12 or 12
    return f"{h12}:{m:02d} {suffix}" if m else f"{h12} {suffix}"


def hours_sentence(specs: list[dict]) -> str:
    """'Monday and Wednesday to Saturday, 9 AM to 1 PM and 4:30 PM to 7 PM.
    Sunday 9 AM to 3 PM. Closed on Tuesdays.' from OpeningHoursSpecification."""
    by_day: dict[str, list[str]] = {d: [] for d in _DAYS}
    for spec in specs:
        for d in spec["dayOfWeek"]:
            by_day[d].append(f"{_clock(spec['opens'])} to {_clock(spec['closes'])}")
    # consecutive day runs with an identical schedule
    runs: list[tuple[list[str], tuple[str, ...]]] = []
    for d in _DAYS:
        sched = tuple(by_day[d])
        if runs and runs[-1][1] == sched and _DAYS.index(runs[-1][0][-1]) == _DAYS.index(d) - 1:
            runs[-1][0].append(d)
        else:
            runs.append(([d], sched))
    label = lambda days: days[0] if len(days) == 1 else f"{days[0]} to {days[-1]}"
    parts, closed = [], []
    # merge non-consecutive runs that share a schedule ("Monday and Wednesday to Saturday")
    merged: dict[tuple[str, ...], list[str]] = {}
    for days, sched in runs:
        if not sched:
            closed.extend(days)
        else:
            merged.setdefault(sched, []).append(label(days))
    for sched, labels in merged.items():
        parts.append(f"{' and '.join(labels)}, {' and '.join(sched)}." if len(sched) > 1 or len(labels) > 1
                     else f"{labels[0]} {sched[0]}.")
    if closed:
        parts.append("Closed on " + " and ".join(f"{d}s" for d in closed) + ".")
    return " ".join(parts)


HOURS = hours_sentence(_HOME_CLINIC["openingHoursSpecification"])
# The footer hours block is the home page's, verbatim.
FOOTER_HOURS_BLOCK = re.search(r"<h4>Clinic Hours</h4>(.*?)</div>", INDEX_HTML, re.S).group(1).rstrip()
ADDRESS = _HOME_CLINIC["address"]
ADDRESS_LINE = f"{ADDRESS['streetAddress']}, {ADDRESS['addressLocality']}, J&K {ADDRESS['postalCode']}"

CLINIC = {
    "@type": "MedicalClinic",
    "@id": _HOME_CLINIC["@id"],
    "name": _HOME_CLINIC["name"],
    "url": SITE,
    "telephone": TELEPHONE,
    "address": {"@type": "PostalAddress", **{k: v for k, v in ADDRESS.items() if k != "@type"}},
}
PHYSICIAN = {"@type": "Physician", "@id": _HOME_PHYSICIAN["@id"], "name": _HOME_PHYSICIAN["name"], "url": SITE}
# The WebSite node each page's MedicalWebPage is part of, defined on the page
# itself so the reference resolves without the home page's graph.
WEBSITE = {k: _HOME_WEBSITE[k] for k in ("@type", "@id", "url", "name", "publisher", "inLanguage")}

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
             "<p>An internal medicine physician looks after the health of adults as a whole rather than one organ. At this clinic that means fever and infections, respiratory problems such as cough and breathlessness, thyroid disorders, blood pressure, diabetes, heart-related risk, and the general complaints that do not fit a neat label: tiredness, weight change, poor sleep, aches that will not settle.</p><p>When one doctor sees you over time, a problem can be read in the context of your history, your reports and your other medicines, which is the advantage of having a physician rather than a different doctor for each complaint.</p>"),
            ("The general check-up",
             "<p>The clinic's general check-up costs <strong>[[FEE]]</strong> and includes a physical examination, blood pressure measurement, fasting and post-meal blood sugar testing, cholesterol screening and a detailed consultation with personalised advice. If you have not seen a doctor in a while, have a family history of diabetes or heart disease, or want a baseline, ask when you book whether the check-up is the right visit for you.</p>"),
            ("What to bring",
             "<p>Any previous medical reports, a list of the medicines you take (or the strips themselves), and, if you have them, recent blood test results. If your check-up includes a fasting blood sugar test, ask the clinic when you book how long to fast and what to do about any medicines you take that morning; do not stop a medicine on your own.</p>"),
            ("When not to wait for an appointment",
             "<p>Chest pain, sudden weakness or numbness on one side, difficulty speaking, severe breathlessness, or confusion with a fever are emergencies. Go to the nearest hospital emergency department rather than waiting for a clinic slot.</p>"),
        ],
        "faqs": [
            ("How do I book a consultation?", "By phone, WhatsApp or SMS on [[PHONE]], with your name and preferred time. The clinic staff confirm the appointment."),
            ("What does the general check-up cost?", "[[FEE]]. It includes the examination, blood pressure, fasting and post-meal blood sugar, cholesterol screening and the consultation."),
            ("Which days is the clinic open?", "[[HOURS]]"),
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
             "<p>Diabetes is managed over years, not in one visit. The clinic tracks <strong>HbA1c</strong> (the three-month average of your blood sugar) at regular intervals, checks fasting and post-meal sugar, reviews your medicines and adjusts insulin doses when readings call for it. Diet planning is personalised to what you eat.</p><p>Just as important is long-term prevention of complications. Diabetes can affect the heart, kidneys, eyes and feet when sugar stays high for years, and the doctor advises which checks are due, which can help catch problems early. That is the point of regular follow-up.</p>"),
            ("Who should come",
             "<p>Anyone already diagnosed with diabetes who wants one doctor to follow their control over time. Anyone with symptoms that suggest it: unusual thirst, passing urine often, tiredness, blurred vision, wounds that heal slowly, or unexplained weight loss. And anyone with a strong family history who wants to be screened; the general check-up includes fasting and post-meal blood sugar.</p>"),
            ("What to bring",
             "<p>Your glucometer log if you keep one, recent HbA1c and blood reports, the medicines or insulin you use with their doses, and a note of any low-sugar episodes. If your visit includes a fasting test, ask the clinic when you book how long to fast and what to do about your diabetes medicines or insulin that morning; skipping a meal while on them can drop your sugar too low, so do not decide this alone.</p>"),
            ("The pharmacy on site",
             "<p>Prescribed medicines and insulin are available from the clinic's own pharmacy immediately after the consultation, so a change in dose does not mean a second trip.</p>"),
        ],
        "faqs": [
            ("Does Dr. Dhar treat Type 1 as well as Type 2 diabetes?", "Yes. The clinic manages both, including insulin adjustment for patients who use it."),
            ("How often should HbA1c be checked?", "That depends on how stable your control is; the doctor sets the interval at your visit. The clinic tracks it regularly as part of ongoing care."),
            ("What does a diabetes consultation cost?", "Ask when you book on [[PHONE]]. The general check-up, which includes fasting and post-meal blood sugar, is [[FEE]]."),
        ],
        "specialty": "Diabetology",
    },
    {
        "slug": "bp-and-heart-care-jammu",
        "title": "Blood Pressure and Heart Care in Jammu | Dr. Anil Kumar Dhar",
        "description": "Hypertension treatment and heart risk care in Jammu with Dr. Anil Kumar Dhar, MBBS MD DNB: BP monitoring, cholesterol management and cardiovascular risk review.",
        "h1": "Blood Pressure and Heart Care in Jammu",
        "lede": "High blood pressure rarely announces itself, which is why it is worth having measured. Dr. Anil Kumar Dhar treats hypertension, manages cholesterol and assesses cardiovascular risk at his internal medicine clinic on Canal Road, Jammu, with medication chosen on evidence-based protocols.",
        "about_condition": "Hypertension",
        "sections": [
            ("What blood pressure care involves here",
             "<p>Blood pressure is measured at the visit, and your readings at home are useful to bring if you take them. If treatment is needed, the doctor starts or adjusts medicines and reviews the result at follow-up. Cholesterol is checked and managed alongside, because blood pressure and cholesterol are two of the main things that decide the risk to the heart.</p><p>A cardiovascular risk assessment puts these together with your age, sugar, weight, smoking and family history to estimate where you stand and what would change it most.</p>"),
            ("Who should come",
             "<p>Anyone told their blood pressure is high, anyone on blood pressure or cholesterol medicine who wants it reviewed, and anyone with a family history of heart disease, stroke or diabetes who has not been assessed. Headaches, breathlessness on exertion, or swelling of the feet are worth a visit.</p>"),
            ("What to bring",
             "<p>Your home blood pressure readings if you have them, any ECG, echo or blood reports, and the medicines you take. Avoid tea, coffee or smoking in the half hour before the visit so the reading is a fair one.</p>"),
            ("When it is an emergency",
             "<p>Chest pain or pressure, pain spreading to the arm or jaw, sudden breathlessness, or sudden weakness or slurred speech are not clinic matters. Go to the nearest hospital emergency department at once.</p>"),
        ],
        "faqs": [
            ("Does the clinic do ECGs?", "Ask when you book on [[PHONE]]. The clinic offers lab collection on site; the doctor will tell you which tests you need and where."),
            ("Can I stop my blood pressure medicine if my readings are normal?", "Not on your own. Normal readings may be the medicine working; any change should be made by the doctor after a review."),
            ("What does a consultation cost?", "Ask when you book. The general check-up, which includes blood pressure and cholesterol screening, is [[FEE]]."),
        ],
        "specialty": "InternalMedicine",
    },
    {
        "slug": "vaccination-jammu",
        "title": "Adult Vaccination in Jammu | Dr. Anil Kumar Dhar",
        "description": "Adult vaccination in Jammu at Dr. Anil Kumar Dhar's clinic: annual flu, pneumonia, hepatitis B, typhoid and other recommended vaccines under proper cold chain.",
        "h1": "Adult Vaccination in Jammu",
        "lede": "Vaccines are not only for children. Dr. Anil Kumar Dhar's clinic on Canal Road, Jammu, offers adult immunisation including the annual flu vaccine, pneumonia vaccine, hepatitis B, typhoid and other recommended vaccines, stored under proper cold chain.",
        "about_condition": None,
        "sections": [
            ("Vaccines offered",
             "<p>The annual <strong>influenza</strong> vaccine, the <strong>pneumonia</strong> vaccine, <strong>hepatitis B</strong>, <strong>typhoid</strong>, and other vaccines recommended for adults according to age, health conditions and travel. The doctor advises which apply to you; not everyone needs every vaccine.</p>"),
            ("Who benefits most",
             "<p>Adults over 60, people with diabetes, heart or lung disease, or a weakened immune system, for whom flu and pneumonia are far more dangerous than for a healthy young adult. People who missed hepatitis B as children. Anyone travelling to areas where typhoid is common. And anyone who simply wants their adult vaccinations up to date.</p>"),
            ("What to bring",
             "<p>Any record of previous vaccinations, and a note of allergies or reactions to past vaccines. Tell the doctor if you are unwell on the day, pregnant, or on medicines that affect immunity; the vaccine may be given or deferred accordingly.</p>"),
            ("Cold chain",
             "<p>Vaccines have to be kept at the right temperature from manufacture to injection, or they can lose their effect. The clinic stores its vaccines under proper cold chain.</p>"),
        ],
        "faqs": [
            ("When should I get the flu vaccine?", "Once a year. Ask the clinic about timing for the current season when you book on [[PHONE]]."),
            ("How do I arrange a vaccination?", "Book by phone, WhatsApp or SMS on [[PHONE]] and say which vaccine you are asking about, so the clinic can confirm it for your visit."),
            ("What do vaccines cost?", "Ask when you book on [[PHONE]]."),
        ],
        "specialty": "InternalMedicine",
    },
    {
        "slug": "thyroid-doctor-jammu",
        "title": "Thyroid Doctor in Jammu | Dr. Anil Kumar Dhar",
        "description": "Thyroid care in Jammu with Dr. Anil Kumar Dhar, MBBS MD DNB, internal medicine physician for 30+ years. Lab collection and pharmacy on site. Canal Road clinic.",
        "h1": "Thyroid Treatment in Jammu",
        "lede": "Dr. Anil Kumar Dhar is an internal medicine physician (MBBS, MD, DNB) who treats thyroid disorders at his clinic on Canal Road, Bhagwati Nagar, Jammu. Blood samples are collected at the clinic, and prescribed medicines are available from its own pharmacy.",
        "about_condition": "Thyroid disease",
        "sections": [
            ("How thyroid problems are found and treated",
             "<p>The thyroid is a small gland in the neck that sets the pace of the body. Too little thyroid hormone slows things down; too much speeds them up. Neither can be judged from symptoms alone; the level of thyroid hormone is measured with a blood test, read together with the symptoms. A swelling or lump in the neck is a separate matter: it may need a scan even when the blood test is normal.</p><p>Treatment is usually long term, and the right dose can change with time. That is why thyroid care is a matter of regular follow-up rather than a single visit, and why it helps to see one doctor who knows your earlier reports.</p>"),
            ("Who should come",
             "<p>Anyone already on thyroid medicine who wants it reviewed. Anyone with complaints that can point to the thyroid: tiredness that does not lift, a change in weight without a reason, feeling cold or hot when others do not, hair fall, a swelling in the neck, or a fast or irregular heartbeat. And anyone with thyroid disease in the family who has not been tested.</p>"),
            ("What to bring",
             "<p>Your previous thyroid reports, in order if you can, and the thyroid medicine you take with its dose. Bring your other medicines too, because some affect the thyroid or its tests. Do not stop the medicine or change the dose on your own before the visit.</p>"),
            ("Thyroid with diabetes or blood pressure",
             "<p>Many patients have more than one long-term condition. An internal medicine physician looks at them together, so that the treatment for one does not work against another. The clinic also provides <a href=\"/diabetes-doctor-jammu\">diabetes care</a> and <a href=\"/bp-and-heart-care-jammu\">blood pressure and heart care</a>.</p>"),
            ("Tests and medicines",
             "<p>Which blood tests are needed depends on your symptoms and your earlier reports. The clinic offers lab collection on site, and prescribed medicines are available from the in-house pharmacy immediately after the consultation.</p>"),
        ],
        "faqs": [
            ("Is Dr. Dhar a thyroid specialist?", "He is an internal medicine physician (MBBS, MD, DNB). Thyroid disorders are among the conditions he treats at the clinic."),
            ("Can I give the blood sample at the clinic?", "The clinic offers lab collection on site. Ask when you book on [[PHONE]] which tests you need and how to prepare for them."),
            ("What does a thyroid consultation cost?", "Ask when you book on [[PHONE]]."),
            ("Which days is the clinic open?", "[[HOURS]]"),
        ],
        "specialty": "InternalMedicine",
        "relies_on": ["thyroid disorders", "Lab Collection Service", "In-house Pharmacy", "diabetes", "hypertension"],
    },
    {
        "slug": "fever-doctor-jammu",
        "title": "Fever Doctor in Jammu | Dr. Anil Kumar Dhar",
        "description": "Fever and infection care in Jammu with Dr. Anil Kumar Dhar, MBBS MD DNB, internal medicine physician for 30+ years. Lab collection on site. Canal Road clinic.",
        "h1": "Fever and Infection Treatment in Jammu",
        "lede": "Most fevers settle in a few days. Some do not, and those need a doctor to find the cause. Dr. Anil Kumar Dhar, an internal medicine physician (MBBS, MD, DNB), sees adults with fever and infections at his clinic on Canal Road, Bhagwati Nagar, Jammu.",
        "about_condition": "Fever",
        "sections": [
            ("How a fever is assessed",
             "<p>Fever is a sign, not a diagnosis. What matters is how long it has lasted, how it rises and falls, and what else you feel. When the cause is not clear from that, blood or urine tests may be needed; the clinic offers lab collection on site.</p><p>Treatment depends on the cause. Antibiotics work only against bacteria, so not every fever needs one. Prescribed medicines are available from the clinic's own pharmacy immediately after the consultation.</p>"),
            ("When to see the doctor",
             "<p>A fever that lasts more than two or three days, or one that goes and comes back. Fever with a cough or breathlessness, burning when you pass urine, a rash, or severe headache and body pain. And any fever in an older adult or in someone with diabetes, heart disease or lung disease, for whom an infection can turn serious faster.</p>"),
            ("What to bring",
             "<p>A note of your temperature readings and when you took them, the medicines you have already taken for the fever, and any recent reports. Bring the list of medicines you take regularly as well.</p>"),
            ("Vaccines against typhoid and flu",
             "<p>Some fevers can be prevented. The clinic offers the typhoid vaccine and the annual flu vaccine for adults; see <a href=\"/vaccination-jammu\">adult vaccination</a>.</p>"),
            ("When not to wait for an appointment",
             "<p>Confusion or unusual drowsiness, severe breathlessness, chest pain, a fit, a stiff neck with a severe headache, or bleeding are emergencies, whether the fever is high or mild. Go to the nearest hospital emergency department rather than waiting for a clinic slot.</p>"),
        ],
        "faqs": [
            ("Do I need a blood test for a fever?", "Not always. It depends on your symptoms and the examination. If a test is needed, the clinic offers lab collection on site."),
            ("Can I get the typhoid vaccine at the clinic?", "Yes. The clinic offers the typhoid vaccine for adults. Book by phone, WhatsApp or SMS on [[PHONE]]."),
            ("How do I book a consultation?", "By phone, WhatsApp or SMS on [[PHONE]], with your name and preferred time. The clinic staff confirm the appointment."),
            ("Which days is the clinic open?", "[[HOURS]]"),
        ],
        "specialty": "InternalMedicine",
        "relies_on": ["fever, infections", "Lab Collection Service", "In-house Pharmacy", "annual flu vaccine", "typhoid", "healthcare for adults"],
    },
    {
        "slug": "internal-medicine-physician-jammu-kashmir",
        "title": "Internal Medicine Doctor, Jammu & Kashmir | Dr. Anil Kumar Dhar",
        "description": "Dr. Anil Kumar Dhar, MBBS MD DNB, internal medicine physician in Jammu for 30+ years. Patients visit from across Jammu and Kashmir. Lab collection, pharmacy.",
        "h1": "Internal Medicine Physician in Jammu and Kashmir",
        "lede": "Dr. Anil Kumar Dhar is an internal medicine physician (MBBS, MD, DNB) who has practised in Jammu for more than 30 years. Patients come to his clinic on Canal Road from Jammu city and from across Jammu and Kashmir, for everyday illness, long-term conditions and health check-ups.",
        "about_condition": None,
        "sections": [
            ("What an internal medicine physician treats",
             "<p>An internal medicine physician looks after the health of adults as a whole. At this clinic that covers <a href=\"/general-physician-jammu\">general physician care and check-ups</a>, <a href=\"/diabetes-doctor-jammu\">diabetes</a>, <a href=\"/bp-and-heart-care-jammu\">blood pressure and heart care</a>, <a href=\"/thyroid-doctor-jammu\">thyroid disorders</a>, <a href=\"/fever-doctor-jammu\">fever and infections</a>, respiratory problems such as cough and breathlessness, and <a href=\"/vaccination-jammu\">adult vaccination</a>.</p>"),
            ("If you are travelling to the clinic",
             "<p>Book before you set out: call or WhatsApp [[PHONE]] with your name and preferred time, and the clinic staff confirm the appointment. Bring your previous reports and the medicines you take, so that the doctor has your full history at the visit.</p><p>The clinic has a lab collection service and its own pharmacy, so a blood sample can be given and prescribed medicines collected at the clinic. The opening hours include a weekend day, which suits patients who cannot travel on a working day.</p>"),
            ("Where the clinic is",
             "<p>The address is <strong>[[ADDRESS]]</strong>. If you are coming for the first time, call [[PHONE]] for directions; the reception also advises on parking.</p>"),
            ("Check-ups",
             "<p>The clinic's general check-up costs <strong>[[FEE]]</strong>. The <a href=\"/general-physician-jammu\">general physician page</a> lists what it covers and what to bring.</p>"),
            ("At the clinic",
             "<p>An air-conditioned waiting area, wheelchair access, an in-house pharmacy and a lab collection service. The clinic accepts cash and all UPI apps.</p>"),
        ],
        "faqs": [
            ("Do I need an appointment if I am coming from outside Jammu city?", "Book before you travel, by phone, WhatsApp or SMS on [[PHONE]]. The clinic staff confirm the appointment."),
            ("Which days is the clinic open?", "[[HOURS]]"),
            ("Can I get tests and medicines on the same visit?", "The clinic offers lab collection on site, and prescribed medicines are available from the in-house pharmacy after the consultation."),
            ("Is the clinic wheelchair accessible?", "Yes. The clinic is wheelchair accessible."),
        ],
        "specialty": "InternalMedicine",
        "relies_on": ["Bhagwati Nagar", "Canal Road", "30+ years", "thyroid disorders", "respiratory problems", "fever, infections",
                      "AC Waiting Area", "Wheelchair Accessible", "In-house Pharmacy", "Lab Collection Service",
                      "Contact Reception for Parking Advice", "cash payment and all UPI apps"],
    },
    {
        "slug": "longevity-care-jammu",
        "title": "Longevity Doctor in Jammu | Dr. Anil Kumar Dhar",
        "description": "Longevity and preventive care in Jammu with Dr. Anil Kumar Dhar, MBBS MD DNB, internal medicine physician for 30+ years. Healthy ageing, check-ups, vaccines.",
        "h1": "Longevity and Preventive Care in Jammu",
        "lede": "Longevity care is preventive medicine with a long view: finding the risks to your health early and keeping them under control for years. Dr. Anil Kumar Dhar, an internal medicine physician (MBBS, MD, DNB) with more than 30 years of practice, provides it at his clinic on Canal Road, Bhagwati Nagar, Jammu.",
        "about_condition": None,
        "sections": [
            ("What longevity care means at this clinic",
             "<p>The clinic's longevity care focuses on healthy ageing, metabolic health, nutritional guidance and stress management. It is not one treatment. It is a way of looking after an adult over many years, so that the common long-term conditions are prevented where they can be, found early where they cannot, and kept under control once they are found.</p><p>No doctor can promise a longer life. What medicine can do is lower the known risks, and that is the aim.</p>"),
            ("The conditions that matter most",
             "<p>For most adults the largest risks build up without symptoms: raised blood pressure, raised blood sugar and raised cholesterol. Each can be measured, and each can be treated. The clinic provides <a href=\"/bp-and-heart-care-jammu\">blood pressure and heart care</a>, <a href=\"/diabetes-doctor-jammu\">diabetes care</a> and <a href=\"/thyroid-doctor-jammu\">thyroid treatment</a>, and one physician looks at them together.</p>"),
            ("Where to start",
             "<p>A baseline comes first. The clinic's general check-up costs <strong>[[FEE]]</strong>; the <a href=\"/general-physician-jammu\">general physician page</a> lists what it covers and what to bring. From the results, the doctor advises what to change, what to treat and when to come back.</p>"),
            ("Food, activity, sleep and stress",
             "<p>Medicines are one part of the plan. What you eat, how much you move, how you sleep and how you handle stress all affect blood pressure, sugar and weight. The clinic's longevity care includes nutritional guidance and stress management, with advice fitted to you.</p>"),
            ("Vaccines for adults",
             "<p>Preventing infections is part of ageing well, more so for older adults and for people with diabetes, heart disease or lung disease. The clinic offers <a href=\"/vaccination-jammu\">adult vaccination</a>, including the annual flu vaccine and the pneumonia vaccine.</p>"),
        ],
        "faqs": [
            ("Who is longevity care for?", "Any adult who wants to look after their long-term health, with or without an existing condition. It is useful if you have a family history of diabetes or heart disease, or have not had a check-up in a while."),
            ("Is longevity care a separate treatment?", "No. It is preventive care by an internal medicine physician: check-ups, control of blood pressure, sugar and cholesterol, advice on food and stress, and vaccination."),
            ("How do I book a consultation?", "By phone, WhatsApp or SMS on [[PHONE]], with your name and preferred time. The clinic staff confirm the appointment."),
            ("Which days is the clinic open?", "[[HOURS]]"),
        ],
        "specialty": "InternalMedicine",
        "relies_on": ["Longevity Care", "healthy aging", "nutritional guidance", "stress management", "cholesterol screening",
                      "pneumonia vaccine", "annual flu vaccine", "30+ years"],
    },
    {
        "slug": "in-house-pharmacy-jammu",
        "title": "Clinic with In-house Pharmacy in Jammu | Dr. Anil Kumar Dhar",
        "description": "Dr. Anil Kumar Dhar's clinic on Canal Road, Jammu, has its own pharmacy. Prescribed medicines are available immediately after your consultation.",
        "h1": "In-house Pharmacy at the Clinic in Jammu",
        "lede": "Dr. Anil Kumar Dhar's clinic on Canal Road, Bhagwati Nagar, Jammu, has its own pharmacy. The medicines the doctor prescribes are available immediately after your consultation, which saves an extra trip to an outside chemist.",
        "about_condition": None,
        "sections": [
            ("How it works",
             "<p>You see the doctor, and the pharmacy at the clinic dispenses the medicines on your prescription before you leave. If anything about a medicine is not clear, such as when to take it or for how long, you can ask at the clinic while you are still there.</p>"),
            ("Why it helps",
             "<p>You do not have to look for the medicines elsewhere after the visit. That helps patients who find a second stop difficult: older adults, people who are unwell, and people who have travelled to reach the clinic.</p>"),
            ("Long-term medicines",
             "<p>Patients with <a href=\"/diabetes-doctor-jammu\">diabetes</a>, <a href=\"/bp-and-heart-care-jammu\">blood pressure</a> or <a href=\"/thyroid-doctor-jammu\">thyroid</a> conditions take medicines for years, and the dose can change at a follow-up visit. Bring the medicines you take now, or their strips, so that the doctor can check them against the new prescription.</p>"),
            ("Tests at the clinic",
             "<p>The clinic also offers a lab collection service, so a blood sample can be given at the clinic when the doctor asks for a test.</p>"),
            ("Paying",
             "<p>The clinic accepts cash and all UPI apps.</p>"),
        ],
        "faqs": [
            ("Are all prescribed medicines available at the clinic?", "The pharmacy stocks the medicines the doctor prescribes, and they are available immediately after your consultation."),
            ("Can I buy medicines without seeing the doctor?", "The pharmacy dispenses medicines prescribed at the clinic. For anything else, ask the clinic on [[PHONE]]."),
            ("How can I pay?", "The clinic accepts cash and all UPI apps."),
            ("Which days is the clinic open?", "[[HOURS]]"),
        ],
        "specialty": "InternalMedicine",
        "relies_on": ["In-house Pharmacy", "Fully stocked on-site pharmacy", "immediately after your consultation",
                      "outside chemist", "Lab Collection Service", "cash payment and all UPI apps"],
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
        WEBSITE,
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


def fill(text: str) -> str:
    return text.replace("[[FEE]]", FEE).replace("[[PHONE]]", PHONE_DISPLAY).replace("[[HOURS]]", HOURS).replace("[[ADDRESS]]", html.escape(ADDRESS_LINE))


def render(page: dict) -> str:
    page = {**page,
            "lede": fill(page["lede"]),
            "sections": [(h, fill(b)) for h, b in page["sections"]],
            "faqs": [(fill(q), fill(a)) for q, a in page["faqs"]]}
    url = f"{SITE}/{page['slug']}"
    sections = "\n".join(
        f'            <section class="article-section">\n                <h2>{esc(h)}</h2>\n                {b}\n            </section>'
        for h, b in page["sections"]
    )
    related = "\n".join(
        f'                    <li><a href="/{other["slug"]}">{esc(other["h1"])}</a></li>'
        for other in PAGES if other["slug"] != page["slug"]
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
                <a href="/#booking">Book Appointment</a>
                <a href="/#faq">FAQ</a>
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
                <p><strong>Where:</strong> {esc(ADDRESS_LINE)}.</p>
                <p><strong>When:</strong> {HOURS}</p>
                <p><strong>Booking:</strong> call or WhatsApp <a href="tel:+91{PHONE_ENT}" data-obf-href="tel" data-obf="phone">{PHONE_DISPLAY_ENT}</a>, or send an SMS with your name and preferred time. Cash and all UPI apps accepted. In-house pharmacy and lab collection on site.</p>
            </section>

            <section class="article-section" aria-labelledby="faq-heading">
                <h2 id="faq-heading">Frequently asked questions</h2>
                <div class="faq-container">
{faqs}
                </div>
            </section>

            <section class="article-section related-care" aria-labelledby="related-heading">
                <h2 id="related-heading">Related care at the clinic</h2>
                <ul class="related-links">
{related}
                </ul>
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
                    <p class="footer-email"><a href="mailto:{EMAIL_ENT}" data-obf-href="email" data-obf="email">{EMAIL_ENT}</a></p>
                </div>
                <div class="footer-col">
                    <h3 class="footer-heading">Specialties</h3>
                    <ul class="footer-links">
                        <li><a href="/general-physician-jammu">General Physician</a></li>
                        <li><a href="/diabetes-doctor-jammu">Diabetes Care</a></li>
                        <li><a href="/bp-and-heart-care-jammu">Heart &amp; BP Care</a></li>
                        <li><a href="/vaccination-jammu">Adult Vaccination</a></li>
                        <li><a href="/thyroid-doctor-jammu">Thyroid Treatment</a></li>
                        <li><a href="/fever-doctor-jammu">Fever &amp; Infections</a></li>
                        <li><a href="/internal-medicine-physician-jammu-kashmir">Physician for Jammu and Kashmir</a></li>
                        <li><a href="/longevity-care-jammu">Longevity Care</a></li>
                        <li><a href="/in-house-pharmacy-jammu">In-house Pharmacy</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h3 class="footer-heading">Quick Links</h3>
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
                    <h3 class="footer-heading">Clinic Hours</h3>{FOOTER_HOURS_BLOCK}
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

    <script src="/script.js?v={JS_VERSION}" defer></script>
    <noscript>
        <div class="noscript-banner">
            To book an appointment, call <strong>{PHONE_DISPLAY}</strong> or email <strong>{EMAIL}</strong>
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
