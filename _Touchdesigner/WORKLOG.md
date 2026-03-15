# Worklog

## 2026-03-15
- Organized `/project1` into `devices`, `eventbus`, `context`, `intent`, `adapters`, and `debug`.
- Rebuilt shared eventbus and reconnected `vcm600` and `cntrlr`.
- Verified VCM-600 LED test workflow and corrected live mapping values in tables.
- Verified CNTRLR LED color values on direct hardware channel 1.
- Added initial project state and context documentation files.
- Added first `/project1/context` state table, API, debug view, and synced notes.
- Reorganized `context` toward modular blocks with `context_store` and `channel_selector`.
- Documented the planned state-driven LED adapter architecture.
- Built `/project1/adapters/vcm600_channel_selector_leds` as the first state-driven LED adapter block.
- Added filesystem documentation for the new `state`, `modes`, and `features` root areas.
- Migrated selector logic into `/project1/features/channel_selector` and flattened shared context into `/project1/state/global_state`.
- Moved selector toggle truth into `/project1/state/channel_selector_state` and left only mirrored state views inside the feature block.
- Added `channel_selector_active` in `/project1/state/global_state` and gated selector input and LED rendering through it.
- Defined the next channel architecture around `device -> eventbus -> feature -> state -> outputs`.
- Started migrating from selector toggle truth toward hybrid shared `channel_state` with `focused_channel` and explicit `channel_n_enabled` fields.
- Split VCM-600 LED sending into production `vcm600_led_transport` and debug-only `vcm600_led_test_api`.
- Extended `channel_state` with explicit `focused_track_slot` and `focused_track_linear_index`.
- Added a Bitwig output consumer that follows the last selected `track_1.1` to `track_6.3` slot.
- Replaced frame-end polling in the LED and Bitwig outputs with DAT-change-driven execution on `channel_state`.
