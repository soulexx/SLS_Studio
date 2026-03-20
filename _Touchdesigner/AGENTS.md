# SLS Studio Project Rules

## Purpose
- This project contains the TouchDesigner setup and support files for SLS Studio.
- Stable project rules live here.

## Startup Routine
At the beginning of a new chat in this project:

1. Read `AGENTS.md`.
2. Read `PROJECT_STATE.md`.
3. Inspect the relevant project area before changing logic.
4. Update documentation when the verified project state changes.

## Source Of Truth
- Stable rules: `AGENTS.md`
- Current working context: `PROJECT_STATE.md`
- Brief change history: `WORKLOG.md`

## Current Root Structure
TouchDesigner runtime centers around `/project1` with these main areas:

- `/project1/project_docs`
- `/project1/bitwig`
- `/project1/vcm600`
- `/project1/cntrlr`
- `/project1/midicon`
- `/project1/midicraft`
- `/project1/eventbus`
- `/project1/state`
- `/project1/modes`
- `/project1/features`
- `/project1/intent`

Active devices now live directly on `/project1` and should stay grouped as one visible network area.

## Device Rules
- Device-specific mapping conventions live in `devices/DEVICE_RULES.md`.
- Device notes should stay close to the device they describe.
- Devices prepare normalized events for the eventbus.
- Device COMPs live on `/project1` root, not inside a separate `devices` base.
- If a device or feature should read as one visible root block, prefer a CHOP-level input/output on the COMP and keep DAT/Python processing inside the block.

## Working Rules
- Keep documentation concise and current.
- Prefer incremental edits over broad refactors.
- Before modifying TouchDesigner logic, inspect the relevant COMP/DAT structure first.
- Use logical layout and grouping in the TouchDesigner network.
- Avoid hiding device-specific mapping corrections in callback hacks when tables can hold the verified values directly.

## Documentation Rules
- `PROJECT_STATE.md` should stay short and operational.
- `WORKLOG.md` should contain brief dated notes.
- Documentation files that matter in daily work should be mirrored in TouchDesigner as synced `textDAT`s.
- Mirrored docs should appear in a logical project area, not scattered randomly.

## TouchDesigner Layout
- Prefer this order inside a logical area when possible:
  - Rules
  - I/O
  - Verarbeitung
  - Bus
  - Debug
  - Tests
- Keep root-level layout readable and spatially grouped by function.
- When devices are shown on root, keep them inside one visible annotation area so the hardware side reads like one connected playground.

## Current Interaction Architecture
- `devices` handles hardware I/O, mapping, and local LED tests.
- `eventbus` collects normalized shared events.
- `state` holds shared semantic truth such as active mode, page, target, and reusable selections.
- `modes` defines how features behave or are bound in different situations.
- `features` contains visible functional building blocks that read events and mutate or consume shared truth.
- `outputs` contains downstream consumers that read shared truth and drive external targets.
- `intent` should turn event plus context into user intent.
- `debug` holds testing and visibility tools.
- Prefer visible root-level main flow as `device -> feature -> state/output` through CHOP connections when the relationship should read like a TouchDesigner patch.
- Keep DAT tables, event logs, and Python-driven translation inside the block unless they are part of the root-level story.

## State Rule
- Use `eventbus` for transient events.
- Use `state` for current truth.
- If a feature-owned value is read by other blocks, move that value into `state` and mirror it locally only for visibility.

## LED Architecture Rule
- LED output should be state-driven, not event-driven.
- Preferred flow:
  - `input event -> context/state mutation -> desired_led_state -> midi transport`
- Adapters should separate:
  - state input
  - semantic LED image derivation
  - diff/full render
  - transport output

## Default Assistant Behavior
- Be concise and practical.
- Explain assumptions when they matter.
- If project conventions change, update documentation too.
