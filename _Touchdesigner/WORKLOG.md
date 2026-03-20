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
- Migrated selector logic into `/project1/channel_selector` and flattened shared context into `/project1/state/global_state`.
- Moved selector toggle truth into `/project1/state/channel_selector_state` and left only mirrored state views inside the feature block.
- Added `channel_selector_active` in `/project1/state/global_state` and gated selector input and LED rendering through it.
- Defined the next channel architecture around `device -> eventbus -> feature -> state -> outputs`.
- Started migrating from selector toggle truth toward hybrid shared `channel_state` with `focused_channel` and explicit `channel_n_enabled` fields.
- Split VCM-600 LED sending into production `vcm600_led_transport` and debug-only `vcm600_led_test_api`.
- Replaced selector toggle truth with shared `/project1/state/channel_state` carrying focused slot, focused track name, and per-channel enabled flags.
- Added `/project1/outputs/bitwig_channel_selection` with explicit `bitwig_track_map` and Bitwig cursor navigation through `bitwigTrack`.
- Replaced frame-end polling in the selector LED and Bitwig outputs with DAT-change-driven execution on `channel_state`.

## 2026-03-17
- Added `/project1/state/group_volume_state` and `/project1/state/group_volume_api` for shared VCM-600 group-volume truth.
- Added `/project1/outputs/bitwig_group_volumes` with `group_volume_map`, debug table, and synced notes.
- Wired VCM-600 channel 1 to 6 `level` topics to the existing `bitwigTrack` component for Bitwig group volume control.
- Set provisional Bitwig group-name defaults to `DRUM`, `BASS`, `LEAD`, `PAD`, `VOCAL`, and `FX`.

## 2026-03-18
- Removed the temporary VCM-600 to Bitwig group-volume experiment from the active project path.
- Reset `vcm600_callbacks` to device-table and eventbus output only.
- Removed `/project1/state/group_volume_*`, `/project1/outputs/bitwig_group_volumes`, and `/project1/bitwig/group_tracks`.
- Moved `vcm600`, `cntrlr`, `midicon`, and `midicraft` out of the old `/project1/devices` base onto `/project1` root.
- Added a root-level `devices_area` annotation so the hardware blocks read as one visible TouchDesigner area.
- Moved mirrored device rules DATs into `/project1/project_docs`.
- Repaired stale device callback and lookup paths after the root-level move, including the broken VCM-600 MIDI input path.
- Stacked the root-level devices vertically and added visible `bus_out` DAT ports on each device plus `/project1/eventbus/bus_out`.
- Moved `channel_selector` out of `/project1/features` to `/project1/channel_selector`.
- Switched `channel_selector` input from the shared eventbus table to `/project1/vcm600/bus_out` for a more direct visible device connection.
- Added `/project1/vcm600/current_bus_event` as a one-row live view of the latest VCM-600 bus event.
- Refined the root layout so `vcm600` exposes one visible docked output port and `channel_selector` one visible docked input port, connected by a single cable.
- Replaced the temporary root DAT helper path with a direct COMP-to-COMP CHOP cable from `/project1/vcm600` to `/project1/channel_selector`.
- Added a normalized VCM-600 CHOP output and moved the selector input bridge inside `/project1/channel_selector/selector_logic`.
- Reduced `/project1/vcm600/current_bus_event` to a compact last-active view so the device block stays readable.
- Documented that MIDI device `11` is reserved for Bitwig MIDI In mapping control.
- Added `/project1/bitwig_midi_map_out` as a root-level output block with a visible CHOP input and internal MIDI send to device `11`.
- Added a visible CHOP output on `/project1/channel_selector` exposing active selector slots as normalized channels.
- Added `/project1/bitwig_midi_router` to assign the first five active selector subtracks onto Bitwig MIDI output slots for device IDs `12..16`.
- Added `/project1/bitwig_midi_out_1` to `/project1/bitwig_midi_out_5` as root-level MIDI output blocks with visible CHOP inputs and internal generic `enc_1..8` / `btn_1..10` to MIDI remapping.
- Reworked the Bitwig MIDI output logic from temporary active-slot assignment to fixed groups `1..6` with devices `11..16`.
- Added `/project1/vcm600_group_router` to expose six generic group control outputs from the normalized VCM-600 CHOP stream.
- Updated the Bitwig group output blocks so each one mirrors its incoming controls onto all active subtracks `.1/.2/.3` of its fixed group.
- Moved `bitwig_midi_router` and `vcm600_group_router` inside `/project1/channel_selector` so the root reads more clearly as `vcm600 -> channel_selector -> bitwig outputs`.

