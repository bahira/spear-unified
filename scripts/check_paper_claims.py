"""Reproduce a counterexample to the printed pendulum Lyapunov identity.

Only tests equations printed in SPEAR embedded-control manuscript. Does not
reproduce training, real-policy task rewards, MCU timing, or hardware claims.
Run: python -m scripts.check_paper_claims
"""
import json
import math

G = 9.81
K = 4.524403
MAX_TORQUE = 2.0


def control(theta, omega):
    return max(-MAX_TORQUE, min(MAX_TORQUE, -K * omega * math.cos(theta)))


def acceleration(theta, omega, m=1.0, l=1.0):
    return 3.0 * G / (2.0 * l) * math.sin(theta) + 3.0 * control(theta, omega) / (m * l * l)


def energy(theta, omega, m=1.0, l=1.0):
    return 0.5 * m * l * l * omega**2 + m * G * l * (1.0 - math.cos(theta))


def energy_derivative(theta, omega, m=1.0, l=1.0):
    return omega * (m * l * l * acceleration(theta, omega, m, l) + m * G * l * math.sin(theta))


def manuscript_claimed_derivative(theta, omega):
    return 3.0 * omega * control(theta, omega)


def rk4_step(theta, omega, dt):
    def derivative(t, w):
        return w, acceleration(t, w)
    k1 = derivative(theta, omega)
    k2 = derivative(theta + dt*k1[0]/2, omega + dt*k1[1]/2)
    k3 = derivative(theta + dt*k2[0]/2, omega + dt*k2[1]/2)
    k4 = derivative(theta + dt*k3[0], omega + dt*k3[1])
    return (theta + dt*(k1[0]+2*k2[0]+2*k3[0]+k4[0])/6,
            omega + dt*(k1[1]+2*k2[1]+2*k3[1]+k4[1])/6)


def local_eigenvalues(m=1.0, l=1.0):
    """Unsaturated linearized printed plant with velocity-only control near origin."""
    a = 3.0 * G / (2.0 * l)
    damping = 3.0 * K / (m * l*l)
    root = math.sqrt(damping*damping + 4.0*a)
    return ((-damping + root)/2.0, (-damping - root)/2.0)


def cycles_to_ns(cycles, clock_mhz):
    """Idealized cycle timing lower bound, not a compiled-kernel measurement."""
    if type(cycles) not in (int, float) or type(clock_mhz) not in (int, float) or not math.isfinite(cycles) or not math.isfinite(clock_mhz) or cycles <= 0 or clock_mhz <= 0:
        raise ValueError('Cycles and clock frequency must be finite positive numbers')
    return 1000.0 * cycles / clock_mhz


def run(duration=2.0, dt=0.001):
    theta, omega = 0.1, 0.0
    trace = [(0.0, theta, omega, energy(theta, omega))]
    for i in range(1, int(duration/dt) + 1):
        theta, omega = rk4_step(theta, omega, dt)
        if i % 100 == 0:
            trace.append((i*dt, theta, omega, energy(theta, omega)))
    t, w = 0.3, 0.01
    return {
        'source_commit': '4e1c7bf529436b9e802ae27a733bc3b07800a35c',
        'system': 'printed pendulum dynamics with m=l=1, g=9.81, torque clipped ±2',
        'counterexample_state': {'theta': t, 'omega': w, 'cos_theta': math.cos(t)},
        'actual_Vdot': energy_derivative(t, w),
        'manuscript_Vdot': manuscript_claimed_derivative(t, w),
        'omitted_gravity_term': 2.5*G*w*math.sin(t),
        'linearized_origin_eigenvalues_per_second': list(local_eigenvalues()),
        'three_cycles_at_84mhz_ns': cycles_to_ns(3, 84),
        'trace': trace,
        'limits': 'Numerical illustration only; no hardware timing, complete simulator reproduction, or global Lyapunov certificate.'
    }


def main():
    print(json.dumps(run(), indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
