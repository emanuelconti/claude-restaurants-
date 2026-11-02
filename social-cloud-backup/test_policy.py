import datetime as dt,unittest
from policy import TZ,target,seen,count_today,next_item,gap_ok,youtube_title,parse_ig_history
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
if __name__=='__main__':unittest.main()
