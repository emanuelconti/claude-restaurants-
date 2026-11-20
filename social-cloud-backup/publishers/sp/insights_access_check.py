"""One-shot, read-only diagnosis using the existing SocialPerks grant only."""
import datetime as dt
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'gms'))
import ig_publish as IG

EXPECTED = 'socialperks.es'
USER = '17841450639747283'


def diagnose(token):
    host = 'graph.facebook.com' if token.startswith('EAA') else 'graph.instagram.com'
    result = {'schema_version': 1, 'checked_at': dt.datetime.now(dt.timezone.utc).isoformat(),
              'account': EXPECTED, 'host': host, 'checks': {}}
    for version in ('v21.0', 'v27.0'):
        IG.API = f'https://{host}/{version}'
        check = {}
        result['checks'][version] = check
        try:
            identity = IG.call('GET', USER, token, {'fields': 'username'})
            if identity.get('username') != EXPECTED:
                check['identity'] = 'mismatch; stopped'
                break
            check['identity'] = 'verified'
            try:
                permissions = IG.call('GET', 'me/permissions', token).get('data', [])
                relevant = {'instagram_basic', 'instagram_manage_insights', 'pages_read_engagement',
                            'instagram_business_basic', 'instagram_business_manage_insights'}
                check['permissions'] = [{'permission': p.get('permission'), 'status': p.get('status')}
                                        for p in permissions if p.get('permission') in relevant]
            except Exception as error:
                check['permissions_error'] = str(error).replace(token, '[redacted]')[:300]
            media = IG.call('GET', USER + '/media', token, {'fields': 'id', 'limit': 1}).get('data', [])
            if not media:
                check['views'] = 'no media available'
                continue
            metrics = IG.call('GET', str(media[0]['id']) + '/insights', token,
                              {'metric': 'views'}).get('data', [])
            check['views'] = 'available' if any(m.get('name') == 'views' for m in metrics) else 'not returned'
        except Exception as error:
            check['error'] = str(error).replace(token, '[redacted]')[:300]
    return result


if __name__ == '__main__':
    print(json.dumps(diagnose(os.environ['INSTAGRAM_ACCESS_TOKEN'])))
