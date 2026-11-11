import copy
import base64
import json
import io
import contextlib
import datetime as dt
from email.message import EmailMessage
from unittest import TestCase, main
from unittest.mock import patch, MagicMock
import sys
sys.path.insert(0, 'scripts')
import outreach_cloud as o

DAY=dt.date(2026,11,11)
def entry():
    body=('Bonjour, votre café accueille des rencontres dans le quartier. Je suis Emanuel, étudiant et fondateur de SocialPerks avec une petite équipe étudiante. Vos clients invitent leurs amis pendant vos heures calmes : vous choisissez le cadeau, puis validez chaque visite au comptoir. Le pilote dure 60 jours, sans carte ni passage payant automatique. Ça vous dirait de regarder ? https://www.socialperkses.com/start Et si ce n\'est pas pour vous, dites-le-moi simplement, je ne vous réécrirai pas. Emanuel')
    q=dict(approved=True,id='a'*32,city='paris',country='fr',role='paris',reviewed_by='owner-authorized-editor',reviewed_at='2026-11-11',market_date=DAY.isoformat(),expires_date=DAY.isoformat(),recipient='hello@example.org',subject='Une idée pour votre café',body=body,variant='fr-visit-first',venue_type='cafe',language='fr',policy_sha256='b'*64,checker_sha256='c'*64,fact_url='https://example.org/',collaboration_url='https://example.org/contact',contact_url='https://example.org/contact',fact_excerpt='coffee and community',collaboration_excerpt='we welcome collaborations',opt_out="Et si ce n'est pas pour vous, dites-le-moi simplement, je ne vous réécrirai pas.",hypothesis='clarify real visits')
    q['content_sha256']=o.digest(q['subject']+'\n'+q['body'])
    return q
