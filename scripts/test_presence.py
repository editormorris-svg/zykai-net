import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('presence', ROOT / 'scripts/build_presence.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PresenceTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / 'brand/presence.json').read_text(encoding='utf-8'))
        self.queue = json.loads((ROOT / 'brand/social-launch.json').read_text(encoding='utf-8'))

    def profile(self, account='new-zyk-test-account'):
        return {'platform': 'facebook', 'account_id': account, 'url': 'https://www.facebook.com/zyk-test',
                'brand': 'ZYK', 'ownership_confirmed': True, 'verified_at': '2026-10-05',
                'verification_note': 'Synthetic unit-test fixture; not a real account.'}

    def test_drafts_validate(self):
        self.assertEqual(module.validate(self.config, self.queue), 8)

    def test_all_historical_destinations_rejected(self):
        for identifier in module.LEGACY_IDS:
            with self.subTest(identifier=identifier):
                config = copy.deepcopy(self.config)
                config['verified_profiles'] = [self.profile(identifier)]
                with self.assertRaises(ValueError):
                    module.validate(config, self.queue)

    def test_missing_ownership_rejected(self):
        profile = self.profile()
        profile['ownership_confirmed'] = False
        self.config['verified_profiles'] = [profile]
        with self.assertRaises(ValueError):
            module.validate(self.config, self.queue)

    def test_lookalike_domain_rejected(self):
        profile = self.profile()
        profile['url'] = 'https://www.facebook.com.example.org/zyk'
        self.config['verified_profiles'] = [profile]
        with self.assertRaises(ValueError):
            module.validate(self.config, self.queue)

    def test_publishing_cannot_be_enabled(self):
        self.config['publishing_enabled'] = True
        with self.assertRaises(ValueError):
            module.validate(self.config, self.queue)

    def test_duplicate_posts_rejected(self):
        self.queue['posts'].append(copy.deepcopy(self.queue['posts'][0]))
        with self.assertRaises(ValueError):
            module.validate(self.config, self.queue)

    def test_approval_without_evidence_rejected(self):
        self.queue['posts'][0]['status'] = 'approved'
        with self.assertRaises(ValueError):
            module.validate(self.config, self.queue)

    def test_private_contact_rejected(self):
        self.config['email'] = '2026wm@gmail.com'
        with self.assertRaises(ValueError):
            module.validate(self.config, self.queue)

    def test_localised_channel_templates(self):
        template = '<html><head><title>Home</title><meta name="description" content="Old"></head><body><main>Old main</main><footer><div class="wrap">ZYK</div></footer></body></html>'
        with tempfile.TemporaryDirectory() as temporary:
            site = Path(temporary)
            for lang in module.COPY:
                (site / lang).mkdir()
                (site / lang / 'channels.html').touch()
            for lang in module.COPY:
                page = module.channel_page(template, lang, [])
                page = module.enrich(page, Path(lang) / 'channels.html', self.config, site)
                self.assertIn('mailto:hello@zykai.net', page)
                self.assertIn(module.COPY[lang][0], page)
                self.assertNotIn('Old main', page)
                self.assertNotIn('sameAs', page)
                self.assertIn('https://zykai.net/' + lang + '/channels.html', page)
                self.assertEqual(page.count('<main>'), 1)
                self.assertEqual(page.count('hreflang='), 4)


if __name__ == '__main__':
    unittest.main()
