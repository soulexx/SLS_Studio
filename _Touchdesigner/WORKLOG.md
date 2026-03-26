# Worklog

## 2026-03-22
- Reconnected `/project1/Instrument_Control_Core/fx_grid_router/out1` to `fx_grid_out` so the internal deep path again forwards live `fx_grid 1..8` values into `fx_subbank_map`, `deep_bus`, slot memory, and the `current_values_all` overview without requiring selector re-toggle.
- Restored the root tdBitwig track template `/project1/bitwigTrack` into a visible root row `/project1/bitwigTrack1 .. /project1/bitwigTrack6` and set those six track cursors to `live ch 1 .. 6`.
- Marked `/project1/bitwigRemotesTrack1_1 .. /project1/bitwigRemotesTrack6_3` as fixed target slots with visible comments and a `project_docs/bitwig_remote_target_rules` note so the layer is no longer treated as a reliable dynamic track-retarget system.

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
- Removed the unused root `_tmp_*` scratch files that were left over from the earlier Bitwig and VCM-600 experiments.
- Reconnected `/project1/Midi_Bitwig_Ch1/midi_out` from the temporary `direct_test` source back to `mapped_midi`.
- Switched the six `Midi_Bitwig_Ch*` `midi_out` operators back to device IDs `11..16` after confirming the current Bome network resolves those ports directly again.
- Verified that the current receive failure was caused by a `Bitwig MIDI Out -> Bitwig MIDI In` loop in the external Bome routing, not by the internal `vcm600 -> channel_selector -> Group_MIDI_Map -> Midi_Bitwig_Ch*` path.

