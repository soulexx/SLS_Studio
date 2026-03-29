# SLS Studio — Project Rules

Last Updated: 2026-03-29
Worked On: 2026-03-29

## Purpose
TouchDesigner ↔ Bitwig Studio ↔ VCM-600 controller integration.
Data-driven, single-source-of-truth routing architecture.

## Startup Routine
At the beginning of every new session:
1. Read `/project1/docs_AGENTS_md`.
2. Read `/project1/docs_PROJECT_STATE_md`.
3. Inspect the live `.toe` via MCP before proposing changes — the live `.toe` is the source of truth.
4. Verify relevant nodes in `/project1` before proposing or implementing changes.
5. Update `/project1/docs_PROJECT_STATE_md` when meaningful state, tests, architecture, or open work changes.
6. Update the `Last Updated` / `Worked On` date in every touched project doc DAT.

## Critical Documentation Rule
- There are no canonical project documentation files outside the TouchDesigner project for this workflow.
- Project rules and working state live inside the live `.toe` as root textDATs.
- `/project1/docs_AGENTS_md` is the canonical AGENTS document.
- `/project1/docs_PROJECT_STATE_md` is the canonical PROJECT_STATE document.
- Read and update project docs through MCP against the live `.toe`, not via filesystem assumptions.
- If a filesystem file with the same name appears later, the live TD root textDAT still wins unless explicitly migrated.

## Source Of Truth
- **Live `.toe` / `/project1`** = primary truth for node structure, logic, live state, and project docs.
- **`/project1/docs_AGENTS_md`** = stable project rules.
- **`/project1/docs_PROJECT_STATE_md`** = current working context, test status, and open items.
- **`docs__system_map`** = authoritative in-TD node registry, but must be kept current.
- **Git commits** = change history.

## Project Structure
- `_Touchdesigner/` — all TouchDesigner assets.
- Active `.toe`: `SLS_Studio_1.2.17.toe`.
- TD auto-backup: `SLS_Studio_1.2.toe`.
- TouchDesigner runtime: `/project1`.
- `/project1` currently has 132 direct children (verified 2026-03-29).
- Project docs live in root textDATs, not external markdown files.

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

### Device Containers (verified)
- `vcm600`
- `cntrlr`
- `midicon`
- `midicraft`
- `vcm600_ui`
- `logic__channel_selector`
- `logic__gummiband`
- `out__vcm600_leds`
- `out__cntrlr_leds`

### Bitwig Nodes (verified)
- `bitwigMain`
- `bitwigTrack1`–`bitwigTrack6`, `bitwigTrackMaster`
- `bitwigClipSlot{1-6}_{1-3}` — 18 live clip slot nodes
- `bitwigRemotesTrack1`–`bitwigRemotesTrack6`
- `bitwigRemotesTrack{1-6}_{1-3}` sub-track nodes

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
  → out__led_router              (sends LED MIDI)
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

### Focus State
`state__focus` (tableDAT, field/value, row `focus_ch`) determines which channel global controls route to.
Written by `logic__domain_updater` on level events. Read by `logic__event_normalizer._group_from_topic()`.

## Working Rules
- Always read relevant nodes via MCP before proposing changes.
- Always read and update project docs via MCP on the live `.toe`.
- Do not invent node names — verify they exist in the `.toe`.
- Prefer incremental changes over broad refactors.
- Run `test__runner` after any logic change and verify `test__results`.
- Always add tests for new logic and automatically maintain them as part of the same change.
- Remove or update tests immediately when they are obsolete, replaced, or no longer match the live architecture.
- A feature/change is not complete unless the required tests are added or the stale tests are cleaned up in the same pass.
- Keep `/project1/docs_PROJECT_STATE_md` current when test count, architecture, or active work changes.
- Update `Last Updated` / `Worked On` whenever `/project1/docs_AGENTS_md` or `/project1/docs_PROJECT_STATE_md` is edited.
- Update `docs__system_map` when nodes are added or removed.
- If `docs__system_map` disagrees with the live node graph, treat the live node graph as truth and repair the map.

## Recovery Commands (in TD Python console)
```python
op('/project1/ops__recovery').module.check_health()
op('/project1/ops__recovery').module.rebuild_map_cache()
op('/project1/ops__recovery').module.full_restart()
op('/project1/test__runner').module.run_all()
```
