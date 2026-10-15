import importlib.machinery, importlib.util, unittest
from pathlib import Path

path = Path(__file__).resolve().parent / 'mseries-profile'
loader = importlib.machinery.SourceFileLoader('mseries_profile', str(path))
spec = importlib.util.spec_from_loader('mseries_profile', loader)
profile = importlib.util.module_from_spec(spec)
loader.exec_module(profile)


class ProfileTests(unittest.TestCase):
    def kinds(self, steps):
        return [(a[0], str(a[1]) if len(a) > 1 else '') for _, a in steps]

    def test_battery_has_no_display_step_by_default(self):
        text = ' '.join(d for d, _ in profile.plan('battery'))
        self.assertNotIn('VISIBLE', text)
        self.assertIn('power-saver', text)

    def test_display_step_only_with_flag(self):
        self.assertTrue(any('VISIBLE' in d for d, _ in profile.plan('battery', display=True)))

    def test_balanced_undoes_battery(self):
        self.assertIn(('remove', str(profile.WP_FILE)), self.kinds(profile.plan('balanced')))

    def test_never_touches_brightness_or_kernel(self):
        blob = repr(profile.plan('battery', display=True) + profile.plan('balanced', display=True)).lower()
        for word in ('brightness', 'backlight', 'grub', 'm1n1', 'speakersafetyd', 'charge_control'):
            self.assertNotIn(word, blob)

    def test_unknown_profile_rejected(self):
        with self.assertRaises(SystemExit):
            profile.plan('turbo')


if __name__ == '__main__':
    unittest.main()
