# Research-site complete manuscript audit and executable falsification (2026-11-19)

Source: [rabdelaal/rabdelaal.github.io](https://github.com/rabdelaal/rabdelaal.github.io/tree/4e1c7bf529436b9e802ae27a733bc3b07800a35c/papers), pinned at commit `4e1c7bf529436b9e802ae27a733bc3b07800a35c`. The nine paper bodies are stored as Markdown despite the public HTML page displaying "Loading paper content..." to static fetchers. We inspected the manuscript text and checked its methods/claimed results. **Manuscript assertions are not treated as peer review or independent empirical confirmation.**

## Nine-paper triage: what survives first principles

| Paper | Actual empirical basis in manuscript | Reuse / caution |
| --- | --- | --- |
| SSR / Three-Kernel | Python NumPy *discrete-time cost simulation* of 1000 virtual machines, simulated SSR vs GSEE 1.8×; not native GPU performance | Reuse overlap/rollback hypothesis; no real GPU speedup evidence |
| SSR Omega | Modular orchestration blueprint and example pseudo-code; no comparable production performance | Can inspire DAG scheduling; not CPU math kernel acceleration |
| vTRN | Synthetic long-range-copy benchmark vs full self-attention; different model capacities unconfirmed | Linear scaling conditional on fixed number of memory nodes; cannot establish superior quality vs efficient attention |
| is-vTRN | Manuscript: 2.83s training, 58.6% test accuracy vs Transformer 22.14s, **60.2%**; models not equivalent | Claimed 7.8× *training time* on synthetic grammar task, not matched-quality proof |
| SDRC | A*B+C*D regression: 0.71s / MAE 11.51 vs serial baseline 0.74s / 11.56; both MAEs high | Decomposition and supervised residues plausible; improvements small and no matched-seed uncertainty reported |
| SyS-Fused | Synthetic bag-of-words logistics: **0.97s, loss 8.00e-5** vs momentum **0.77s, loss 8.68e-5** | Proposed fused weight update is an optimizer heuristic; measured training **slower**, not latency hiding |
| GEPARD | Vanilla-Python `Continuum-v0` control benchmark, tree parsimony comparisons | Reuse compact policy search / penalties after stronger seeded baselines |
| Cognitive Resonance Cascade | Black-box optimization on synthetic proxies and literature/externally supplied results | Defer; verify on reproducible standard BBO suites first |
| SPEAR embedded control | Printed pendulum ODE and Lyapunov calculation; claimed controller and MCU numbers | **Paper contains a falsifiable algebraic contradiction; do not reuse stability certificate or hardware claims** |

Other unlisted Markdown files under `papers/` make speculative assertions about vacuum energy, infinite batteries and propulsion; these are **not established physical results** and are outside SPEAR Unified's numerical CPU scope.

## Critical falsification: pendulum stability derivation

The embedded SPEAR paper gives:

`theta'' = (3g/(2l))sin(theta) + (3/(m*l^2))*u`

and proposes:

`V = 1/2*m*l^2*omega^2 + m*g*l*(1-cos(theta))`.

Its printed derivative **incorrectly omits the gravitational component** and writes:

`Vdot_claimed = 3*omega*u`.

Differentiation of the equations **as printed** actually yields:

`Vdot_actual = (5/2)*m*g*l*omega*sin(theta) + 3*omega*u`.

Counterexample for `m=l=1`, `g=9.81`, `theta=0.3`, `omega=0.01`, `u=clamp(-4.524403*omega*cos(theta),-2,2)`:

- `cos(theta)=0.9553 > 0` (within the paper's claimed stabilizing regime);
- `Vdot_claimed=-0.001296698183...` (negative);
- `Vdot_actual=+0.071179632500...` (positive);
- omitted term `+0.072476330684...`.

The published claim `Vdot<=0` in that region does not follow. In addition, with the paper's stated **positive** gravitational sign, a velocity-only damping policy has no restoring torque at zero velocity for theta away from 0. A deterministic RK4 integration starting at `theta=0.1, omega=0` yields `theta~0.847 rad`, positive growing energy at t=2 s (unit parameters). That is a **counterexample to the stated derivation**, not a complete re-evaluation of training, real hardware, or any other pendulum convention.

Reproduction:

```sh
python -m scripts.check_paper_claims
python -m unittest tests.test_paper_claims -v
```

Source: [full embedded control manuscript](https://github.com/rabdelaal/rabdelaal.github.io/blob/4e1c7bf529436b9e802ae27a733bc3b07800a35c/papers/SPEAR_%20Symbolic%20Policy%20Evolution%20for%20Ante-hoc%20Robust%20Control.md).

**Consequences:** neither the advertised asymptotic stability nor the quoted 235.3 ns MCU timing is certified by this derivation. MISRA or cycle count requires a real target build, linter and on-device measurement. Do not silently transplant the controller into safety-critical code. Fix or retract the mathematical claim in the research site separately after independent review.

## Integration decision

- **Reuse now:** methodology (train/holdout separation, Pareto parsimony, strict domain/precision and explicit fallback, predictable bounded computation). No fabricated speed claims.
- **Test next:** exact control policy on a repaired physical environment with independently benchmarked PD/PID baseline, repeated seeds and adversarial initial states. For a CPU product, opt-in real-workload SpearVM/TensorFold kernel evaluation has stronger evidence.
- **Do not activate:** SyS-Fused as a speed-up optimizer; SDRC speculative residual as an unverified speed-up; vTRN as matched-quality replacement for attention; the embedded controller as formally stabilized.

## Verification status

- Full source Markdown: **read** (nine listed papers, additional proof files).
- Deterministic numeric counterexample: **executed locally** and tested in Python CI.
- Physical hardware/optimizer training/LLM inference reproduction: **not done**.
- Paper text corrections in source research-site repo: **not performed**, because the required scientific revisions need independent confirmation and traceable benchmark evidence.
