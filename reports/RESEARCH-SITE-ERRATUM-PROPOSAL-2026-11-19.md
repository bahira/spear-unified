# Proposed public research-site erratum — 2026-11-19

**Status: prepared only, NOT published to the research site.** A GitHub connector attempt to create a branch in `rabdelaal/rabdelaal.github.io` returned HTTP 403 (resource inaccessible). The repository remains unchanged by this work. The manuscript's text was read at commit `4e1c7bf529436b9e802ae27a733bc3b07800a35c`.

## Priority 0: Embedded SPEAR paper — mathematical correction

Original: [SPEAR: Symbolic Policy Evolution for Ante-hoc Robust Control](https://github.com/rabdelaal/rabdelaal.github.io/blob/main/papers/SPEAR_%20Symbolic%20Policy%20Evolution%20for%20Ante-hoc%20Robust%20Control.md).

**Public advisory to prepend:**

> ERRATUM (2026-11-19): The previous Lyapunov proof in §4.3 is incorrect for the plant equation stated in §4.1. Its expression for `Vdot` omits a gravity term; the proposed velocity-only controller is not shown stable. The 4.2 ns / 3 cycles at 84 MHz timing claim is inconsistent with the stated clock, and is not a hardware-verified benchmark. Stability certification, safety-critical deployment claims and target-cycle claims are withdrawn pending corrected dynamics, independent verification and on-device measurements.

**Replace §4.3 derivative and stability conclusion with:**

```text
For theta_ddot = (3g/2l)*sin(theta) + (3/ml²)*u
and V = (ml²/2)*theta_dot² + mgl*(1-cos(theta)),
Vdot = (5mgl/2)*theta_dot*sin(theta) + 3*theta_dot*u.

The prior Vdot=3*theta_dot*u cancels the gravity term incorrectly.
Therefore the sign and asymptotic-stability conclusions do not follow.
At m=l=1, g=9.81, theta=0.3, theta_dot=0.01,
u=clip(-4.524403*theta_dot*cos(theta),-2,+2):
 Vdot(actual) = +0.071179632500...
 Vdot(old)    = -0.001296698183...
This is a counterexample within the region cos(theta)>0.

Near theta=0 the unsaturated closed loop linearizes to
theta_ddot = 14.715*theta - 13.573209*theta_dot,
whose eigenvalues are about +1.0091 and -14.5823 per second.
The positive eigenvalue is incompatible with local asymptotic
stability for the printed plant and policy.

These statements concern the specific printed equations only.
Any different pendulum sign/coordinate convention must be
specified and independently re-derived before safety claims.
```

**Target timing correction:**

At 84 MHz, one clock is 11.90 ns and three clocks require **35.71 ns**, not 4.2 ns. This is a theoretical arithmetic lower bound *given the claimed cycle count*, not an observed compiled C runtime. The macro `SATURATE` and `cos_theta` evaluation are not proven to execute in three cycles. Actual cycle count must be measured with the target MCU, compiler, flags and a hardware counter before quoting performance.

**Certification correction:** a small C function is not by itself a MISRA-C:2012-compliant, DO-178C Level A certified controller or a proof of safety. Such assertions require separate static checks, system-level safety cases, adversarial operating-envelope tests and certification evidence.

Reproducible diagnostics: [scripts/check_paper_claims.py](https://github.com/bahira/spear-unified/blob/main/scripts/check_paper_claims.py), [tests/test_paper_claims.py](https://github.com/bahira/spear-unified/blob/main/tests/test_paper_claims.py), [full-paper audit](FULL-PAPERS-VERIFICATION-2026-11-19.md).

## Priority 1: Other paper presentation corrections

- **SyS-Fused**: report shows 0.97 s vs momentum 0.77 s; the measured implementation is **slower**, despite lower final *training* loss (8.00e-5 vs 8.68e-5) on a synthetic task. Do not market as proven latency hiding, superior validation quality or GPU speed.
- **SDRC**: reports MAE 11.51 vs 11.56, duration 0.71 s vs 0.74 s on a synthetic task. Difference is marginal, both errors large, no multi-seed uncertainty. No demonstrated real LLM speedup.
- **is-vTRN**: reports 2.83 s / 58.6% accuracy vs Transformer 22.14 s / 60.2%. Faster but **lower** accuracy; architectures and budgets differ. Not a matched-quality comparison.
- **SSR**: 1.8× is from discrete-time *simulation*, not GPU execution.
- **vTRN**: linear complexity holds only with bounded node count, top-k and width, and does not independently prove competitive task quality.

## Required to publish corrections

1. Restore authenticated write access to the public-site repository.
2. Apply a precise, reviewable PR with erratum atop the manuscript and correction in §4.3 and MCU section.
3. Run site HTML/link checks and verify rendered Markdown page.
4. Obtain independent control-theory review before reinstating any stability or critical-system claims.

**No PR or commit was applied to the research-site repository.**
