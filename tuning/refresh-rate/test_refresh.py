import importlib.machinery, importlib.util, tempfile, unittest
from pathlib import Path

path = Path(__file__).resolve().parent / 'mseries-refresh'
loader = importlib.machinery.SourceFileLoader('mseries_refresh', str(path))
spec = importlib.util.spec_from_loader('mseries_refresh', loader)
refresh = importlib.util.module_from_spec(spec)
loader.exec_module(refresh)

MODES = [('a', 3024, 1890, 120.0), ('b', 3024, 1890, 60.0), ('c', 3024, 1890, 59.94), ('d', 1920, 1200, 60.0)]


class RefreshTests(unittest.TestCase):
    def test_picks_closest_rate_at_the_same_size(self):
        self.assertEqual(refresh.pick_mode(MODES, MODES[0], 60)[0], 'b')
        self.assertEqual(refresh.pick_mode(MODES, MODES[1], 120)[0], 'a')

    def test_never_changes_resolution(self):
        self.assertEqual(refresh.pick_mode(MODES, MODES[3], 120)[0], 'd')

    def test_target_follows_source(self):
        config = refresh.DEFAULTS
        self.assertEqual(refresh.target_hz(config, True), 60)
        self.assertEqual(refresh.target_hz(config, False), 120)

    def test_config_parsing_and_bad_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'refresh.conf'
            p.write_text('battery_hz = 48  # saver\nac_hz=100\nenabled = off\n')
            c = refresh.load_config(p)
            self.assertEqual((c['battery_hz'], c['ac_hz'], c['enabled']), (48.0, 100.0, False))
            self.assertEqual(refresh.load_config(Path(d) / 'missing')['battery_hz'], 60.0)
            p.write_text('battery_hz = banana\n')
            self.assertEqual(refresh.load_config(p)['battery_hz'], 60.0)


class DynamicTests(unittest.TestCase):
    cfg = dict(refresh.DEFAULTS, dynamic=True)

    def test_idle_drops_to_low_and_input_restores(self):
        self.assertEqual(refresh.decide_dynamic(self.cfg, False, 20000, 120.0, 60), 60.0)    # idle on AC -> low
        self.assertEqual(refresh.decide_dynamic(self.cfg, False, 500, 60.0, 60), 120.0)      # input -> back up

    def test_no_change_when_already_right_or_too_soon(self):
        self.assertIsNone(refresh.decide_dynamic(self.cfg, False, 20000, 60.0, 60))          # already low
        self.assertIsNone(refresh.decide_dynamic(self.cfg, False, 20000, 120.0, 5))          # dwell not elapsed
        self.assertIsNone(refresh.decide_dynamic(self.cfg, False, 500, 120.0, 60))           # active, already high

    def test_battery_active_rate_is_the_battery_rate(self):
        self.assertIsNone(refresh.decide_dynamic(self.cfg, True, 500, 60.0, 60))             # battery caps active at 60
        self.assertEqual(refresh.decide_dynamic(self.cfg, True, 500, 120.0, 60), 60.0)

    def test_low_never_exceeds_active(self):
        cfg = dict(self.cfg, low_hz=90.0, battery_hz=60.0)
        self.assertEqual(refresh.decide_dynamic(cfg, True, 20000, 90.0, 60), 60.0)


if __name__ == '__main__':
    unittest.main()
