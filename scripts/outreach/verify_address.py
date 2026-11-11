#!/usr/bin/env python3
"""Check one outreach address before any email is sent (docs/coordination/OUTREACH.md).

    python3 scripts/outreach/verify_address.py <page-url> <email> [<page-url> ...]

The owner, 8 November 2026: only addresses verified 100%, never one that can
bounce. Port 25 is closed here, so the mailbox itself cannot be probed; this
checks everything else that makes an address go wrong, and prints PASS only
when every check passes:

  1. the address is printed on the page fetched now (raw HTML, mailto links,
     HTML entities and URL encoding decoded), exactly, character by character;
  2. the page answers 200 and is not a parked or for-sale domain;
  3. the address's domain has real MX records (DNS over HTTPS), not a null MX,
     and every MX host resolves;
  4. the address's domain is the site's own domain or appears on the page;
  5. it is not a free or personal mailbox (gmail, hotmail, outlook, yahoo...)
     and not a web designer's or host's address (webmaster@, the designer's
     domain);
  6. the page shows it is current: this year or last year printed on it.

Exit code 0 means PASS. Anything else means do not send.
"""
import datetime, html, json, re, sys, urllib.parse, urllib.request

FREE = {"gmail.com", "googlemail.com", "hotmail.com", "hotmail.it", "hotmail.es", "hotmail.fr", "outlook.com", "outlook.es",
        "live.com", "yahoo.com", "yahoo.es", "yahoo.it", "yahoo.fr", "yahoo.com.br", "icloud.com", "me.com", "aol.com",
        "gmx.de", "gmx.at", "gmx.net", "web.de", "libero.it", "uol.com.br", "bol.com.br", "terra.com.br", "proton.me", "protonmail.com"}
NOT_THE_VENUE = re.compile(r"^(webmaster|hostmaster|postmaster|abuse|admin|noreply|no-reply|donotreply|privacy|dpo|legal|rgpd|gdpr|datenschutz)@", re.I)
PARKED = re.compile(r"(this domain (is|may be) for sale|domain parked|buy this domain|parkingcrew|sedoparking|domain is parked|godaddy\.com/domainsearch)", re.I)
UA = "Mozilla/5.0 (compatible; SocialPerksVerify/1.0)"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en,es,it,de,fr,pt;q=0.8"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.status, r.geturl(), r.read(3_000_000).decode(r.headers.get_content_charset() or "utf-8", "replace")


def doh(name, kind):
    url = "https://dns.google/resolve?" + urllib.parse.urlencode({"name": name, "type": kind})
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=20) as r:
        data = json.load(r)
    return [a["data"] for a in data.get("Answer", []) if a.get("type") == {"MX": 15, "A": 1, "AAAA": 28}[kind]]


def cloudflare(hexstr):
    # Cloudflare's email protection: the first byte is the key, XOR the rest.
    try:
        key = int(hexstr[:2], 16)
        return "".join(chr(int(hexstr[i:i + 2], 16) ^ key) for i in range(2, len(hexstr), 2))
    except ValueError:
        return ""


def emails_in(text):
    text = text + " " + " ".join(cloudflare(h) for h in re.findall(r'(?:data-cfemail="|email-protection#)([0-9a-fA-F]{6,})', text))
    t = html.unescape(urllib.parse.unquote(text))
    t = re.sub(r"\s*(\[at\]|\(at\)|&#64;)\s*", "@", t, flags=re.I)
    return {m.lower() for m in re.findall(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", t)}


def site_domain(url):
    host = urllib.parse.urlparse(url).hostname or ""
    return host[4:] if host.startswith("www.") else host


def main(argv):
    if len(argv) < 3:
        print(__doc__); return 2
    email = argv[-1].strip().lower()
    pages = argv[1:-1]
    checks, ok = [], True

    def check(passed, label):
        nonlocal ok
        checks.append(("PASS" if passed else "FAIL") + ": " + label)
        ok = ok and passed

    if not re.fullmatch(r"[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}", email):
        check(False, "address has a valid shape"); return report(email, checks, ok)
    domain = email.split("@", 1)[1]
    found, texts, sites = False, [], set()
    for url in pages:
        try:
            status, final, body = fetch(url)
        except Exception as e:  # noqa: BLE001
            check(False, f"page answers: {url} ({type(e).__name__}: {e})"); continue
        check(status == 200, f"page answers 200: {final}")
        check(not PARKED.search(body), f"page is not a parked domain: {final}")
        texts.append(body); sites.add(site_domain(final))
        if email in emails_in(body):
            found = True
    check(found, "address printed on the page, exactly")
    try:
        mx = doh(domain, "MX")
        real = [m.split()[-1].rstrip(".") for m in mx if m.split()[-1] not in (".", "")]
        check(bool(real), f"MX records for {domain}: {', '.join(real) or 'none'}")
        for host in real[:3]:
            check(bool(doh(host, "A") or doh(host, "AAAA")), f"MX host resolves: {host}")
    except Exception as e:  # noqa: BLE001
        check(False, f"DNS lookup for {domain} ({e})")
    own = any(domain == s or domain.endswith("." + s) or s.endswith("." + domain) for s in sites)
    # Named on the page as a website, not only inside the address itself.
    mentioned = any(re.search(r"https?://(www\.)?" + re.escape(domain) + r"(/|\b)", t, re.I) for t in texts)
    check(own or mentioned, f"address domain {domain} is the site's own ({', '.join(sorted(sites))}) or named on it")
    check(domain not in FREE, "not a free or personal mailbox")
    check(not NOT_THE_VENUE.match(email), "not a webmaster, legal or no-reply address")
    year = datetime.date.today().year
    current = any(str(year) in t or str(year - 1) in t for t in texts)
    check(current, f"page shows {year} or {year - 1} (site is current)")
    return report(email, checks, ok)


def report(email, checks, ok):
    print(("PASS " if ok else "FAIL ") + email)
    for c in checks:
        print("  " + c)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
