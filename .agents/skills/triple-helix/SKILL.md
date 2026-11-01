---
name: triple-helix
description: >
  Triple Helix (Self-Contained Edition). A skill that makes the agent itself
  the runtime for four nested loops — Tactical (Pareto-Caveman), Strategic
  (Plan-Falsification), Operational (Grounded), and Retrospective (new).
  No external .py file needed: the agent reads this skill, internalizes the
  procedure, and executes all four loops on every non-trivial multi-step task.
  State persists in a JSON file the agent reads and writes itself.
  Use whenever two or more of {speed, plan-risk, output-quality} matter
  simultaneously, OR when the same task pattern recurs across sessions.
  Do NOT trigger for single-shot lookups or trivial transforms.
---

# Triple Helix — Self-Contained Edition

> **What it is**: An operating procedure for the agent. Four loops, four time scales, 25 hard rules, 15 anti-gaming patterns. State persists in a JSON file the agent reads and writes itself.
>
> **Why no .py**: The agent IS the runtime. It executes each loop as a thinking step, writes observations to state, and adapts its own thresholds across sessions. No import. No install. No dependency.

---

## 0. When to trigger

Trigger this skill when ALL of the following hold:
- The task has ≥3 sub-tasks or ≥2 decision points
- At least two of {speed, plan-risk, output-quality} are at stake
- The work will produce observable outcomes (artifacts, errors, user feedback)

Do NOT trigger for: single-shot lookups, format conversions, "fix this typo" tasks, or any task completable in one tool call.

---

## 1. State file (the agent's memory across sessions)

The agent maintains state at `/home/z/my-project/triple_helix_state.json`. **Create if missing.** Read at session start. Write at session end. **Never modify mid-loop.**

```json
{
  "session": 0,
  "signals": {
    "RFR": 0.0,
    "CSR": 1.0,
    "convergence_score": 0.0
  },
  "config": {
    "pareto_ratio": 0.20,
    "pareto_ratio_bounds": [0.10, 0.40],
    "pareto_ratio_delta": 0.05,
    "falsifier_K": 6,
    "falsifier_K_bounds": [3, 12],
    "active_falsifiers": [
      "F-RESOURCE", "F-DEPENDENCY", "F-SPEC",
      "F-SAFETY", "F-EDGE", "F-COUNTERFACTUAL"
    ],
    "grounded_min_depth": "L2",
    "probe_set_size": 5,
    "safety_locked_task_types": ["math_proof", "security_review"],
    "safety_locked_params": ["grounded_min_depth"]
  },
  "trials": [],
  "cooldowns": [],
  "discovered_signals": [],
  "discovered_edges": [],
  "cascade_reversals_this_session": 0,
  "sessions_since_self_retro": 0,
  "history": []
}
```

---

## 2. The 4 loops — execution order

For every non-trivial task, the agent executes these four loops **in order**. **No execution** (no file writes, no tool calls that change state) may happen until all four loops have completed planning.

```
                ┌─────────────────────────────────────────────────────┐
                │           RETROSPECTIVE LOOP (per-session-end)      │
                │   learns + adapts + rolls back + self-audits        │
                └──────────────── ┌────────────────── ─────────────────┘
                                 │ adapts parameters
                                 ▼
   TASK ──► TACTICAL LOOP ──► STRATEGIC LOOP ──► OPERATIONAL LOOP ──► OUTPUT
            (Pareto-Caveman)  (Plan-Falsification)  (Grounded)
            per-task ~ms      per-plan ~s           per-output ~min
            cuts 80% noise    falsifies the 20%     grounds each iter
                │                   │                      │
                │     skip-reversal │     gap-cite         │
                └────── cascade ────┴────── cascade ───────┘
```

### Loop 1 — Tactical (Pareto-Caveman) ~ms, per-task

**Goal**: cut 80% of noise, keep top 20% by impact.

**Procedure**:
1. Decompose the task into sub-tasks. Each sub-task gets:
   - `id` (e.g. `"auth-001"` — prefix = type)
   - `label` (human-readable)
   - `impact` (0..1, higher = more impactful)
   - `spec_critical` (bool — skipping causes a spec gap)
   - `falsifier_will_flag` (bool — strategic loop will produce a CE on this)
   - `grounded_gap_will_cite` (bool — operational loop will cite this as a gap)
2. Sort sub-tasks by impact, descending.
3. Keep top `pareto_ratio` (default `0.20`, ±0.05 adaptation per session). Mark the rest as `skipped`.
4. **Exceptions** (never skip):
   - `spec_critical=True`
   - Task type ∈ `safety_locked_task_types` (`math_proof`, `security_review`)
