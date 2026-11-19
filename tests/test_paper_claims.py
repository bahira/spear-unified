"""Regression tests for claims reproduced from the complete source manuscripts."""
import math
import unittest

from scripts import check_paper_claims as paper


class PublishedPendulumCounterexampleTests(unittest.TestCase):
    def test_printed_lyapunov_identity_omits_gravity(self):
        theta, omega = 0.3, 0.01
        actual = paper.energy_derivative(theta, omega)
        claimed = paper.manuscript_claimed_derivative(theta, omega)
        expected_gap = 2.5 * paper.G * omega * math.sin(theta)
        self.assertAlmostEqual(actual - claimed, expected_gap, places=12)
        self.assertGreater(actual, 0)
        self.assertLess(claimed, 0)
        self.assertGreater(math.cos(theta), 0)

    def test_finite_difference_energy_derivative_matches_correct_expression(self):
        theta, omega = 0.3, 0.01
        h = 1e-6
        a = paper.acceleration(theta, omega)
        fd = (paper.energy(theta + h*omega, omega + h*a) -
              paper.energy(theta - h*omega, omega - h*a)) / (2*h)
        self.assertAlmostEqual(fd, paper.energy_derivative(theta, omega), delta=1e-8)

    def test_inverted_equilibrium_does_not_converge_from_small_displacement(self):
        trace = paper.run(duration=2, dt=0.001)['trace']
        self.assertEqual(trace[0][1:3], (0.1, 0))
        self.assertGreater(trace[-1][1], 0.5)
        self.assertGreater(trace[-1][3], trace[0][3])

    def test_local_linearization_has_positive_eigenvalue(self):
        # Positive root implies local instability for the printed dynamics
        # and unsaturated velocity-only controller; not a global theorem.
        positive, negative = paper.local_eigenvalues()
        self.assertGreater(positive, 1)
        self.assertLess(negative, -1)

    def test_three_cycles_at_84mhz_is_not_4_point_2_ns(self):
        actual = paper.cycles_to_ns(3, 84)
        self.assertAlmostEqual(actual, 35.71428571428571)
        self.assertGreater(actual, 4.2)
        for cycles, mhz in ((0, 84), (3, 0), (True, 84), (3, float('inf'))):
            with self.assertRaises(ValueError):
                paper.cycles_to_ns(cycles, mhz)

    def test_smaller_rk4_timestep_agrees(self):
        a = paper.run(duration=2, dt=0.001)['trace'][-1]
        b = paper.run(duration=2, dt=0.0005)['trace'][-1]
        self.assertAlmostEqual(a[1], b[1], delta=1e-5)
        self.assertAlmostEqual(a[2], b[2], delta=1e-5)


if __name__ == '__main__':
    unittest.main()