class Boundaries(TestCase):
    def test_import_roundtrip_with_mail_wrapping(self):
        raw=json.dumps({'policy':'A < B, https://example.org/','entries':[]}).encode()
        encoded=base64.b64encode(raw).decode()
        wrapped='\n'.join(encoded[i:i+35] for i in range(0,len(encoded),35))
        value='SOCIALPERKS_PRIVATE_IMPORT_BASE64_V1:'+o.digest(raw)+'\n'+wrapped
        self.assertEqual(o.decode_private_import(value)['policy'],'A < B, https://example.org/')
        self.assertEqual(o.decode_private_import(value.replace('\n','\r\n'))['policy'],'A < B, https://example.org/')
    def test_corrupt_import_never_approved(self):
        raw=b'{}'
        with self.assertRaises(o.Hold):
            o.decode_private_import('SOCIALPERKS_PRIVATE_IMPORT_BASE64_V1:'+'0'*64+'\n'+base64.b64encode(raw).decode())
    def test_gmail_fetch_metadata_after_body_literal(self):
        store=o.Gmail.__new__(o.Gmail);store.client=MagicMock();store.select=MagicMock()
        body=b'From: socialperks.team@gmail.com\r\nTo: hello@example.org\r\n\r\nPrivate body'
        store.client.uid.side_effect=[('OK',[b'4']),('OK',[(b'4 (UID 4 BODY[] {99}',body),b' X-GM-LABELS ("outreach/venue") X-GM-THRID 1234)'])]
        item=store.items('Sent')[0]
        self.assertIn('outreach/venue',item['labels']);self.assertIn('X-GM-THRID 1234',item['labels'])
        self.assertNotIn('Private body',item['labels'])
    def test_real_to_without_cc_bcc_is_preserved(self):
        m=EmailMessage();m['To']='bienvenue@example.org'
        self.assertEqual(o.addresses(m),{'bienvenue@example.org'})
    def test_valid_sent_receipt_is_accepted(self):
        q=entry();m=EmailMessage();m['To']=q['recipient'];m['Message-ID']=f'<sp-venue-{q["id"]}@socialperkses.com>'
        store=MagicMock();o.confirm_receipts(store,{'entry':q},[{'msg':m}]);store.label.assert_called_once()
    def test_valid(self): self.assertEqual(o.validate_entry(entry(),DAY)['city'],'paris')
    def test_unapproved(self):
        q=entry();q['approved']=False
        with self.assertRaises(o.Hold):o.validate_entry(q,DAY)
    def test_personal_address(self):
        q=entry();q['recipient']='alice@example.org'
        with self.assertRaises(o.Hold):o.validate_entry(q,DAY)
    def test_unapproved_city(self):
        q=entry();q['city']='dallas'
        with self.assertRaises(o.Hold):o.validate_entry(q,DAY)
    def test_geography(self):
        q=entry();q['country']='it'
        with self.assertRaises(o.Hold):o.validate_entry(q,DAY)
    def test_changed_copy(self):
        q=entry();q['body']+=' Merci'
        with self.assertRaises(o.Hold):o.validate_entry(q,DAY)
    def test_late_replay(self):
        q=entry();q['expires_date']='2026-11-12'
        with self.assertRaises(o.Hold):o.validate_entry(q,DAY)
    def test_second_link(self):
        q=entry();q['body']+=' https://example.org'
        with self.assertRaises(o.Hold):o.validate_entry(q,DAY)
    def test_market_hours(self):
        self.assertEqual(o.roles_at(dt.datetime(2026,11,11,11,5,tzinfo=dt.timezone.utc)),['paris'])
        self.assertEqual(o.roles_at(dt.datetime(2026,11,11,16,5,tzinfo=dt.timezone.utc)),['ambassador','paris'])
        self.assertEqual(o.roles_at(dt.datetime(2026,11,14,11,5,tzinfo=dt.timezone.utc)),[])
    def test_night(self):self.assertEqual(o.roles_at(dt.datetime(2026,11,11,2,tzinfo=dt.timezone.utc)),[])
    def test_private_url(self):
        with self.assertRaises(o.Hold):o.public_url('http://localhost/')
    def test_private_dns(self):
        with patch.object(o.socket,'getaddrinfo',return_value=[(0,0,0,0,('127.0.0.1',443))]):
            with self.assertRaises(o.Hold):o.public_url('https://example.org/')
    def test_checker_arguments(self):
        q=entry();policy=b'p';checker=b'c';q['policy_sha256']=o.digest(policy);q['checker_sha256']=o.digest(checker)
        with patch.object(o,'fetch',return_value=b'coffee and community we welcome collaborations'),patch.object(o.subprocess,'run',return_value=MagicMock(returncode=0,stdout=b'PASS hello@example.org')) as run:
            o.check_sources(q,policy,checker)
            self.assertEqual(run.call_args.args[0][-1],q['recipient'])
            self.assertNotIn('SOCIALPERKS_GMAIL_APP_PASSWORD',run.call_args.kwargs['env'])
    def test_dedupe_before_smtp(self):
        store=MagicMock();store.contacted.return_value=True;smtp=MagicMock()
        with self.assertRaises(o.Hold):o.send_one(store,{'entry':entry()},'fake',smtp)
        smtp.assert_not_called()
    def test_ambiguous_marks_inflight(self):
        store=MagicMock();store.contacted.return_value=False;store.pending.return_value=False;smtp=MagicMock();smtp.return_value.__enter__.return_value.send_message.side_effect=OSError()
        with self.assertRaisesRegex(o.Hold,'ambiguous_send_hold'):o.send_one(store,{'entry':entry()},'fake',smtp)
        self.assertEqual(store.label.call_args.kwargs['add'],(o.INFLIGHT,))
        store.receipt.assert_not_called()
    def test_pending_draft_blocks_smtp_data(self):
        store=MagicMock();store.contacted.return_value=False;store.pending.return_value=True;smtp=MagicMock()
        with self.assertRaisesRegex(o.Hold,'recipient_has_pending_message'):
            o.send_one(store,{'entry':entry()},'fake',smtp)
        smtp.return_value.__enter__.return_value.send_message.assert_not_called()
    def test_receipt_identity(self):
        m=EmailMessage();m['To']='wrong@example.org';m['Message-ID']='<wrong>'
        with self.assertRaises(o.Hold):o.confirm_receipts(MagicMock(),{'entry':entry()},[{'msg':m}])
    def test_city_cap(self):
        q=entry();q.update(city='madrid',country='es',role='ambassador')
        m=EmailMessage();m['X-SocialPerks-City']='madrid'
        sent=[{'msg':m,'labels':'outreach/c-es'}]*2
        self.assertFalse(o.within_city_cap(sent,q))
    def test_unknown_primary_city_holds(self):
        q=entry();q['country']='es'
        self.assertFalse(o.within_city_cap([{'msg':EmailMessage(),'labels':'outreach/c-es'}],q))
    def test_primary_skip(self):
        self.assertTrue(o.primary_worked([{'msg':EmailMessage(),'labels':'outreach/venue outreach/c-fr'}],'paris'))
    def test_reply_not_primary(self):
        m=EmailMessage();m['In-Reply-To']='<id>'
        self.assertFalse(o.primary_worked([{'msg':m,'labels':'outreach/venue outreach/c-fr'}],'paris'))
    def test_question(self):
        m=EmailMessage();m.set_content('Comment fonctionne votre plateforme ?')
        self.assertEqual(o.reply_kind(m),'question')
    def test_later(self):
        m=EmailMessage();m.set_content('Plus tard, merci.')
        self.assertEqual(o.reply_kind(m),'later')
    def test_auto(self):
        m=EmailMessage();m['Auto-Submitted']='auto-replied';m.set_content('no')
        self.assertEqual(o.reply_kind(m),'auto')
    def test_quote_does_not_refuse(self):
        m=EmailMessage();m.set_content('Comment faire ?\n> no thanks')
        self.assertEqual(o.reply_kind(m),'question')