5. Record skip decisions in state for cascade reversal.

### Loop 2 — Strategic (Plan-Falsification) ~s, per-plan

**Goal**: falsify the 20% that survived the tactical cut.

**Procedure**:
1. For each kept sub-task, run K falsifiers (default 6, bounds [3, 12]):
   - **F-RESOURCE**: can this be done with available tools/time?
   - **F-DEPENDENCY**: are upstream sub-tasks assumed but skipped?
   - **F-SPEC**: does this match the user's actual spec (not paraphrased)?
   - **F-SAFETY**: any irreversible operations? side effects?
   - **F-EDGE**: what's the edge case that breaks this?
   - **F-COUNTERFACTUAL**: if this sub-task didn't exist, would the plan still work? (If yes → it's noise → demote.)
2. Each falsifier produces 0+ counterexamples (CEs).
3. Any CE citing a `skipped` sub-task → trigger cascade reversal (restore in Loop 1).
4. If a falsifier fires >80% of sessions with no plan improvement → demote (CSR < 0.40).
5. If a falsifier fires rarely but always saves the plan → promote (CSR > 0.80).
6. Dedup CEs across loops by `(subtask_id, observable_failure)` — anti-gaming TH-AF2.

### Loop 3 — Operational (Grounded) ~min, per-output

**Goal**: ground each iteration against ground truth. Prevents mirror-loop info decay (55% loss).

**Procedure**:
1. For each artifact produced, cite:
   - **ground-truth source** (file path, doc URL, user statement, tool output)
   - **depth**: `L0` (hearsay) / `L1` (paraphrased) / `L2` (direct quote) / `L3` (verified by tool)
   - Minimum depth = **L2** for non-trivial claims.
2. Gaps (claims without L2+ grounding) → flagged. Each gap may cite a skipped sub-task → cascade reversal.
3. Convergence score = `grounded_claims / total_claims`. Target ≥ 0.80.
4. Run probe set (default 5 probes per artifact): random spot-checks against ground truth.
5. Mark skill-coupled probes (probes that only fire when a specific skill is active). Their PHR contribution is discounted 0.5 unless they fire on ≥2 skills (TH-AF5).

### Loop 4 — Retrospective (new) ~s, per-session-end

**Goal**: learn which decisions mattered. Adapt. Roll back bad adaptations. Self-audit.

**Procedure** (run AFTER the task completes, before writing state):
1. Compute 4 signals:
   - **RFR** (Re-flag Rate) = (sub-tasks re-flagged by downstream loops that tactical skipped) / (total skipped). **Lower is better.**
   - **CSR** (CE Survival Rate) = (CEs that survived into final output) / (CEs raised). **Lower is better** — high CSR means falsifiers are noise.
   - **CBA** (Convergence-Block Attribution) = which sub-task types most often block convergence? 3-session pattern → permanent impact boost +0.30.
   - **PHR** (Probe Hit-Rate) = (probes that caught a real defect) / (probes run). **Higher is better.**
2. Apply adaptation rules (see §3).
3. Open/close trials. Apply rollbacks (see §4).
4. **Every 10th session**: run self-retrospective (re-audit all signals, all adaptations, all discovered edges). Cannot be disabled (rule 22).
5. Increment `session`. Append this session's summary to `history`. Write state file.

---

## 3. Adaptation rules (what the agent changes between sessions)

The agent may modify these parameters in state, **subject to all hard rules in §5**:

| Parameter | Trigger | Action | Bounds |
|-----------|---------|--------|--------|
| `pareto_ratio` | RFR > 0.20 | raise by 0.05 | [0.10, 0.40] |
| `pareto_ratio` | RFR < 0.05 for 3 consecutive sessions | lower by 0.05 | [0.10, 0.40] |
| `falsifier_K` (demote) | CSR < 0.40 | K -= 1, drop weakest falsifier | K ≥ 3 |
| `falsifier_K` (promote) | CSR > 0.80 | K += 1, add falsifier | K ≤ 12 |
| Sub-task impact (permanent) | CBA pattern across 3 sessions | +0.30 to that sub-task type's default impact | — |

Every adaptation opens a **trial**. Trials last 3 sessions. At trial end:
- **Improvement on ALL tracked signals** → confirm
- **ANY signal regression > 20%** → rollback
- **No improvement on ANY signal** → rollback (no neutral theater, TH-AF7)

---

## 4. Rollback & cooldown

