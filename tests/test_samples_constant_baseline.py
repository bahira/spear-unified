"""Train-only constant baseline, including empty range groups."""
import test_samples_coverage as coverage
import unittest
import shutil

@unittest.skipUnless(shutil.which('node'), 'Node required')
class SamplesConstantBaselineChecks(unittest.TestCase):
    setUp = coverage.SamplesCoverageChecks.setUp
    run_samples = coverage.SamplesCoverageChecks.run_samples

    def fixture(self):
        return {'train':list(range(8)), 'validation':[-2,-1,.25,.75,3.25,6.75,8,9]}

    def test_mean_and_errors_are_computed_from_training_only(self):
        xs = self.fixture()
        r = self.run_samples(xs)
        mean = sum(x*x+1 for x in xs['train'])/8
        self.assertEqual(r['constant_baseline']['value'], mean)
        for name, values in xs.items():
            m = r['splits'][name]['constant_baseline']
            self.assertEqual(m['n'], len(values))
            self.assertAlmostEqual(m['mse'],sum((mean-(x*x+1))**2 for x in values)/len(values))
        self.assertIn('constante', (self.root/'reports/samples-discovery.md').read_text())

    def test_heldout_coordinates_and_labels_do_not_change_constant(self):
        a = self.run_samples(self.fixture())
        b = self.run_samples({'train':list(range(8)), 'validation':list(range(8,16))})
        self.assertEqual(a['constant_baseline'],b['constant_baseline'])
        self.assertEqual(a['candidate'],b['candidate'])

    def test_group_metrics_and_empty_groups(self):
        r = self.run_samples(self.fixture())
        groups = r['range_metrics']['validation']
        self.assertAlmostEqual(sum(groups[g]['constant_baseline']['mse']*groups[g]['constant_baseline']['n']
                                   for g in groups)/8, r['splits']['validation']['constant_baseline']['mse'])
        self.assertIsNone(r['range_metrics']['train']['outside_training'])
        self.assertNotIn('test',r['range_metrics'])
