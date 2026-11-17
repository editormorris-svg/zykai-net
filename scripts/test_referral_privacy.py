"""Guard: internal referral economics must never reach the public site.

Owner directive 2026-11-17: the NAE Staff-Get-Staff referral bonus schedule is
ZYKai's own commercial interest. We never publish or mention it. Public pages
show the referral route and referrer attribution only.

See ops/change-log/2026-11-17-referral-bonus-never-publish.md.
"""
import json
import re
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_SITE = ROOT / 'public-site'
PUBLIC_CATALOG = PUBLIC_SITE / 'assets/data/jobs-catalog.json'

# Catalog keys that carry internal referral economics / bulletin data / HR contacts.
PRIVATE_KEYS = (
    'referral_bonus_program',
    'referral_program',
    'last_referral_program_ingest',
    'referral_bonus_publication_policy',
    'internal_bulletin',
    'last_internal_bulletin_ingest',
)

# Public HTML must never carry the bonus table or the internal program name.
FORBIDDEN_PHRASES = (
    'Staff Get Staff Referral Bonus',
    'referral-bonus',
    'Referral Bonus Policy',
    '内推奖励标准',
    '內推獎勵標準',
)

# Internal HR personal addresses (school/group staff), never published.
HR_ADDRESS = re.compile(r'[a-z][a-z0-9._-]*@(?:nacis|nordanglia)[a-z0-9.-]*\.(?:cn|com)', re.I)


class ReferralPrivacyTests(unittest.TestCase):
    def test_public_catalog_has_no_private_keys(self):
        self.assertTrue(PUBLIC_CATALOG.is_file(), f'missing {PUBLIC_CATALOG}')
        catalog = json.loads(PUBLIC_CATALOG.read_text(encoding='utf-8'))
        leaked = [k for k in PRIVATE_KEYS if k in catalog]
        self.assertEqual(leaked, [], f'internal referral keys published: {leaked}')
        self.assertGreater(len(catalog.get('jobs', [])), 0, 'public catalog has no jobs')

    def test_public_html_has_no_bonus_program(self):
        pages = sorted(PUBLIC_SITE.glob('*/*.html'))
        self.assertGreater(len(pages), 0, 'no public HTML pages found')
        for page in pages:
            text = page.read_text(encoding='utf-8')
            for phrase in FORBIDDEN_PHRASES:
                with self.subTest(page=page.name, phrase=phrase):
                    self.assertNotIn(phrase, text, f'{page} still publishes the internal referral bonus program')

    def test_no_internal_hr_addresses_published(self):
        targets = [PUBLIC_CATALOG, *sorted(PUBLIC_SITE.glob('*/*.html'))]
        for target in targets:
            text = target.read_text(encoding='utf-8')
            hits = sorted(set(HR_ADDRESS.findall(text)))
            with self.subTest(target=target.name):
                self.assertEqual(hits, [], f'internal HR address(es) published in {target}: {hits}')

    def test_referral_route_still_present(self):
        """The public referral page must still offer the route, minus figures."""
        for locale in ('en', 'zh-cn', 'zh-hk'):
            page = PUBLIC_SITE / locale / 'referral.html'
            with self.subTest(locale=locale):
                self.assertTrue(page.is_file(), f'missing {page}')
                text = page.read_text(encoding='utf-8')
                self.assertIn('id="referral-route"', text, f'{page} lost the referral route section')
                self.assertIn('data-job-id=', text, f'{page} lost the job cards')


if __name__ == '__main__':
    unittest.main()