- **Cooldown**: rolled-back `(param, delta)` tuples are blocked for `5 + floor(severity / 0.20)` sessions, capped at 15 (TH-AF14, adaptive cooldown).
- **Max rollbacks**: 1 per session per param (TH-AF10).
- **Multi-signal**: a trial snapshots ALL tracked signals (`RFR`, `CSR`, `convergence_score`). ANY regression → rollback, regardless of target improvement (TH-AF11). Rollback reason must list ALL regressed signals (rule 25).
- **Edge validation**: discovered edges demoted if avg convergence delta < 0 over 5 sessions (TH-AF13).
- **Signal freshness**: discovered signals demoted after 10 sessions without re-validation (TH-AF12).

---

## 5. The 25 hard rules (non-negotiable)

**v1 (rules 1-12)**:
1. No execution before all 4 loops have run.
2. No auto-reversal beyond 3 per session.
3. No threshold delta > ±0.05 per session.
4. No permanent change without 3-session pattern.
5. No cascade edge may form a cycle (DFS at insert).
6. No Retrospective-Loop skip.
7. No execution while auto-reversal is pending.
8. No falsifier demotion below `K_min = 3`.
9. No probe demotion below 3 inline probes.
10. No adaptation of safety-critical thresholds (`safety_locked_params`).
11. Retrospective state must be human-readable JSON.
12. RFR > 0.50 → session flagged unstable.

**v2 (rules 13-18)**:
13. No adaptation is permanent without 3-session trial.
14. No trial may exceed 3 sessions.
15. No retry of rolled-back `(param, delta)` within 5 sessions.
16. No neutral-theater (no improvement → rollback, not confirm).
17. Discovered signals require ≥3 occurrences AND ≥80% consistency.
18. Discovered edges require 2 occurrences.

**v3 (rules 19-25)**:
19. No trial may evaluate only the target signal.
20. ANY signal regression > 20% → rollback, regardless of target improvement.
21. Adaptive cooldown is mandatory.
22. Self-retrospective runs every 10 sessions (cannot be disabled).
23. Discovered signals demoted after 10 sessions without re-validation.
24. Discovered edges demoted if avg convergence delta < 0 over 5 sessions.
25. Multi-signal rollback reason must list ALL regressed signals.

---

## 6. The 15 anti-gaming patterns (TH-AF1..15)

| # | Pattern | Defense |
|---|---------|---------|
| TH-AF1 | Cross-skill cut-gaming | Cascade auto-restores any skipped sub-task cited by a CE or gap |
| TH-AF2 | Echo-critic across loops | Dedup by `(subtask_id, observable_failure)` |
| TH-AF3 | Retrospective over-fit | All deltas bounded ±0.05; 3-session pattern required for permanent change |
| TH-AF4 | Cascade loop | Max 3 auto-reversals per session |
| TH-AF5 | Skill-coupled probe gaming | Mark skill-coupled probes; PHR discounted 0.5 unless fires on ≥2 skills |
| TH-AF6 | Adaptation retry-loop | 5-session cooldown on rolled-back `(param, delta)` |
| TH-AF7 | Neutral-theater | No improvement after 3 sessions → rollback (not confirm) |
| TH-AF8 | Signal-overfit | ≥3 occurrences AND ≥80% consistency for promotion |
| TH-AF9 | Edge-overfit | 2-occurrence threshold; 1st occurrence does NOT trigger auto-reversal |
| TH-AF10 | Trial-cascade | Max 1 rollback per session per param |
| TH-AF11 | Single-signal confirmation bias | Multi-signal trial: ANY signal regression → rollback |
| TH-AF12 | Stale-signal gaming | 10-session re-validation window |
| TH-AF13 | Net-negative edge gaming | 5-session convergence delta check |
| TH-AF14 | Severity-blind retry | Adaptive cooldown: severity scales length |
| TH-AF15 | Meta-blocker accumulation | Periodic self-retrospective every 10 sessions |

---

## 7. The 11 mechanisms (across 3 generations)

### v1 mechanisms
1. **Cross-skill dependency cascade** — downstream loop flags a skipped sub-task → auto-reverse the skip (max 3/session).
2. **4 retrospective signals** — RFR, CSR, CBA, PHR.
3. **Learned signal detector** — cluster `(signal_type, subtask_type, outcome)` triples; ≥3 occ + ≥80% consistency → promoted.
4. **Edge discovery** — unknown sub-task type → `candidate_edge`; 2nd occurrence → `discovered_edge` + auto-reversal.

### v2 mechanisms
5. **Adaptation rollback** — every adaptation enters a 3-session trial; regression or no-improvement → auto-reverted.
6. **Cooldown on retries** — rolled-back `(param, delta)` tuples blocked for 5+ sessions.