class RunBoundaries(TestCase):
    def setUp(self):
        self.quiet=contextlib.redirect_stdout(io.StringIO());self.quiet.__enter__()
        self.store=MagicMock()
        q=entry()
        self.item={'entry':q,'labels':o.APPROVED,'raw':b'reviewed'}
        self.store.queue.return_value=[self.item]
        self.store.policy.return_value=b'private policy'
        playbook=EmailMessage();playbook.set_content('Private shared playbook')
        self.store.playbook.return_value={'msg':playbook,'raw':b'playbook'}
        self.store.sent_today.return_value=[]
        self.store.contacted.return_value=False
        self.store.suppressed.return_value=False
        self.sources=patch.object(o,'check_sources')
        self.sources.start()
        self.learning=patch.object(o,'learn',return_value=({},set()))
        self.learning.start()
        self.send=patch.object(o,'send_one')
        self.smtp=self.send.start()
        self.now=dt.datetime(2026,11,11,11,5,tzinfo=dt.timezone.utc)
    def tearDown(self):
        self.sources.stop();self.learning.stop();self.send.stop();self.quiet.__exit__(None,None,None)
    def test_valid_delivery(self):
        o.run('send',self.store,'fake',self.now)
        self.smtp.assert_called_once()
    def test_expired_never_replayed(self):
        self.item['entry']['market_date']='2026-11-10'
        o.run('send',self.store,'fake',self.now);self.smtp.assert_not_called()
    def test_no_approval_label(self):
        self.item['labels']=''
        o.run('send',self.store,'fake',self.now);self.smtp.assert_not_called()
    def test_shared_cap(self):
        self.store.sent_today.return_value=[{'msg':EmailMessage(),'labels':''}]*60
        o.run('send',self.store,'fake',self.now);self.smtp.assert_not_called()
    def test_primary_already_worked(self):
        self.store.sent_today.return_value=[{'msg':EmailMessage(),'labels':'outreach/venue outreach/c-fr'}]
        o.run('send',self.store,'fake',self.now);self.smtp.assert_not_called()
    def test_suppression(self):
        self.store.suppressed.return_value=True
        o.run('send',self.store,'fake',self.now);self.smtp.assert_not_called()
    def test_bounce_holds(self):
        self.store.no_bounce_today.side_effect=o.Hold('bounce_requires_owner_review')
        with self.assertRaises(o.Hold):o.run('send',self.store,'fake',self.now)
        self.smtp.assert_not_called()
    def test_missing_receipt_never_retry(self):
        self.item['labels']=o.INFLIGHT
        self.store.receipt.return_value=[]
        with self.assertRaises(o.Hold):o.run('send',self.store,'fake',self.now)
        self.smtp.assert_not_called()
    def test_readonly_check(self):
        o.run('check',self.store,'fake',self.now)
        self.smtp.assert_not_called();self.store.label.assert_not_called();self.store.append_learning.assert_not_called()
    def test_expired_snapshot(self):
        self.store.policy.side_effect=o.Hold('policy_snapshot_requires_refresh')
        with self.assertRaisesRegex(o.Hold,'policy_snapshot_requires_refresh'):
            o.run('send',self.store,'fake',self.now+dt.timedelta(days=8))
        self.smtp.assert_not_called()
if __name__=='__main__':main()