## 2026-03-21
- Extended the new root `/project1/gummiband_master` to the deep path: `/project1/Instrument_Control_Core/deep_write_callbacks` now runs `fx_grid_1 .. fx_grid_8` through a new `fx_grid_hybrid_state` table so active deep targets receive elastic per-slot values instead of an identical deep fan-out.
- Added `/project1/gummiband_master` on root and extracted the elastic multi-slot movement formula into `gummiband_core`; `channel_selector/event_stream_exec` now calls that reusable algorithm instead of carrying the full motion curve inline.
- Added `/project1/Instrument_Control_Core/fx_grid_memory` and wired it into the centralized deep path so per-slot `fx_grid_1 .. fx_grid_8` values are persisted for `1.1 .. 6.3` instead of disappearing on selector deactivation.
- Updated `/project1/channel_selector/event_stream_exec` to snapshot the current `fx_grid` state before a selector button turns an active slot off, and updated `Instrument_Control_Core/deep_write_callbacks` plus `current_values_all_core` so inactive slots now show the last stored `fx_grid` values.
- Added `/project1/project_docs/vcm600_notes` and `/project1/project_docs/cntrlr_notes` as synced mirrors of the device note files so the active hardware docs are centralized with the rest of the project docs.
- Added `/project1/project_docs/bitwig_rules` as the synced mirror of `bitwig/BITWIG_RULES.md` and removed unreferenced callback duplicates from `/project1/Group_MIDI_Map` (`mapped_midi_*_callbacks1` plus the unused `hybrid_out_callbacks` DAT).
- Moved `channel_selector_state` into `/project1/channel_selector` and `channel_value_memory` into `/project1/Group_MIDI_Map`, then removed the remaining obsolete root `/project1/state` block after confirming no live references remained.
- Reduced the active `/project1` root to the current live runtime blocks and centralized docs by removing the obsolete root `modes`, `intent`, `features`, `outputs`, old duplicated root doc DATs, and the old root `eventbus`.
- Removed the remaining root `eventbus` write path from `vcm600_callbacks` and `cntrlr_callbacks`; device-local debug/event tables remain inside the device blocks.
- Moved the synced `DEVICE_RULES.md` and `MAPPING_RULES.md` mirrors into `/project1/project_docs` as `device_rules` and `mapping_rules`, and removed the obsolete documentation-only `/project1/devices` base.
- Verified that `/local/midi/device` had regressed again so only row `11` still pointed to a real Bome output while rows `12..16` had empty `outdevice` fields.
- Restored `/local/midi/device` rows `12..16` to `BMT 2..6`, so `Midi_Bitwig_Ch2` to `Midi_Bitwig_Ch6` resolve physical outputs again like `Midi_Bitwig_Ch1`.
- Changed the selector-toggle path so activating `track_x.y` no longer forces a full `Group_MIDI_Map` MIDI resend; slot activation is now arm/routing-only and waits for real control movement plus the existing pickup/gummiband logic before sending.
- Changed `Group_MIDI_Map/mapped_midi_1..6` from selector-dependent channel creation to fixed `ch1..ch3` transport outputs so slot toggles no longer create/remove MIDI channels and therefore no longer emit activation-time snapshots.
- Restored the hybrid encoder motion to an anchor-based elastic model: the live hardware value defines the segment start, `base_1..3` preserve slot spacing, and compression toward `0` or `1` only starts when the raw movement would cross the boundary.
- Fixed hybrid re-anchoring so active slots rebuild from `channel_value_memory` instead of being normalized to the current live encoder value; only truly detached zero-state slots now bootstrap from live on activation.
- Changed the hybrid multi-slot edge behavior again so no active slot reaches `0` or `1` before the physical VCM-600 control does; the remaining travel to the edge now uses a shaped slowdown across all active slots.
- Restored the VCM-600 LED transport semantics to the live-confirmed map rule `Note On 127 / Note On 0`, fixed the stale `vcm600_all_leds_on/off` DAT paths that still pointed to the removed `/project1/devices/...` base, and cleared stale `selectDAT` expr leftovers in `channel_selector`.
- Fixed the actual VCM-600 LED transport binding by switching `/project1/vcm600/vcm600_midi_out` to `onebased = true`; the previous `false` setting left the hardware dark even though selector LED renders and send logs still looked correct.
- Added a direct LED refresh call to the selector-toggle success path in `/project1/channel_selector/event_stream_exec` so VCM-600 selector LEDs update immediately on each toggle instead of depending only on the `frameend` render callback.
- Optimized that selector LED refresh path again to use the existing `render_core` module directly and diff-render only the changed LED state instead of forcing a full re-send on every toggle.
- Removed the last dead `/project1/state/group_volume_*` and `/project1/outputs/bitwig_group_volumes/*` callback remnants from `/project1/vcm600/vcm600_callbacks` and aligned the docs with the current root-only runtime structure.
- Added the first visible deep-mapping prototype on root as `focus_router -> fx_subbank_map -> Midi_Bitwig_Ch1`: group-1 focus is now derived from the last touched encoder family, and `fx_grid` is remapped to focus-dependent extra CC banks `21..84` when selector slot `1.1` is active.
- Corrected the prototype focus source again so `focus_router` now reads the semantic Group-1 control stream from `/project1/channel_selector/vcm600_group_router/group_1_source` instead of trying to infer focus from the already mapped `Group_MIDI_Map/out1` output.
- Finished that cleanup by routing `focus_router` visibly from `/project1/channel_selector/out1`; the focus callback now reads only its own local `in1` again, so the root path is visible and the hidden direct source reference is gone.
- Replaced the deep-mapping MIDI prototype transport with a visible tdBitwig path: `/project1/fx_subbank_map` now outputs semantic `deep_1..8`, `/project1/tdbitwig_deep_router` now sits on root, and the active deep path is `vcm600 -> channel_selector -> focus_router -> fx_subbank_map -> tdbitwig_deep_router -> bitwig`.
- Wired `/project1/vcm600` visibly into `/project1/fx_subbank_map`, rewired `/project1/fx_subbank_map` visibly into `/project1/tdbitwig_deep_router`, and added `/project1/bitwig/in1` so the tdBitwig deep path is readable on root end-to-end.
- Pointed the first tdBitwig deep target at `/project1/bitwig/DEMO1/project1/projectRemotesMacros1`; direct writes to `Remotecontrol0..7` are live, while remote page switching remains prepared but not yet verified because that target currently reports no populated page names.
- Added a dedicated visible `/project1/fx_grid_router` root block between `vcm600` and `fx_subbank_map` so the VCM-600 `fx_grid` fader values are readable at a glance via base viewer plus `grid_to_dat`, instead of being pulled invisibly straight out of the device stream.
- Added a first minimal live tdBitwig core directly on root as `/project1/bitwigMain` plus `/project1/bitwigRemotesTrack`, confirmed `bitwigMain/out1 -> connected = 1`, and repointed `/project1/tdbitwig_deep_router` from the dead old demo target to the live `/project1/bitwigRemotesTrack`.
- Verified that the deep path now writes current `fx_grid` values into `/project1/bitwigRemotesTrack` `Remotecontrol0..7` while selector slot `1.1` is active.
- Reorganized the visible tdBitwig target area into grouped containers `CH_1_Instruments` through `CH_6_Instruments`; each container now holds the three matching `bitwigRemotesTrackx_1 .. x_3` targets configured to tracks `x.1 .. x.3`.
- Added grouped `CH_1_Deep` through `CH_6_Deep` blocks between each `Midi_Bitwig_Ch*` and `CH_*_Instruments` and upgraded them to live summary views: each block now shows slot activity plus current per-group deep-relevant values from `channel_selector/out1..out6`; only `CH_1_Deep` currently carries the true tracked focus label.
- Replaced the six separate `CH_x_Deep` implementations with one shared master clone `/project1/channel_deep_summary_master` and parameterized clone instances `CH_1_Deep .. CH_6_Deep` using `Group=1..6`.
- Generalized the deep focus path from the old `CH_1` prototype to all six channels: `/project1/focus_router` now tracks both `focus_control` and `focus_group` across `channel_selector/out1..out6`, and `/project1/fx_subbank_map` now gates by the focused group plus its active slots instead of the hard-coded `track_1_1`.
- Turned `CH_1_Deep .. CH_6_Deep` from pure summary clones into the actual grouped tdBitwig deep writers: the focused channel now writes `deep_1..8` to all active `bitwigRemotesTrackx_1..x_3` targets in its matching `CH_x_Instruments` container.
- Enabled page-aware deep writes in the grouped `CH_x_Deep` writer path: the current focus page index now switches the active `bitwigRemotesTrackx_y` targets to the matching remote page first, clamping automatically where a track exposes fewer pages than the requested focus bank.
- Removed the obsolete single-slot prototype nodes `/project1/deep_target_1` and `/project1/deep_target_1_bus` after the per-channel `CH_x_Deep` writer path took over.
- Recorded a possible later structure refactor: consolidate each channel row into larger `CH_1 .. CH_6` blocks and leave only the truly global selector/routing logic in a smaller shared core.
- Recorded a second later improvement: migrate repeated per-channel logic toward one parameterized reusable block instead of keeping six separate channel-specific copies.
- Renamed `/project1/Group_MIDI_Map` live to `/project1/Instrument_Control_Core` and updated all verified callback/path references to the new core path without introducing TD errors.
- Verified that the grouped `bitwigRemotesTrackx_y` tdBitwig target layer is not a reliable fixed-slot addressing model: changing the visible `Track` parameter does not reliably retarget the underlying pinned Bitwig cursor, so the current grouped deep fan-out remains experimental pending a new target strategy.
- Moved the active deep bus into `/project1/Instrument_Control_Core` by adding root-fed `in7`, centralized `deep_bus`, and `deep_state`; the old root `tdbitwig_deep_router` has been removed and the per-channel `CH_x_Deep` writers now read the central core bus instead.
- Extended `/project1/Instrument_Control_Core/current_values_all` so the base viewer now shows the live deep summary (`focus_group`, `focus_control`, `page_index`, `active_slots`, `deep_1..8`) above the per-group slot table.
- Renamed the raw eight deep-fader rows in `/project1/Instrument_Control_Core/current_values_all` to `fx_grid_1 .. fx_grid_8` and changed them to read directly from the raw internal `fx_grid` source instead of the gated deep bus.
- Removed the loose root helper blocks `fx_grid_router`, `fx_grid_router1`, and `fx_subbank_map` after copying and rewiring them inside `/project1/Instrument_Control_Core` as internal helper blocks.
- Added a central `/project1/Instrument_Control_Core/deep_write_callbacks` + `deep_write_state` path so the core now writes the focused group's deep values directly to the active root `bitwigRemotesTrack{group}_{slot}` targets.