### v3 mechanisms
7. **Multi-signal trial evaluation** — every trial snapshots ALL tracked signals; ANY regression → rollback (not just target signal).
8. **Periodic self-retrospective** — re-runs self-audit every 10 sessions; new meta-blockers auto-promote to v_next.
9. **Signal freshness decay** — discovered signals demoted if not re-validated in 10 sessions.
10. **Edge validation** — discovered edges demoted if avg convergence delta < 0 over 5 sessions.
11. **Adaptive cooldown** — `cooldown = 5 + floor(severity / 0.20)`, capped at 15.

---

## 8. Operating checklist (run this every non-trivial task)

```
[ ] 1. Read /home/z/my-project/triple_helix_state.json (create if missing)
[ ] 2. LOOP 1 — Tactical
        - Decompose task into sub-tasks (id, label, impact, spec_critical,
          falsifier_will_flag, grounded_gap_will_cite)
        - Sort by impact desc
        - Keep top pareto_ratio; mark rest skipped
        - Never skip: spec_critical=True OR safety_locked_task_types
[ ] 3. LOOP 2 — Strategic
        - Run K active falsifiers on each kept sub-task
        - Record CEs (dedup by subtask_id+failure)
        - Any CE citing a skipped sub-task → cascade reversal (≤3/session)
[ ] 4. LOOP 3 — Operational
        - Produce artifacts with L2+ grounding on every non-trivial claim
        - Cite source + depth for each claim
        - Run probe_set_size spot-checks
        - Compute convergence_score
        - Any gap citing a skipped sub-task → cascade reversal
[ ] 5. EXECUTE — only now: write files, call tools, make changes
[ ] 6. LOOP 4 — Retrospective
        - Compute RFR, CSR, CBA, PHR
        - Open/close adaptation trials
        - Apply rollbacks (max 1/param/session, ≥5-session cooldown)
        - sessions_since_self_retro += 1
        - If sessions_since_self_retro == 10 → run self-retrospective, reset counter
        - Increment session counter
[ ] 7. Write /home/z/my-project/triple_helix_state.json
[ ] 8. Output to user: ~5-line summary (loops run, cuts, CEs, convergence,
       adaptations, self-retro if any)
```

---

## 9. What to tell the user (transparency, not theater)

At session end, the agent reports in ~5 lines:
- Which loops ran
- Which sub-tasks were cut, which were cascade-restored
- Which falsifiers fired
- Convergence score
- Any adaptations made this session (trial or confirmed)
- Whether self-retrospective ran (every 10th session)

---

## 10. What this closes (honest accounting)

| Layer | Open candidates | Closed | Remaining |
|-------|-----------------|--------|-----------|
| Pareto-Caveman v1 §Still open | 6 | 3 (v1) | 3 |
| Plan-Falsification v2 §Still open | 6 | 2 (v1) | 4 |
| Grounded-Loop v9 §Still open | 12 | 2 (v1) | 10 |
| v1 §Still open | 10 | 3 (v2) + 0 (v3) | 7 |
| v2 §Still open | 10 | 5 (v3) | 5 |
| v3 §Still open | 10 | — | 10 (v4 candidates) |
| Anti-gaming patterns introduced | — | 15 (5 per version) | 0 |
| **Totals** | **44** | **15 + 15 patterns** | **29** |

---

## 11. Still open (v4 candidates, honest)

The most important v4 targets:
1. **Cross-adaptation interaction detection** — two adaptations might each be fine alone but conflict when both active. v3 evaluates trials independently.
2. **Real clustering algorithm** — replace rule-based ≥3/≥80% with DBSCAN.
3. **Real spec parsing for self-retrospective** — currently synthetic.
4. **Adaptive regression threshold per signal** — some signals are noisier than others.
5. **Exponential cooldown for catastrophic regressions** — currently linear.
6. **Rollback of confirmed adaptations** — conditions may change.

---

## 12. Migration note (from the .py edition)

If a previous project used `triple_helix.py` and has a `helix_state.json`:
1. Read the old `helix_state.json` directly — the schema is compatible (the agent uses the same field names).
2. No code import needed. The agent takes over as runtime on the next session.
3. Drop `triple_helix.py` — it is no longer referenced.

---

**Self-Contained Edition** · 4 loops · 11 mechanisms · 15 anti-gaming patterns · 25 hard rules · **no .py file** · state persists in JSON.

The other three skills think. Triple Helix learns how they think — and undoes its own mistakes.
