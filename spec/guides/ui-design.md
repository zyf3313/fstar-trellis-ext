# UI design

Use for a new user-visible interface, a changed interaction or visual system, UI implementation, or UI review. Skip when behavior and presentation have no UI impact. Preserve the project's established visual language, components, accessibility and platform conventions.

## Baseline and feature route

For a new project, or one without an adequate UI baseline, read [the Chinese UI baseline template](../templates/ui-baseline.zh-CN.md). Define and present the design language, tokens, components, application frame, navigation, layout, responsive/device boundaries, critical paths and global states before implementation. Record the actual user confirmation and version.

For an existing project, discover and cite its confirmed baseline. Do not redesign the whole product for a feature task. Read [the Chinese feature-interaction template](../templates/ui-feature.zh-CN.md) and design only the affected module/function: roles and entry, pages and stable IDs, normal/empty/loading/permission/error states, validation, cancellation and duplicate actions, recovery and feedback, navigation/return behavior, keyboard/focus/touch behavior, long content and applicable screen sizes. Clarify the interaction before implementation and reuse prior confirmation within its recorded scope.

## Core and conditional references

`emil-design-eng` is the single core design Skill for new directions and existing interactions. Load relevant sections when available; a mention in this guide does not prove installation or client loading. Do not route the same task through a competing core design Skill.

| Task condition | Additional reference | Evidence to produce |
|---|---|---|
| Real data can stretch, empty or break a view | `break-ui` | Representative empty, long, missing and boundary data states |
| Motion is added, changed or implicated in a defect | `review-animations` | Applicable motion/accessibility review and target-browser checks |
| Phone or touch interaction is targeted | `mobile-native` | Touch/layout review and critical paths on a real target device |

These are conditional specialist checks. Explain applicable and skipped conditions. Project baselines and measured behavior take precedence over generic duration, scale or performance heuristics. If a Skill is unavailable, use the project baseline and existing checks, report the limitation and do not install it automatically.

## Conditional delivery contract

When the user requests design deliverables, local review or an implementation reference, define the required subset and provide:

- an editable authoritative design source with source/tool/schema version and regeneration method;
- an index from menu/module → function → page/state/viewport, using stable IDs that map to PRD/TDD, implementation and acceptance;
- viewable previews for every in-scope board/state, organized so the user can inspect one module or function without guessing filenames;
- a runnable prototype for required click/input paths using real DOM or target-platform components where behavior matters, with startup/build commands, sample data and simulation boundaries;
- implementation mapping for tokens, components, routes, events and state ownership, plus the intended target stack and affected code boundary;
- explicit coverage of validation, loading/empty/permission/failure states, recovery, focus, touch/keyboard, responsive or device-specific behavior;
- separate evidence for source/file integrity, local preview, browser/device behavior and user visual acceptance.

A static image or hotspot prototype can explain an early flow but does not prove input, focus, responsive or application behavior. Do not claim a standalone runnable project unless its dependencies, entry point and commands are present and verified.

If the user requests Figma or MasterGo delivery, provide a real format that the target can import, its editable source, import instructions and known losses or substitutions. The user performs the platform import. Do not upload on the user's behalf, rename custom JSON as a native design file, or claim universal lossless compatibility. Record file-structure/read-back checks, actual platform import feedback and user acceptance separately; keep platform acceptance pending until observed.

## Consistency and acceptance

The authoritative source, generated boards, local preview, platform exchange file and implementation must carry the same baseline version and stable IDs. Regenerate only affected outputs after a change. If a platform or generated artifact is edited locally, compare it with the source and choose an explicit merge/synchronization direction before overwriting anything. Apply [document consistency](document-consistency.md) and use the [change review template](../templates/review-change.zh-CN.md) when the change invalidates prior design or evidence.

Show proposed or implemented states and record what was reviewed, screenshot-tested, measured and actually used on a target browser/device separately. A prototype or emulator does not complete real-device acceptance. Small fixes can cite an unchanged confirmed baseline and update the affected interaction only.

Sources: [Emil Skills](https://github.com/emilkowalski/skills#readme), [core](https://github.com/emilkowalski/skills/blob/main/skills/emil-design-eng/SKILL.md), [data boundaries](https://github.com/emilkowalski/skills/blob/main/skills/break-ui/SKILL.md), [motion review](https://github.com/emilkowalski/skills/blob/main/skills/review-animations/SKILL.md), [mobile](https://github.com/emilkowalski/skills/blob/main/skills/mobile-native/SKILL.md) and [Motion performance](https://motion.dev/docs/performance).
