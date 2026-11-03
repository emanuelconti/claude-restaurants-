import datetime as dt,unittest
from policy import TZ,target,seen,count_today,next_item,gap_ok,youtube_title,parse_ig_history,SINGAPORE,local_now,selected_brands,EU_CRON,GMS_CRON
class QueuePolicyTests(unittest.TestCase):
 def setUp(self):
  self.day='2026-11-03';self.now=dt.datetime(2026,11,3,20,58,tzinfo=TZ)
  self.items=[dict(id=f'sp-{i}',brand='sp',date=self.day,title=f'Topic {i}') for i in range(8)]
 def test_completed_first_item_does_not_block_following_items(self):
  self.assertEqual(next_item(self.items,'sp','ig',self.day,{'sp-0:ig':'success'})['id'],'sp-1')
 def test_receipt_on_another_channel_does_not_consume_item(self):
  self.assertEqual(next_item(self.items,'sp','ig',self.day,{'sp-0:threads':'success'})['id'],'sp-0')
 def test_yesterday_is_not_reused_today(self):
  self.assertIsNone(next_item(self.items,'sp','ig','2026-11-04',{}))
 def test_timezone_boundary_counts_actual_local_day(self):
  self.assertEqual(count_today([dict(stamp='2026-11-02T23:05:00Z')],self.now),1)
  self.assertEqual(count_today([dict(stamp='2026-11-02T22:59:59Z')],self.now),0)
 def test_facebook_gap_is_sixty_actual_minutes(self):
  self.assertFalse(gap_ok([dict(stamp='2026-11-03T20:00:00+01:00')],self.now,60))
  self.assertTrue(gap_ok([dict(stamp='2026-11-03T19:58:00+01:00')],self.now,60))
 def test_short_title_match_uses_exact_published_truncation(self):
  item={'title':'A long original title '*5}
  self.assertTrue(seen(item,'youtube',[dict(title=youtube_title(item['title']))]))
  self.assertFalse(seen(item,'youtube',[dict(title='A long original title with a different ending')]))
 def test_targets_stop_at_eight(self):
  self.assertEqual([target(self.now.replace(hour=h)) for h in [6,7,8,9,13,14,15,19,20,23]],[0,1,2,3,4,5,6,7,8,8])
 def test_eight_posts_can_advance_without_republishing_first(self):
  state={};chosen=[]
  for _ in range(8):
   item=next_item(self.items,'sp','ig',self.day,state);chosen.append(item['id']);state[item['id']+':ig']='success'
  self.assertEqual(len(set(chosen)),8);self.assertIsNone(next_item(self.items,'sp','ig',self.day,state))
 def test_recovery_slots_fill_facebook_without_shortening_its_gap(self):
  posts=[];state={};minute_durations=[5,0,3,0,2,0,4,0,0,2,0,0,0,3,0,0,0]
  for hour,delay in zip(range(7,24),minute_durations):
   now=dt.datetime(2026,11,3,hour,58,tzinfo=TZ)+dt.timedelta(minutes=delay)
   if count_today(posts,now)>=target(now) or not gap_ok(posts,now,60):continue
   item=next_item(self.items,'sp','facebook',self.day,state)
   if item:
    state[item['id']+':facebook']='success';posts.append(dict(title=item['title'],stamp=now.isoformat()))
  self.assertEqual(len(posts),8)
 def test_empty_caption_still_counts_as_a_real_post(self):
  rows=parse_ig_history('2026-11-03T08:00:00+0000  \n2026-11-03T09:00:00+0000 A title\n')
  self.assertEqual(len(rows),2);self.assertEqual(rows[0]['title'],'');self.assertEqual(count_today(rows,self.now),2)
class SingaporeMarketTests(unittest.TestCase):
 def test_one_instant_has_two_different_calendar_days(self):
  now=dt.datetime(2026,11,3,17,tzinfo=dt.timezone.utc)
  self.assertEqual(local_now(now,'sp').date().isoformat(),'2026-11-03')
  self.assertEqual(local_now(now,'gms').date().isoformat(),'2026-11-04')
 def test_midnight_resets_gms_only_at_singapore_midnight(self):
  posts=[dict(stamp='2026-11-03T15:59:59Z'),dict(stamp='2026-11-03T16:00:00Z')]
  now=dt.datetime(2026,11,3,16,1,tzinfo=dt.timezone.utc)
  self.assertEqual(count_today(posts,now,'gms'),1)
  self.assertEqual(count_today(posts,now,'sp'),2)
 def test_gms_uses_singapore_slots_with_minutes(self):
  now=dt.datetime(2026,11,4,8,16,tzinfo=SINGAPORE)
  self.assertEqual(target(now,'gms'),0)
  self.assertEqual(target(now.replace(minute=17),'gms'),1)
  self.assertEqual(target(now.replace(hour=12,minute=17),'gms'),3)
  self.assertEqual(target(now.replace(hour=21,minute=17),'gms'),8)
 def test_european_trigger_cannot_publish_gms(self):
  self.assertEqual(selected_brands(EU_CRON),('sp','sin'))
  self.assertEqual(selected_brands(GMS_CRON),('gms',))
  self.assertEqual(selected_brands('', 'gms'),('gms',))
  with self.assertRaises(ValueError):selected_brands('unrecognized schedule')
 def test_singapore_morning_runs_during_owners_night(self):
  singapore=dt.datetime(2026,11,4,8,17,tzinfo=SINGAPORE)
  self.assertEqual(singapore.astimezone(TZ).strftime('%H:%M'),'01:17')
  self.assertEqual(target(singapore,'gms'),1)
  self.assertEqual(target(singapore,'sp'),0)
 def test_facebook_spacing_uses_actual_elapsed_time_in_singapore(self):
  now=dt.datetime(2026,11,4,15,17,tzinfo=SINGAPORE)
  self.assertFalse(gap_ok([dict(stamp='2026-11-04T06:18:00Z')],now,60))
  self.assertTrue(gap_ok([dict(stamp='2026-11-04T06:17:00Z')],now,60))
 def test_reviewed_queue_and_reel_match_local_time(self):
  import json
  from pathlib import Path
  items=json.loads((Path(__file__).parent/'queue.json').read_text())
  for day in ('2026-11-03','2026-11-04','2026-11-05'):
   ordered=sorted([x for x in items if x['brand']=='gms' and x['date']==day],key=lambda x:x['publish_order'])
   self.assertEqual([x['publish_order'] for x in ordered],list(range(1,9)))
   self.assertEqual(ordered[2].get('kind'),'reel')
   self.assertTrue(all(x['market_timezone']=='Asia/Singapore' for x in ordered))
 def test_all_gms_inner_guards_use_singapore(self):
  from pathlib import Path
  root=Path(__file__).parent/'publishers/gms'
  for filename in ('ig_publish.py','reel_publish.py','channel_guard.py','threads_publish.py','fb_publish.py'):
   source=(root/filename).read_text()
   self.assertIn('ZoneInfo("Asia/Singapore")',source)
   self.assertNotIn('ZoneInfo("Europe/',source)

if __name__=='__main__':unittest.main()
