"""Owner-authorised venue fallback. Private reviewed queue and history stay in Gmail.

Default/check never writes mail or sends. Import consumes a reviewed recipient-free Gmail draft
into private queue drafts, without sending data to GitHub secrets. Send obeys market hours and
uses a durable inflight marker before SMTP; uncertain outcomes never retry.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import datetime as dt
import email
import email.policy
from email.message import EmailMessage
from email.utils import getaddresses, parsedate_to_datetime, format_datetime
import hashlib
from html.parser import HTMLParser
import html
import imaplib
import ipaddress
import json
import os
from pathlib import Path
import re
import smtplib
import socket
import subprocess
import sys
import tempfile
import traceback
import time
import unicodedata
import urllib.request
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

SELF = 'socialperks.team@gmail.com'
ZONE = ZoneInfo('Europe/Paris')
POLICY_DRAFT = 'SocialPerks private cloud outreach policy'
PREFIX = 'SocialPerks approved venue queue '
PLAYBOOK = 'SocialPerks outreach playbook'
# GitHub concurrency group 'outreach' serializes this and the existing sender.
EUROPE = {'es', 'it', 'de', 'at', 'nl'}
APPROVED, INFLIGHT, REVIEW = ('outreach/cloud-approved', 'outreach/cloud-inflight', 'outreach/cloud-needs-review')
CITIES = {
    'paris': ('fr', 'paris'), 'versailles': ('fr', 'paris'), 'jouy-en-josas': ('fr', 'paris'),
    'bogota': ('co', 'ambassador'), 'sao-paulo': ('br', 'ambassador'),
    'barcelona': ('es', 'ambassador'), 'madrid': ('es', 'ambassador'),
    'bologna': ('it', 'ambassador'), 'rome': ('it', 'ambassador'), 'palermo': ('it', 'ambassador'),
    'goettingen': ('de', 'ambassador'), 'vienna': ('at', 'ambassador'),
    'tilburg': ('nl', 'ambassador'), 'delft': ('nl', 'ambassador'),
}
GENERIC = {'info', 'contact', 'hello', 'bonjour', 'hola', 'ola', 'oi', 'comercial', 'commercial',
           'marketing', 'bienvenue', 'digital', 'influence', 'partnerships', 'partenariat', 'partenariats', 'parcerias', 'colaboraciones',
           'comunicacion', 'presse', 'press', 'media', 'business', 'events', 'evenements', 'eventos'}
REFUSAL = re.compile(r'\b(unsubscribe|stop|désinscrire|desinscribir|baja|non merci|no thanks|n[aã]o|not interested|pas intéress|kein interesse|nee|no)\b', re.I)
LATER = re.compile(r'\b(not now|plus tard|pour le moment|por ahora|más adelante|mais tarde|later|später)\b', re.I)
POSITIVE = re.compile(r'\b(oui|yes|interested|intéress|interesa|interess|sim|claro|gerne|ja)\b', re.I)


class Hold(Exception):
    """Only fixed, non-private status codes may leave the worker."""


def require(condition, code):
    if not condition:
        raise Hold(code)


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()


def quoted(value):
    require('\r' not in value and '\n' not in value, 'unsafe_imap_argument')
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def password():
    value = ''.join(c for c in os.environ.get('SOCIALPERKS_GMAIL_APP_PASSWORD', '')
                    if not c.isspace() and unicodedata.category(c) != 'Cf').strip('"\'`')
    require(len(value) == 16 and value.isascii() and value.isalnum(), 'credential_format')
    return value


def roles_at(now):
    local = now.astimezone(ZONE)
    if local.weekday() >= 5:
        return []
    if 12 <= local.hour < 15:
        return ['paris']
    if 17 <= local.hour < 19:
        return ['ambassador', 'paris']
    return []


def addresses(message, fields=('To', 'Cc', 'Bcc')):
    return {addr.casefold() for _, addr in getaddresses([str(message[f]) for f in fields if message.get(f)]) if addr}


def is_first_contact(message):
    return not message.get('In-Reply-To') and not message.get('References')


def message_day(message):
    try:
        value = parsedate_to_datetime(str(message['Date']))
        require(value.tzinfo is not None, 'sent_date_missing_timezone')
        return value.astimezone(ZONE).date()
    except (TypeError, ValueError, KeyError):
        raise Hold('sent_date_unreadable') from None


def text(message):
    body = message.get_body(preferencelist=('plain',)) if message.is_multipart() else message
    if body and body.get_content_type() == 'text/plain':
        return body.get_content()
    body = message.get_body(preferencelist=('html',)) if message.is_multipart() else message
    return plain(body.get_content()) if body else ''


class TextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.hidden = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.hidden += 1
        if tag in ('br', 'p', 'div', 'li'):
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def plain(value):
    parser = TextParser()
    parser.feed(value)
    return ''.join(parser.parts)


def normal(value):
    return ' '.join(value.casefold().split())


def public_url(url):
    parsed = urlsplit(url)
    require(parsed.scheme == 'https' and parsed.hostname and not parsed.username and not parsed.password
            and parsed.port in (None, 443), 'unapproved_source_url')
    try:
        resolved = socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)
    except OSError:
        raise Hold('source_dns_unavailable') from None
    require(resolved and all(ipaddress.ip_address(row[4][0]).is_global for row in resolved), 'nonpublic_source')
    return url


class PublicRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        public_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url):
    public_url(url)
    try:
        with urllib.request.build_opener(PublicRedirect).open(urllib.request.Request(url, headers={'User-Agent': 'SocialPerksVerify/1.0'}), timeout=25) as response:
            require(response.status == 200, 'source_not_available')
            return response.read(3_000_000)
    except (OSError, ValueError):
        raise Hold('source_not_available') from None


def validate_entry(q, today):
    require(isinstance(q, dict) and q.get('approved') is True, 'unreviewed_queue')
    require(re.fullmatch('[a-f0-9]{32}', q.get('id', '')) is not None, 'invalid_queue_id')
    require(q.get('city') in CITIES, 'city_not_authorized')
    require((q.get('country'), q.get('role')) == CITIES[q['city']], 'geography_mismatch')
    require(q.get('reviewed_by') and q.get('reviewed_at'), 'review_not_recorded')
    try:
        reviewed = dt.date.fromisoformat(q['reviewed_at'][:10])
    except (ValueError, TypeError):
        raise Hold('review_date_invalid') from None
    require(0 <= (today - reviewed).days <= 7, 'review_requires_refresh')
    try:
        day = dt.date.fromisoformat(q['market_date'])
    except (KeyError, TypeError, ValueError):
        raise Hold('queue_date_invalid') from None
    require(q.get('expires_date') == q['market_date'], 'queue_must_expire_same_market_day')
    require(day <= today + dt.timedelta(days=7), 'queue_too_far_ahead')
    recipient = q.get('recipient', '')
    require(re.fullmatch(r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}', recipient) is not None, 'recipient_invalid')
    local, domain = recipient.casefold().split('@')
    require(local in GENERIC or local == domain.split('.')[0].replace('-', ''), 'nongeneric_recipient')
    body, subject = q.get('body', ''), q.get('subject', '')
    require(isinstance(body, str) and 60 <= len(body.split()) <= 110, 'body_word_limit')
    require(subject and '\r' not in subject and '\n' not in subject and len(subject) <= 130, 'subject_invalid')
    require('\u2014' not in body + subject, 'em_dash_not_allowed')
    require(re.findall(r'https?://[^\s<>]+', body) == ['https://www.socialperkses.com/start'], 'signup_link_invalid')
    require(isinstance(q.get('variant'), str) and re.fullmatch('[a-z0-9-]{3,35}', q['variant']), 'variant_invalid')
    require(q.get('venue_type') in ('hotel', 'restaurant', 'cafe', 'cocktail-bar', 'bar', 'tattoo', 'gym', 'salon', 'barber'), 'venue_type_invalid')
    require(q.get('language') in ('fr', 'es', 'pt-BR', 'en', 'it', 'de', 'pt', 'nl'), 'language_invalid')
    for key in ('policy_sha256', 'checker_sha256'):
        require(re.fullmatch('[a-f0-9]{64}', q.get(key, '')) is not None, 'review_hash_missing')
    for key in ('fact_excerpt', 'collaboration_excerpt'):
        require(isinstance(q.get(key), str) and 3 <= len(q[key].split()) <= 25, 'source_evidence_missing')
    for key in ('fact_url', 'collaboration_url', 'contact_url'):
        parsed = urlsplit(q.get(key, ''))
        require(parsed.scheme == 'https' and parsed.hostname, 'source_url_missing')
    require(q.get('opt_out') and q['opt_out'] in body, 'opt_out_missing')
    require(q.get('content_sha256') == digest(subject + '\n' + body), 'reviewed_copy_changed')
    require(q.get('hypothesis'), 'daily_hypothesis_missing')
    return q


def decode_private_import(value):
    parts = value.strip().split(':', 1)
    require(len(parts) == 2 and parts[0] == 'SOCIALPERKS_PRIVATE_IMPORT_BASE64_V1', 'import_envelope_missing')
    checksum, separator, encoded = parts[1].partition('\n')
    checksum = checksum.strip()
    require(separator and re.fullmatch('[a-f0-9]{64}', checksum), 'import_envelope_invalid')
    try:
        raw = base64.b64decode(''.join(encoded.split()), validate=True)
        require(digest(raw) == checksum, 'private_import_changed')
        return json.loads(raw)
    except (binascii.Error, ValueError, UnicodeError):
        raise Hold('private_import_encoding_invalid') from None


class Gmail:
    def __init__(self, credential):
        self.client = imaplib.IMAP4_SSL('imap.gmail.com', 993, timeout=30)
        self.client.login(SELF, credential)
        status, rows = self.client.list()
        require(status == 'OK', 'mailbox_list_failed')
        self.folders = {}
        for row in rows:
            match = re.fullmatch(rb'\(([^)]*)\) "[^"]*" (.+)', row)
            if match:
                for tag in ('Sent', 'Drafts', 'All', 'Trash', 'Junk'):
                    if ('\\' + tag).encode() in match[1].split():
                        self.folders[tag] = match[2].decode('ascii')
        require(all(name in self.folders for name in ('Sent', 'Drafts', 'All', 'Trash', 'Junk')), 'special_folder_missing')

    def select(self, folder, write=False):
        status, _ = self.client.select(self.folders[folder], readonly=not write)
        require(status == 'OK', 'mailbox_select_failed')

    def items(self, folder, criteria='ALL', raw=False):
        self.select(folder)
        args = ('X-GM-RAW', quoted(criteria)) if raw else (criteria,)
        status, data = self.client.uid('SEARCH', None, *args)
        require(status == 'OK', 'history_search_failed')
        result = []
        for uid in (data[0] or b'').split():
            status, rows = self.client.uid('FETCH', uid, '(BODY.PEEK[] X-GM-LABELS X-GM-MSGID X-GM-THRID)')
            require(status == 'OK', 'history_fetch_failed')
            values = [row for row in rows if isinstance(row, tuple)]
            require(len(values) == 1, 'history_fetch_incomplete')
            metadata, body = values[0]
            result.append({'folder': folder, 'uid': uid, 'msg': email.message_from_bytes(body, policy=email.policy.default),
                           'raw': body, 'labels': (metadata + b' ' + b' '.join(r for r in rows if isinstance(r, bytes))).decode('ascii', 'replace')})
        return result

    def label(self, item, add=(), remove=()):
        self.select(item['folder'], write=True)
        for operation, labels in (('+X-GM-LABELS', add), ('-X-GM-LABELS', remove)):
            if labels:
                status, _ = self.client.uid('STORE', item['uid'], operation, '(' + ' '.join(quoted(label) for label in labels) + ')')
                require(status == 'OK', 'label_write_failed')

    def append(self, message):
        status, _ = self.client.append(self.folders['Drafts'], '\\Draft', None, message.as_bytes())
        require(status == 'OK', 'private_draft_write_failed')

    def queue(self, today):
        result = []
        for item in self.items('Drafts'):
            if str(item['msg'].get('Subject', '')).startswith(PREFIX):
                require(addresses(item['msg']) == set() and SELF in addresses(item['msg'], ('From',)), 'queue_draft_not_internal')
                try:
                    item['entry'] = validate_entry(json.loads(text(item['msg'])), today)
                except (ValueError, TypeError):
                    raise Hold('queue_not_valid_json') from None
                result.append(item)
        return result

    def confirm_approved(self, item):
        current = [i for i in self.queue(dt.datetime.now(ZONE).date()) if i['entry']['id'] == item['entry']['id']]
        require(len(current) == 1 and current[0]['raw'] == item['raw'] and APPROVED in current[0]['labels'] and INFLIGHT not in current[0]['labels'], 'approval_changed_before_send')

    def sent_today(self, today):
        # IMAP SINCE is deliberately a day wider; Date is then evaluated in Paris.
        since = (today - dt.timedelta(days=1)).strftime('%d-%b-%Y')
        return [item for item in self.items('Sent', f'SINCE {quoted(since)}') if message_day(item['msg']) == today]

    def contacted(self, recipient):
        return bool(self.items('Sent', 'OR (OR TO ' + quoted(recipient) + ' CC ' + quoted(recipient) + ') BCC ' + quoted(recipient)))

    def pending(self, recipient):
        target = recipient.casefold()
        # Recipient-free control drafts cannot collide with a genuine queued mail.
        return any(target in addresses(item['msg'])
                   for item in self.items('Drafts') + self.items('All', 'in:scheduled', raw=True))

    def receipt(self, queue_id):
        return self.items('Sent', 'HEADER Message-ID ' + quoted(f'<sp-venue-{queue_id}@socialperkses.com>'))

    def suppressed(self, recipient, today):
        domain = recipient.split('@')[1].casefold()
        seen = set()
        for folder in ('All', 'Trash', 'Junk'):
            for item in self.items(folder, 'FROM ' + quoted(domain)):
                message = item['msg']
                key = str(message.get('Message-ID', digest(item['raw'])))
                if key in seen:
                    continue
                seen.add(key)
                sender_domains = {a.split('@')[-1] for a in addresses(message, ('From',))}
                if domain in sender_domains and REFUSAL.search(text(message)):
                    return True
        for folder in ('All', 'Trash', 'Junk'):
            for item in self.items(folder, domain, raw=True):
                if any(part.get_content_type() == 'message/delivery-status' for part in item['msg'].walk()):
                    return True
        return False

    def no_bounce_today(self, today):
        since = (today - dt.timedelta(days=1)).strftime('%d-%b-%Y')
        for folder in ('All', 'Trash', 'Junk'):
            for item in self.items(folder, f'SINCE {quoted(since)}'):
                message = item['msg']
                if message_day(message) == today:
                    require(not any(part.get_content_type() == 'message/delivery-status' for part in message.walk()), 'bounce_requires_owner_review')
                    require(not re.search(r'\b(spam warning|spam complaint)\b', str(message.get('Subject', '')), re.I), 'spam_warning_requires_owner_review')

    def playbook(self):
        items = [i for i in self.items('Drafts', 'HEADER Subject ' + quoted(PLAYBOOK))
                 if str(i['msg'].get('Subject', '')) == PLAYBOOK and not addresses(i['msg'])]
        require(items, 'shared_playbook_missing')
        return items[-1]

    def policy(self, today):
        items = [i for i in self.items('Drafts', 'HEADER Subject ' + quoted(POLICY_DRAFT))
                 if str(i['msg'].get('Subject', '')) == POLICY_DRAFT]
        require(len(items) == 1, 'private_policy_missing_or_ambiguous')
        message = items[0]['msg']
        require(not addresses(message) and SELF in addresses(message, ('From',)), 'policy_draft_not_internal')
        try:
            data = json.loads(text(message))
            reviewed = dt.date.fromisoformat(data['reviewed_at'])
        except (ValueError, KeyError, TypeError):
            raise Hold('private_policy_invalid') from None
        require(0 <= (today - reviewed).days <= 7, 'policy_snapshot_requires_refresh')
        require(data['policy_sha256'] == digest(data['text']), 'private_policy_hash_mismatch')
        return data['text'].encode()

    def import_policy(self, value, today):
        current = self.items('Drafts', 'HEADER Subject ' + quoted(POLICY_DRAFT))
        if current:
            require(self.policy(today) == value.encode(), 'private_policy_changed_requires_review')
            return
        message = EmailMessage()
        message['From'], message['Subject'] = SELF, POLICY_DRAFT
        message['Date'] = format_datetime(dt.datetime.now(dt.timezone.utc))
        message.set_content(json.dumps(dict(reviewed_at=today.isoformat(), policy_sha256=digest(value), text=value), ensure_ascii=False))
        self.append(message)
        require(self.policy(today) == value.encode(), 'private_policy_import_not_confirmed')

    def append_learning(self, original, note):
        # A concurrently edited playbook wins; never overwrite its newer content.
        latest = self.playbook()
        require(digest(latest['raw']) == digest(original['raw']), 'playbook_changed_concurrently')
        msg = EmailMessage()
        msg['From'], msg['Subject'] = SELF, PLAYBOOK
        msg['Date'] = format_datetime(dt.datetime.now(dt.timezone.utc))
        msg.set_content(text(original['msg']) + '\n\n' + note)
        original_html = original['msg'].get_body(preferencelist=('html',)) if original['msg'].is_multipart() else None
        if original_html:
            msg.add_alternative(original_html.get_content() + '<hr><pre>' + html.escape(note) + '</pre>', subtype='html')
        self.append(msg)
        self.label(original, add=('\\Trash',))


def primary_worked(sent, role):
    for item in sent:
        message = item['msg']
        if not is_first_contact(message) or message.get('X-SocialPerks-Queue-ID'):
            continue
        if 'outreach/venue' not in item['labels']:
            continue
        country = 'fr' if 'outreach/c-fr' in item['labels'] else 'other'
        if (role == 'paris') == (country == 'fr'):
            return True
    return False


def check_sources(q, policy_bytes, checker_bytes):
    require(digest(policy_bytes) == q['policy_sha256'] and digest(checker_bytes) == q['checker_sha256'], 'reviewed_rules_changed')
    for prefix in ('fact', 'collaboration'):
        page = plain(fetch(q[prefix + '_url']).decode('utf-8', 'replace'))
        require(normal(q[prefix + '_excerpt']) in normal(page), 'reviewed_source_changed')
    with tempfile.TemporaryDirectory() as directory:
        checker = Path(directory) / 'verify_address.py'
        checker.write_bytes(checker_bytes)
        result = subprocess.run([sys.executable, str(checker), q['contact_url'], q['collaboration_url'], q['recipient']],
                                capture_output=True, timeout=180, env={'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LANG': 'C.UTF-8'})
        require(result.returncode == 0 and result.stdout.startswith(('PASS ' + q['recipient']).encode()), 'official_address_check_failed')


def send_one(store, item, credential, smtp_factory=smtplib.SMTP_SSL):
    q = item['entry']
    require(not store.contacted(q['recipient']), 'already_contacted')
    message = EmailMessage()
    message['From'], message['To'] = f'Emanuel Conti <{SELF}>', q['recipient']
    message['Subject'] = q['subject']
    message['Date'] = format_datetime(dt.datetime.now(dt.timezone.utc))
    message['Message-ID'] = f'<sp-venue-{q["id"]}@socialperkses.com>'
    for field in ('id', 'role', 'city', 'variant', 'country', 'venue_type', 'language'):
        message['X-SocialPerks-' + ('Queue-ID' if field == 'id' else field.replace('_', '-').title())] = q[field]
    message.set_content(q['body'])
    with smtp_factory('smtp.gmail.com', 465, timeout=30) as smtp:
        smtp.login(SELF, credential)
        store.confirm_approved(item)
        require(not store.pending(q['recipient']), 'recipient_has_pending_message')
        require(not store.contacted(q['recipient']), 'already_contacted')
        # This marker must exist even if DATA succeeds but the connection dies.
        store.label(item, add=(INFLIGHT,), remove=(APPROVED,))
        try:
            refused = smtp.send_message(message, from_addr=SELF, to_addrs=[q['recipient']])
            require(not refused, 'smtp_recipient_refused')
        except Exception:
            raise Hold('ambiguous_send_hold') from None
    receipts = []
    for delay in (0, 0.5, 1.5):
        if delay:
            time.sleep(delay)
        receipts = store.receipt(q['id'])
        if receipts:
            break
    require(receipts, 'accepted_awaiting_sent_receipt')
    confirm_receipts(store, item, receipts)
    store.label(item, add=('\\Trash',), remove=(INFLIGHT,))


def confirm_receipts(store, item, receipts):
    q = item['entry']
    for receipt in receipts:
        require(q['recipient'].casefold() in addresses(receipt['msg']), 'receipt_recipient_mismatch')
        require(str(receipt['msg'].get('Message-ID', '')) == f'<sp-venue-{q["id"]}@socialperkses.com>', 'receipt_identity_mismatch')
        store.label(receipt, add=('outreach/venue', 'outreach/t-' + q['venue_type'], 'outreach/c-' + q['country'], 'outreach/v-' + q['variant']))


def within_city_cap(sent, q):
    if q['country'] not in EUROPE:
        return True
    # Include primary messages; an unclassified European venue send holds the role.
    european = [i for i in sent if any('outreach/c-' + c in i['labels'] for c in EUROPE)]
    if any(not i['msg'].get('X-SocialPerks-City') for i in european):
        return False
    return len(european) < 14 and sum(i['msg'].get('X-SocialPerks-City') == q['city'] for i in european) < 2


def reply_kind(message):
    if message.get('Auto-Submitted', 'no') != 'no' or message.get('X-Autoreply') or message.get('X-Autorespond'):
        return 'auto'
    # Quoted history contains our own opt-out. Never classify that as a refusal.
    body = re.split(r'(?m)^>|^On .+wrote:|^Le .+écrit :|^From:|^De :', text(message))[0]
    if LATER.search(body):
        return 'later'
    if REFUSAL.search(body):
        return 'no'
    if '?' in body:
        return 'question'
    if POSITIVE.search(body):
        return 'yes'
    return 'unclassified'


def learn(store, today, write=False):
    since = (today - dt.timedelta(days=30)).strftime('%d-%b-%Y')
    cohorts, visited, retired, totals = {}, set(), set(), {}
    for item in store.items('Sent', f'SINCE {quoted(since)}'):
        if 'outreach/venue' not in item['labels'] or not is_first_contact(item['msg']):
            continue
        match = re.search(r'X-GM-THRID (\d+)', item['labels'])
        require(match is not None, 'thread_identity_missing')
        thread_id = match[1]
        if thread_id in visited:
            continue
        visited.add(thread_id)
        variant = item['msg'].get('X-SocialPerks-Variant')
        if not variant:
            legacy = re.search(r'outreach/v-([a-zA-Z0-9-]+)', item['labels'])
            variant = legacy[1] if legacy else 'legacy-unclassified'
        def dimension(field, label):
            known = item['msg'].get('X-SocialPerks-' + field)
            match = re.search(r'outreach/' + label + r'-([a-zA-Z0-9-]+)', item['labels'])
            return known or (match[1] if match else 'unknown')
        key = '|'.join((str(variant), dimension('Language','language'), dimension('Country','c'), dimension('Venue-Type','t')))
        group = cohorts.setdefault(key, dict(sends=0, yes=0, question=0, no=0, later=0, auto=0, unclassified=0, silence_3d=0))
        total = totals.setdefault(variant, dict(sends=0, early_no=0, positive=0))
        group['sends'] += 1
        total['sends'] += 1
        incoming = [m for m in store.items('All', 'X-GM-THRID ' + thread_id)
                    if SELF not in addresses(m['msg'], ('From',))]
        if incoming:
            kind = reply_kind(incoming[-1]['msg'])
            group[kind] += 1
            if kind == 'no' and total['sends'] <= 20:
                total['early_no'] += 1
            if kind in ('yes', 'question'):
                total['positive'] += 1
            if write and kind != 'unclassified':
                label = 'outreach/later' if kind == 'later' else 'outreach/r-' + kind
                for reply in store.items('All', 'X-GM-THRID ' + thread_id):
                    store.label(reply, add=(label,))
        elif (today - message_day(item['msg'])).days >= 3:
            group['silence_3d'] += 1
    for variant, group in totals.items():
        if group['early_no'] >= 2 or (group['sends'] >= 30 and group['positive'] == 0):
            retired.add(variant)
    return cohorts, retired


def import_queue(store, payload, today):
    require(isinstance(payload, list) and 1 <= len(payload) <= 50, 'import_size_invalid')
    existing = {item['entry']['id'] for item in store.queue(today)}
    for value in payload:
        q = validate_entry(value, today)
        if q['id'] in existing or store.contacted(q['recipient']):
            continue
        msg = EmailMessage()
        msg['From'], msg['Subject'] = SELF, PREFIX + q['id']
        msg['Date'] = format_datetime(dt.datetime.now(dt.timezone.utc))
        msg.set_content(json.dumps(q, ensure_ascii=False, indent=2))
        store.append(msg)
        matches = [i for i in store.queue(today) if i['entry']['id'] == q['id']]
        require(len(matches) == 1 and matches[0]['entry'] == q, 'import_not_confirmed')
        store.label(matches[0], add=(APPROVED,))
        existing.add(q['id'])


def run(mode, store, credential, now):
    today = now.astimezone(ZONE).date()
    playbook = store.playbook()
    queue = store.queue(today)
    if mode == 'import':
        imports = [i for i in store.items('Drafts', 'HEADER Subject ' + quoted('SocialPerks reviewed cloud import')) if str(i['msg'].get('Subject','')) == 'SocialPerks reviewed cloud import']
        require(len(imports) == 1, 'private_import_missing_or_ambiguous')
        source = imports[0]
        require(not addresses(source['msg']) and SELF in addresses(source['msg'], ('From',)), 'import_draft_not_internal')
        payload = decode_private_import(text(source['msg']))
        require(isinstance(payload, dict) and isinstance(payload.get('policy'), str), 'private_policy_required')
        store.import_policy(payload['policy'], today)
        import_queue(store, payload.get('entries'), today)
        store.label(source, add=('\\Trash',))
        return 'imported_private_reviewed_drafts'
    policy_bytes = store.policy(today)
    checker_bytes = Path('scripts/outreach/verify_address.py').read_bytes()
    for item in queue:
        if item['entry']['market_date'] >= today.isoformat():
            check_sources(item['entry'], policy_bytes, checker_bytes)
    if mode == 'check':
        learn(store, today, write=False)
        live = [i for i in queue if i['entry']['market_date'] >= today.isoformat() and APPROVED in i['labels']]
        print('OUTREACH_APPROVED_DRAFTS=' + str(len(live)))
        require(live, 'reviewed_inventory_empty')
        return 'read_only_queue_verified'
    roles = roles_at(now)
    if not roles:
        return 'outside_market_hours'
    cohorts, retired = learn(store, today, write=True)
    # Reconcile first. Old accepted mail is never sent again, even after expiry.
    reconciled_count = 0
    for item in queue:
        if INFLIGHT in item['labels']:
            receipts = store.receipt(item['entry']['id'])
            require(receipts, 'unresolved_inflight_hold')
            confirm_receipts(store, item, receipts)
            store.label(item, add=('\\Trash',), remove=(INFLIGHT,))
            reconciled_count += 1
    print('OUTREACH_PRIOR_SENT_RECONCILED=' + str(reconciled_count))
    store.no_bounce_today(today)
    sent = store.sent_today(today)
    allowed_roles = [role for role in roles if not primary_worked(sent, role)]
    candidates = [item for item in queue if item['entry']['market_date'] == today.isoformat()
                  and item['entry']['role'] in allowed_roles and APPROVED in item['labels']
                  and INFLIGHT not in item['labels'] and REVIEW not in item['labels']]
    # Each cloud role contributes at most five actual first contacts/day.
    counts = {role: sum(i['msg'].get('X-SocialPerks-Role') == role for i in sent) for role in roles}
    candidates.sort(key=lambda i: (roles.index(i['entry']['role']), i['entry']['id']))
    sent_count = 0
    for item in candidates:
        q = item['entry']
        if q['variant'] in retired:
            store.label(item, add=(REVIEW,))
            continue
        current = store.sent_today(today)
        if not within_city_cap(current, q):
            continue
        if len(current) >= 60 or primary_worked(current, q['role']) or counts.get(q['role'], 0) >= 5 or sent_count >= 5:
            continue
        if store.contacted(q['recipient']) or store.suppressed(q['recipient'], today):
            store.label(item, add=(REVIEW,))
            continue
        store.no_bounce_today(today)
        check_sources(q, policy_bytes, checker_bytes)
        send_one(store, item, credential)
        counts[q['role']] = counts.get(q['role'], 0) + 1
        sent_count += 1
    print('OUTREACH_SENT_CONFIRMED=' + str(sent_count))
    cohorts, retired = learn(store, today, write=False)
    marker = '[cloud-cohort-snapshot:' + today.isoformat() + ':' + digest(json.dumps(cohorts, sort_keys=True)) + ']'
    if sent_count or reconciled_count or marker not in text(playbook['msg']):
        hypothesis = queue[0]['entry']['hypothesis'] if queue else 'No new reviewed inventory; no copy generated.'
        note = (f'Cloud venue backup {today.isoformat()}: {sent_count} new first contacts confirmed in remote Sent; '
                f'{reconciled_count} earlier sent receipts reconciled without sending again. '
                'No follow-up. Sign-ups not checked; no conversion claim. '
                'Hypothesis: ' + hypothesis + '\nObserved reply cohorts (not sign-ups): ' + json.dumps(cohorts, ensure_ascii=False) +
                '\nGroups below20 sends are descriptive only. No automatic copy rewrite or causal claim. Retired variants: ' +
                ', '.join(sorted(retired)) + '\n' + marker)
        store.append_learning(playbook, note)
    return 'completed_guarded_venue_pass'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=('check', 'import', 'send'), default='check')
    args = parser.parse_args()
    try:
        credential = password()
        store = Gmail(credential)
        result = run(args.mode, store, credential, dt.datetime.now(dt.timezone.utc))
        print('OUTREACH=' + result)
        return 0
    except Hold as error:
        print('OUTREACH_HOLD=' + str(error))
    except (imaplib.IMAP4.error, smtplib.SMTPException):
        print('OUTREACH_HOLD=mail_service_error')
    except Exception as error:
        frames = traceback.extract_tb(error.__traceback__)
        frame = next((f for f in reversed(frames) if f.filename.endswith('outreach_cloud.py')), None)
        print('OUTREACH_DIAGNOSTIC=' + type(error).__name__ + ':' + (str(frame.lineno) if frame else 'external'))
        print('OUTREACH_HOLD=unexpected_error')
    return 1


if __name__ == '__main__':
    sys.exit(main())
