# Project State

## Current Status
Architecture refactoring Phases 1–6 + C0 (Channel Selector) complete.
Software DoD: **42/42 tests PASS** ✅

## Active .toe
`_Touchdesigner/SLS_Studio_1.2.17.toe`
(TD auto-backup `SLS_Studio_1.2.toe` is ignored for git purposes)

## Test Coverage

| Phase | Tests | Topic |
|-------|-------|-------|
| Phase 1–6 | T01–T12 | Basic routing: EQ, level, send, pan, master |
| Gummiband | T13a–T13b | Multi-slot interpolation |
| Modifier | T14a–T14b | scene_push modifier state |
| FX Contextual | T15–T19 | Slot-aware fx_grid routing + parity |
| Modifier Super Mode | T20–T23b | Modifier overrides slot context |
| Hold/Temp Selection | T24–T27 | Effective = base ∪ temp, modifier override |
| Broadcast Mode | T28–T32 | Multi-target broadcast routing |
| Hold-Window Logic | T33–T38 | note-on/off + hold window edge cases |
| LED Visual | L01 | LED sequencer visual test |

**Total: 42 test cases** in `test__cases`, run via `test__runner`.

## Architecture Summary

**Maps (static data):**
`maps__bitwig_remote`, `maps__bitwig_send`, `maps__bitwig_paths`, `maps__bitwig_special`, `maps__led_slots`, `maps__selector`

**Logic (processing):**
`logic__control_exec` → `logic__event_normalizer` → `logic__domain_updater` → `logic__control_resolver` → `logic__priority_resolver` → `logic__selection_effective_merge`

**State (live tables):**
`state__resolved_targets_raw`, `state__resolved_targets`, `state__selection_base`, `state__selection_temp`, `state__selection_effective`, `state__current_values`, `state__value_memory`, `state__modifier`

**Outputs:**
`out__bitwig_router`, `out__led_router`, `out__view_router`, `out__debug_router`, `out__vcm600_leds`

**Removed (legacy):**
- `group_level_bridge` — soft_removed (onFrameEnd disabled, still in system_map as legacy_active)
- `Midi_Bitwig_Ch1-6` — removed in Phase-6-Cleanup
- `state__focus`, `in__vcm600` — removed in Phase E

## Pending — Hardware Required (VCM-600 must be connected)
1. Level-Fader bewegen → verify `bitwigTrack.Volume` responds via new router (without `group_level_bridge`)
   → if OK: permanently delete `group_level_bridge` node + mark `removed` in `docs__system_map`
2. Gummiband multi-slot live test → T13 hardware verify
3. Shift/Modifier press → Session-Clear korrekt
4. Fast fader movement → no frame drops, `debug__perf` stable

## After Hardware Tests
- Remove `group_level_bridge` permanently from `.toe`
- Create GitHub PR via web UI (gh CLI not in PATH)

## Last Verified
- Date: 2026-03-28
- TD MCP reachable, `SLS_Studio_1.2.17.toe` active
- 42 test cases confirmed in `test__cases`
- `docs__system_map` and `docs__runbook` current in TD
- Git branch: `main`