## 2026-03-19
- Restored the crashed TouchDesigner changes so `vcm600`, the root-level `channel_selector`, and the fixed Bitwig group output blocks are live again.
- Rebuilt the visible `vcm600 -> channel_selector -> bitwig_midi_*` CHOP flow and reconnected the internal selector event bridge plus fixed group routers.
- Renamed the six root Bitwig MIDI output blocks to `/project1/Midi_Bitwig_Ch1` through `/project1/Midi_Bitwig_Ch6` and updated the fixed router paths.
- Added six visible root mapper blocks `/project1/Group_1_MIDI_Map` through `/project1/Group_6_MIDI_Map` between `channel_selector` and the Bitwig MIDI outputs.
- Reworked the VCM-600 group sources from generic `enc_*/btn_*` channels to semantic control names and fixed the group MIDI rule to `CC 1..8` plus `Note 1..10` per active `.1/.2/.3` slot.
- Added `/project1/state/channel_value_memory` as the shared 18-slot memory table for all group controls, and switched the group readouts plus MIDI mapping callbacks to read from this central state.
- Kept each `Group_n_MIDI_Map` visually readable by mirroring the central memory back into its local `slot_memory` and `pickup_state` tables.
- Collapsed the six root mapper blocks into one visible `/project1/Group_MIDI_Map` wrapper and moved `Group_1_MIDI_Map` to `Group_6_MIDI_Map` inside it as internal sub-blocks.
- Removed the inner `Group_1_MIDI_Map` to `Group_6_MIDI_Map` blocks as well and replaced them with one lean `Group_MIDI_Map` core using direct `mapped_midi_1..6` script outputs plus the combined `current_values_all` base table.
- Added `/project1/Group_MIDI_Map/hybrid_group_fader` as a reusable internal block with `fader`, `btn1..3` input, `out1..3` output, anchored offset behavior in the middle, and synced travel to `0/1` at the boundaries with epsilon guards.
- Switched all eight encoder controls (`hi_eq` through `frequency`) on outputs `1..6` to a shared elastic hybrid model: single-slot direct follow, multi-slot reversible compression toward `0/1`, and restored spacing when moving back from the edges.

## 2026-03-20
- Restored the crash-lost `hybrid_group_fader`, `hybrid_fader_state`, and the hybrid-aware `event_stream_exec` path under `/project1/Group_MIDI_Map` and `/project1/channel_selector`.
- Recreated `eventbus` plus `eventbus_core` inside `/project1/Midi_Bitwig_Ch1` to `/project1/Midi_Bitwig_Ch6` so each MIDI output block can again show readable outgoing MIDI events.
- Verified `0` reported errors on `/project1`, `/project1/channel_selector`, and `/project1/Group_MIDI_Map` after the restore.
- Re-applied the flattened inner `Group_MIDI_Map` core by removing the temporary inner `Group_1_MIDI_Map` to `Group_6_MIDI_Map` blocks and switching back to direct `mapped_midi_1..6` outputs plus the single `current_values_all` overview.
- Fixed the restored hybrid-slot initialization so active group-2 subslots (`2.1/.2/.3`) no longer leave `send_a`, `resonance`, or `frequency` detached at zero after the crash restore.
- Restored the missing `/local/midi/device` rows for `BITWIG_CH2` to `BITWIG_CH6` (`id 12..16`) so the six Bitwig MIDI output blocks can send to their physical ports again.
- Removed the stale second-stage `enc_*` / `btn_*` remap from `Midi_Bitwig_Ch1` to `Midi_Bitwig_Ch6` again and restored them to pure passthrough transport blocks for the already mapped `Group_MIDI_Map` output.
- Rebound the six `Midi_Bitwig_Ch*` `midi_out` operators from the stale logical IDs `11..16` to the actual restored `/local/midi/device` row positions `3..8`, which map to `BITWIG_CH1..BITWIG_CH6`.
