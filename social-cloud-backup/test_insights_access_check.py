import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('insights_access_check', Path(__file__).parent / 'publishers/sp/insights_access_check.py')
diagnostic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diagnostic)


class AccessCheckTests(unittest.TestCase):
    def test_wrong_account_stops_before_permissions_or_media(self):
        with patch.object(diagnostic.IG, 'call', return_value={'username': 'wrong'}) as call:
            result = diagnostic.diagnose('test-token')
        self.assertEqual(call.call_count, 1)
        self.assertEqual(result['checks']['v21.0']['identity'], 'mismatch; stopped')

    def test_diagnosis_is_read_only_and_redacts_denial(self):
        token = 'EAAtest-private-token'
        def call(method, path, access, params=None):
            self.assertEqual(method, 'GET')
            self.assertEqual(access, token)
            if path == diagnostic.USER: return {'username': diagnostic.EXPECTED}
            if path == 'me/permissions': return {'data': [{'permission': 'instagram_basic', 'status': 'granted'}]}
            if path.endswith('/media'): return {'data': [{'id': 'own-media'}]}
            raise RuntimeError('permission denied ' + token)
        with patch.object(diagnostic.IG, 'call', side_effect=call):
            result = diagnostic.diagnose(token)
        self.assertNotIn(token, json.dumps(result))
        self.assertEqual(len(result['checks']), 2)
        self.assertIn('[redacted]', result['checks']['v27.0']['error'])
