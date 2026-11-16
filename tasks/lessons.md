# Lessons

One line per lesson: the mistake, the rule that prevents it, the date.

- 2026-11-14: Off-site work (a Google profile, directory listings) was proposed although CLAUDE.md records that the doctor declined it on 2026-07-05. Rule: read the Scope Decision in CLAUDE.md before proposing any work for this site.
- 2026-11-14: The sticky header changed height when script.js wrote the "Closed" text after first paint, which pushed the page down on phones and tablets. Rule: an element whose text is written by script gets its box fixed in CSS, and the header height is measured for every badge text at every breakpoint before merge.
- 2026-11-14: script.js had no version and no cache rule, so every visit re-checked it and it ran after first paint. Rule: styles.css and script.js carry the same version query and cache rule; bump both versions in index.html and scripts/build-specialty-pages.py when either file changes.
- 2026-11-14: New specialty pages may state only what index.html states. Rule: add the page to PAGES in scripts/build-specialty-pages.py, pin every phrase it relies on in section 3b of scripts/verify-specialty-pages.py, and never write day names, clock times or a fee outside the [[HOURS]] and [[FEE]] tokens.
- 2026-11-16: Two commits were pushed to an open pull request with only a self review, after the owner asked for a self fact check. Rule: every commit on a pull request branch gets its own local adversarial round before the work is reported as reviewed; a self review is extra, never a replacement.
