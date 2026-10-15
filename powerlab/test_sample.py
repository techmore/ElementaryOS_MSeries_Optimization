import os
import tempfile
import unittest
from pathlib import Path

from powerlab import sample


class SampleTests(unittest.TestCase):
    def test_summary_uses_median_not_mean(self):
        result = sample.summarize([12, 12, 12, 12, 12, 12, 12, 12, 12, 24])
        self.assertEqual(result['median_w'], 12)
        self.assertGreater(result['mean_w'], 13)
        self.assertEqual(result['max_w'], 24)

    def test_prefers_smc_total_system_power(self):
        with tempfile.TemporaryDirectory() as directory:
            hw = Path(directory) / 'hwmon3'
            hw.mkdir()
            (hw / 'name').write_text('macsmc_hwmon\n')
            (hw / 'power1_label').write_text('Total System Power\n')
            (hw / 'power1_input').write_text('8250000\n')
            sample.HWMON = Path(directory)
            found = sample.find_system_power()
            self.assertEqual(found, hw / 'power1_input')
            self.assertEqual(sample.read_watts(found), 8.25)
            sample.HWMON = Path(directory) / 'none'
            self.assertIsNone(sample.find_system_power())

    def test_run_with_fake_battery_and_interrupts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'power_now').write_text('-11700000\n')
            (root / 'status').write_text('Discharging\n')
            irq = root / 'interrupts'
            irq.write_text('CPU0 CPU1\n 1: 10 20 Level foo\n')
            sample.BATTERY, sample.INTERRUPTS, sample.HWMON = root, irq, root / 'no-hwmon'
            ticks = iter(range(0, 100))
            calls = []

            def sleep(_):
                calls.append(1)
                irq.write_text('CPU0 CPU1\n 1: %d %d Level foo\n' % (10 + 5 * len(calls), 20 + 5 * len(calls)))

            result = sample.run(3, sleep=sleep, clock=lambda: float(next(ticks)))
            self.assertEqual(result['median_w'], 11.7)
            self.assertEqual(result['status'], 'Discharging')
            self.assertEqual(result['top_irqs'][0]['irq'], '1 Level foo')
            self.assertGreater(result['top_irqs'][0]['per_s'], 0)


if __name__ == '__main__':
    unittest.main()
