# SLS Studio — Project Rules

## Purpose
TouchDesigner ↔ Bitwig Studio ↔ VCM-600 controller integration.
Data-driven, single-source-of-truth routing architecture.

## Startup Routine
At the beginning of every new session:
1. Read `AGENTS.md` (this file).
2. Read `PROJECT_STATE.md`.
3. Inspect the live `.toe` via MCP before proposing changes — the `.toe` is the source of truth.
4. Update `PROJECT_STATE.md` when meaningful state changes.

## Source Of Truth
- **`.toe` file** = primary truth for all node structure, logic, and state.
- **`AGENTS.md`** = stable project rules (this file).
- **`PROJECT_STATE.md`** = current working context, test status, open items.
- **Git commits** = change history.

## Project Structure
- `_Touchdesigner/` — all TouchDesigner assets.
- Active `.toe`: `SLS_Studio_1.2.17.toe` (TD auto-backup: `SLS_Studio_1.2.toe`, ignore for git).
- TouchDesigner runtime: `/project1` (flat structure, 126 direct children).

### Node Naming Convention
All nodes in `/project1` follow a prefix convention:

| Prefix | Role | Examples |
|--------|------|---------|
| `logic__` | Processing / computation | `logic__control_resolver`, `logic__event_normalizer` |
| `state__` | Live state tables | `state__resolved_targets`, `state__selection_effective` |
| `maps__` | Static lookup tables | `maps__bitwig_remote`, `maps__led_slots` |
| `out__` | Output routers | `out__bitwig_router`, `out__led_router` |
| `debug__` | Debug visibility | `debug__event`, `debug__perf` |
| `docs__` | In-TD documentation | `docs__system_map`, `docs__runbook` |
| `ops__` | Operations / health | `ops__health`, `ops__feature_flags` |
| `test__` | Test infrastructure | `test__cases`, `test__runner`, `test__results` |
| `exec__` | DAT executors | `exec__selection_effective_refresh` |
| `run__` | Manual triggers | `run__tests` |

### Device Containers (baseCOMP)
- `vcm600` — VCM-600 MIDI device (input + LED output)
- `cntrlr` — CNTRLR device
- `midicon` — Midicon device
- `midicraft` — Midicraft device
- `vcm600_ui` — VCM-600 on-screen UI
- `logic__channel_selector` — Channel/slot selection state machine
- `logic__gummiband` — Gummiband multi-slot logic
- `out__vcm600_leds` — VCM-600 LED MIDI output

### Bitwig Nodes
- `bitwigMain` — main Bitwig connection
- `bitwigTrack1–6`, `bitwigTrackMaster` — 7 track nodes
- `bitwigClipSlot{1-6}_{1-3}` — 18 clip slot nodes (6 tracks × 3 scenes)
- `bitwigRemotesTrack1–6` + sub-tracks — remote control nodes

## Pipeline (Data Flow)
```
VCM-600 MIDI
  → logic__control_exec          (pipeline entry)
  → logic__event_normalizer      (topic+value → event{})
  → logic__domain_updater        (state writes + gummiband)
  → logic__control_resolver      (event → raw targets)
  → state__resolved_targets_raw
  → logic__priority_resolver     (dedup + priority)
  → state__resolved_targets
  → out__bitwig_router           (writes Bitwig parameters)
  → out__led_router              (sends LED MIDI to VCM-600)
  → out__view_router             (updates selection readout)
  → out__debug_router            (writes debug__action_log)
```

### Selection State (C0.4)
```
state__selection_base  (stable base)  ┐
state__selection_temp  (hold/loop)    ├→ logic__selection_effective_merge
state__modifier        (modifier)     ┘        → state__selection_effective
```
`state__selection_effective` is the single source of truth for active slot selection.

## Working Rules
- Always read the relevant nodes via MCP before proposing changes.
- Do not invent node names — verify they exist in the `.toe`.
- Prefer incremental changes over broad refactors.
- Run `test__runner` after any logic change and verify `test__results`.
- Keep `PROJECT_STATE.md` current when test count or architecture changes.
- `docs__system_map` inside TD is the authoritative node registry — update it when nodes are added/removed.

## Recovery Commands (in TD Python console)
```python
op('/project1/ops__recovery').module.check_health()
op('/project1/ops__recovery').module.rebuild_map_cache()
op('/project1/ops__recovery').module.full_restart()
op('/project1/test__runner').module.run_all()
```
