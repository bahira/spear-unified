# SPEAR Unified

For substantive work, read `.agents/skills/triple-helix/SKILL.md`, `GOAL.md` and `.agents/triple_helix_state.json` first. Apply the skill with the following explicit environment adaptations:

- State lives in `.agents/triple_helix_state.json`, not the skill's example `/home/z/my-project` path.
- Plan before mutations; retrospective records actual results after execution. Do not invent pre-execution observations or claim to have completed retrospective before execution.
- Preserve all user requirements; Pareto prioritization defers optional work, never discards required work.
- Skill prose has inconsistent CSR interpretations and rollback thresholds. Keep adaptation disabled pending clarification; record raw evidence and undefined ratios as null. No fabricated convergence percentages.
- Read-only discovery may precede execution planning when necessary to ground the plan.

Use short bounded iterations: focused tests, then a small benchmark when relevant. No heavy installs or long training without demonstrated need. Source records and backend semantics must remain traceable. Measure discovery time separately from execution time. Compare precision and domain before performance. Never promote candidates automatically.

Current commands:
- `python -m unittest discover -s tests -v`
- `python -m spear '{"kind":"discover","formula":"x*x","seed":42}'`
- `node --disable-warning=MODULE_TYPELESS_PACKAGE_JSON benchmark_discovery.mjs`

No literal `/goal` command is installed. GOAL.md is the persistent equivalent for agent planning; do not claim a platform slash command exists.

## Visual Grounded Loop — user preference

Whenever creating or modifying visual output, inspect the actual rendered result: produce → capture → inspect → correct → recheck. For images/designs, inspect the final image; for interfaces, capture relevant viewport sizes and check interactions; for animation, inspect a played sequence or video, not only a still frame. Check against the requested criteria and stop once they are met. If rendering, capture or inspection is unavailable, report visual verification as incomplete; source-code checks are not a substitute. Do not add visual checks to work without visual output. Respect the environment's supported preview and browser paths.
