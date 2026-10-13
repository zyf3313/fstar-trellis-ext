import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from database import configuration


class DatabaseScopeTest(unittest.TestCase):
    def setUp(self):
        self.source = {'id': 'app_dev_ro', 'engine': 'postgres', 'environment': 'development',
                       'dsn_env': 'APP_DEV_DSN', 'readonly': True}

    def test_no_database_or_missing_credentials_is_not_connected(self):
        content, report = configuration(Path.cwd(), {'sources': []}, {})
        self.assertIsNone(content)
        self.assertEqual(report['status'], 'not_applicable')
        content, report = configuration(Path.cwd(), {'sources': [self.source]}, {})
        self.assertEqual(report['status'], 'missing_credentials')
        self.assertEqual(report['missing_references'], ['APP_DEV_DSN'])

    def test_credential_values_are_not_written_to_config_or_report(self):
        secret = 'postgres://user:private-password@localhost/database'
        content, report = configuration(Path.cwd(), {'sources': [self.source]}, {'APP_DEV_DSN': secret})
        self.assertIn('${APP_DEV_DSN}', content.decode())
        self.assertNotIn('private-password', content.decode() + json.dumps(report))
        self.assertIn('readonly = true', content.decode())

    def test_production_write_unknown_environment_and_wrong_engine_are_rejected(self):
        with self.assertRaises(ValueError):
            configuration(Path.cwd(), {'sources': [{**self.source, 'environment': 'production', 'readonly': False}]}, {})
        with self.assertRaises(ValueError):
            configuration(Path.cwd(), {'sources': [{**self.source, 'environment': 'unknown'}]}, {})
        with self.assertRaises(ValueError):
            configuration(Path.cwd(), {'sources': [self.source]}, {'APP_DEV_DSN': 'mysql://local/test'})


if __name__ == '__main__':
    unittest.main()
