# Project State

## Current Focus
- Keep the plain VCM-600 input path stable after removing the temporary Bitwig group-volume control layer.
- Keep the older channel-selection notes separate from the currently verified live setup.
- Reshape the root network toward a more TouchDesigner-native CHOP patch layout.

## Verified Status
- `vcm600`, `cntrlr`, `midicon`, and `midicraft` now live directly on `/project1` root inside a shared visible device area.
- The root-level device area is now stacked vertically for a clearer `device -> eventbus` reading direction.
- `vcm600` and `cntrlr` are active and mapped.
- Both devices write normalized events into `/project1/eventbus`.
- Each device exposes a visible local `bus_out` DAT, and `/project1/eventbus` exposes its own `bus_out` for downstream consumers.
- `/project1/vcm600` now exposes one normalized root-level CHOP output, and `/project1/channel_selector` exposes one root-level CHOP input.
- Root now shows the `vcm600 -> channel_selector` relationship as one direct cable between the two COMPs without the temporary root DAT helper nodes.
- `/project1/channel_selector/selector_logic/event_in` is now a local event table fed by an internal CHOP bridge instead of a root DAT select.
- `/project1/channel_selector` now keeps the active selector slots as an internal normalized CHOP that feeds its internal Bitwig router.
- `channel_selector` currently uses 18 independent toggles: each mapped `cf_asn`, `clip`, or `track` button toggles exactly one `track_x.y` slot without per-group exclusivity.
- The routing helpers `bitwig_midi_router` and `vcm600_group_router` now live inside `/project1/channel_selector` instead of as separate root blocks.
- `/project1/vcm600/current_bus_event` now shows only the latest active VCM-600 input in compact form (`topic`, `val`, `label`) inside the device block.
- VCM-600 LED tests work from the device area.
- CNTRLR LED tests work on direct hardware channel 1, including color values and test animations.
- `/project1/state/global_state` holds shared semantic state.
- `/project1/state/global_state` holds feature enable flags.
- Bitwig is reachable again on `127.0.0.1:8088` and TouchDesigner is listening on `9099`.
- MIDI device `11` is currently connected to Bitwig MIDI In and is used for Bitwig control through MIDI mapping.
- `/local/midi/device` again contains the fixed Bitwig output entries `11..16` as `BITWIG_CH1..BITWIG_CH6`, so the six `Midi_Bitwig_Ch*` output blocks can resolve their physical MIDI ports again.
- The six `Midi_Bitwig_Ch*` `midi_out` operators are currently bound directly to MIDI device IDs `11..16`.
- `/project1/Midi_Bitwig_Ch1` now acts as the fixed group-1 Bitwig MIDI output block and targets MIDI device `11`.
- `/project1/channel_selector/bitwig_midi_router` now reads the internal selector CHOP output and keeps fixed per-group activation for groups `1..6`.
- The current fixed group mapping is:
  - group `1 -> device 11`
  - group `2 -> device 12`
  - group `3 -> device 13`
  - group `4 -> device 14`
  - group `5 -> device 15`
  - group `6 -> device 16`
- Within each group:
  - `track_x.1 -> MIDI Channel 1`
  - `track_x.2 -> MIDI Channel 2`
  - `track_x.3 -> MIDI Channel 3`
- `/project1/channel_selector/vcm600_group_router` now reads the incoming VCM-600 CHOP stream and exposes six fixed group outputs with semantic channels `hi_eq`, `mid_eq`, `low_eq`, `pan`, `send_a`, `send_b`, `resonance`, `frequency`, `hi`, `mid`, `low`, `mute`, `solo`, `cf_asn`, `clip`, `track`, `stop`, and `play`.
- `/project1/Midi_Bitwig_Ch2` to `/project1/Midi_Bitwig_Ch6` now act as fixed group output blocks for groups `2..6` and target device IDs `12..16`.
- Each Bitwig group output mirrors its incoming generic controls onto all currently active subtracks of that group.
- Root now shows the visible mapping flow as `channel_selector -> Group_MIDI_Map -> Midi_Bitwig_Ch1 .. Midi_Bitwig_Ch6`.
- `/project1/Group_MIDI_Map` is now a single lean mapper block with direct `in1..in6`, `out1..out6`, six script-driven MIDI outputs, and one combined base table view.
- The former inner `Group_1_MIDI_Map` to `Group_6_MIDI_Map` blocks have been removed.
- The fixed transport rule inside `Group_MIDI_Map` is:
  - `hi_eq..frequency -> CC 1..8`
  - `hi..play -> Note 1..10`
  - active `.1/.2/.3` selector slots map to MIDI channels `1/2/3` on the fixed Bitwig output of that group.
- `/project1/state/channel_value_memory` now holds the shared long-form memory for all `18` selector slots, including per-control stored value plus pickup state.
- `/project1/Group_MIDI_Map/current_values_all` is now the single visible readout for all slots `1.1 .. 6.3`.
- `/project1/Group_MIDI_Map/hybrid_group_fader` now exists as a reusable internal block for relative multi-slot fader movement with synced travel to `0` or `1` at the limits.
- `/project1/Group_MIDI_Map/hybrid_fader_state` is restored and currently holds the shared hybrid-fader anchors for all `6 x 8` encoder lanes.
- The eight encoder-style controls `hi_eq`, `mid_eq`, `low_eq`, `pan`, `send_a`, `send_b`, `resonance`, and `frequency` now use a shared elastic hybrid-fader model across all groups `1..6` and their subslots `.1/.2/.3`.
- With one active subslot the encoder follows directly; with multiple active subslots the values compress elastically toward `0` or `1` at the limits and reopen when the fader moves back from the boundary.
- Active hybrid slots now bootstrap from the current live group value when they still hold an uninitialized zero memory, so restored or newly added slots like `2.3` do not stay detached on `send_a`, `resonance`, or `frequency`.
- `vcm600_callbacks` writes normalized input into the visible device tables and `/project1/eventbus`.
- `/project1/Midi_Bitwig_Ch1` to `/project1/Midi_Bitwig_Ch6` again contain local `eventbus` / `eventbus_core` nodes so each output block can show the outgoing MIDI events in readable table form.
- `/project1/Midi_Bitwig_Ch1/midi_out` is again fed from `mapped_midi` instead of the temporary `direct_test` source.
- `/project1/Group_MIDI_Map` is again flattened to the lean core: direct `mapped_midi_1..6`, direct `out1..out6`, one combined `current_values_all`, and no inner `Group_1_MIDI_Map` to `Group_6_MIDI_Map` compatibility blocks.
- The external MIDI routing is only stable when the Bome network stays linear as `TouchDesigner MIDI Out -> Bitwig MIDI In`; a `Bitwig MIDI Out -> Bitwig MIDI In` loop blocks the expected receive path.

## Open Items
- Build `/project1/intent`.
- Restore the VCM-600 MIDI output device binding so LED transport can send live again without interface warnings.
- Decide later whether VCM-600 should control Bitwig again through the supported existing path or stay decoupled.
- Continue the CHOP-first root-level reorganization so project areas read more like connected TD blocks than software folders.
- Live-test the new fixed group outputs `11..16` from real VCM-600 controls and confirm that active subtracks mirror correctly.
- Live-test the centralized slot memory and pickup behavior from real VCM-600 input and confirm that the first movement after slot activation no longer causes unwanted jumps.

## Next Step
- Live-test one real VCM-600 group control against `/project1/state/channel_value_memory` and confirm that the matching active subtracks receive MIDI on channels `1/2/3` inside the corresponding Bitwig output group without unwanted pickup jumps.
