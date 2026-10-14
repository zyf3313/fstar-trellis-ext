# UI design

Use for user-visible interface design, implementation or review. Skip for work
without a UI change. Preserve the project's established visual language, components,
accessibility and platform conventions. For a new project, confirm the UI direction,
framework and layout before implementation; reuse an existing project's baseline.

## Core and conditional references

`emil-design-eng` is the single core design Skill for both new directions and existing
UI interactions. Load its relevant sections on demand when available; its presence
in this guide is not proof that a client installed or loaded it. Do not route the
same task through another parallel core design Skill. Existing machine installations
are outside this guide's scope.

| Task condition | Additional reference | Evidence to produce |
|---|---|---|
| Real data can stretch, empty or break a view | `break-ui` | Representative empty, long, missing and boundary data states |
| Motion is added, changed or implicated in a defect | `review-animations` | Applicable motion/accessibility review and target-browser checks |
| Phone or touch interaction is targeted | `mobile-native` | Touch/layout review and critical paths on a real target device |

These are conditional checks, not three mandatory stages. Explain applicable and
skipped conditions. Treat duration, scale and similar author heuristics as starting
points, subordinate to the confirmed design and project requirements. Investigate
performance with the current framework/browser guidance and measurements; do not
impose universal property rewrites from a rule of thumb.

## Result and fallback

Show the proposed or implemented states and record what was reviewed, screenshot-tested,
measured and actually used on a device separately. A prototype or emulator does not
complete real-device acceptance; keep that gate pending when no device is available.
If a Skill is missing, use the project's design baseline and existing checks, report
the limitation and avoid automatic installation. Revisit the selected references
when UI scope, platform or upstream guidance changes; on-demand loading does not
prove zero persistent client cost.

Sources: [Emil Skills](https://github.com/emilkowalski/skills#readme),
[core](https://github.com/emilkowalski/skills/blob/main/skills/emil-design-eng/SKILL.md),
[data boundaries](https://github.com/emilkowalski/skills/blob/main/skills/break-ui/SKILL.md),
[motion review](https://github.com/emilkowalski/skills/blob/main/skills/review-animations/SKILL.md),
[mobile](https://github.com/emilkowalski/skills/blob/main/skills/mobile-native/SKILL.md)
and [Motion performance](https://motion.dev/docs/performance).