## Session 2026-03-27 — Bitwig-Routing, Selection-Fix, Performance, Doku

### Multi-Channel Fader Jitter (Root Fix)
- `vcm600_callbacks.onReceiveMIDI`: CC-Events rufen `write_exec.refresh()` direkt auf (kein `_set_current_bus_event`) — eliminiert inDAT-Latenz für parallele Faderbewegungen
- Note-Events gehen weiterhin auf `_set_current_bus_event` für den Bus + direkt auf `event_in_exec.process()`

### CH_N Spalten in ICC-Tabelle
- `current_values_all_core`: HEADER erweitert um `CH_1..CH_6` (je nach Gruppe: live-Wert wenn kein Slot aktiv, sonst unverändert)
- `write_exec._write_direct()`: schreibt CH_N bei no-slot-Pfad mit live-Wert, bei Slot-Pfaden kein Überschreiben (kein Sprung auf 0)

### Bitwig Remote Controls Routing
- `_write_bitwig_remotes()` in write_exec: eq_hi/mid/low, pan, send_a/b, resonance, frequency → bitwigRemotesTrack{N}.Remotecontrol0..7
- Kein Slot: CH_N → bitwigRemotesTrackN / Slot aktiv: N.s → bitwigRemotesTrackN_s
- Kein CH_N=0 mehr beim Slot-Aktivieren (verhindert Sprünge in Bitwig)

### FX Sends Routing  
- fx_grid_1..8 → bitwigTrack{focus_ch}.Send0..7
- Bedingung: focus_ch gesetzt UND kein Slot aktiv für focus_ch
- Check: selector_in wird inline in _write_bitwig_remotes gelesen

### Focus Tracking / Make Visible
- `_update_focus(group)` in write_exec: schreibt focus_ch in focus_state, pulst bitwigTrackN.Makevisibleinmixer nur bei echtem Kanalwechsel
- Level-Fader triggert _update_focus(group) für ch1-6
- master_level triggert _update_focus('master') → bitwigTrackMaster

### Master Volume
- vcm600/global/master_level → bitwigTrackMaster.par.Volume (immer, in _write_bitwig_remotes)

### VCM600 Map Fix
- scene_push idx 86→87, foot_switch idx 87→88 (Kollision behoben)

### Channel Selector State Machine (Neuaufbau)
- selection_core: Normal-Mode (live replace on first press, live add during anchor hold, release ends session only)
- Shift-Mode (live toggle auf bestehender Auswahl)
- event_in_exec ruft selection_core.module.handle_event() direkt auf (kein inDAT single-event loss)
- scene_push press/release clearst immer Session (verhindert orphaned sessions)
- Neue DATs: modifier_state, selection_session, session_members

### Numerische Konsistenz
- _norm() / _fmt() überall: canonical '{:.3f}' Format
- one-time migration value_memory

### Performance
- memory_in_sync: onTableChange nur bei Strukturänderung (numRows/numCols), kein O(n) rebuild auf CC-Events
- _write_direct(): O(1) via _control_row_cache + _target_col_cache

### Dokumentation
- system_map tableDAT: alle 20 Features mit trigger/logic/output/condition
- system_docs textDAT: vollständige Architektur-Doku
