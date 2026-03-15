# Project State

## Current Focus
- Define the modular interaction architecture after device and LED verification.
- Root structure is now moving toward `state`, `modes`, and `features`.
- Separate reusable channel truth from feature-local logic and output consumers.

## Verified Status
- `devices` for `vcm600` and `cntrlr` are active and mapped.
- Both devices write normalized events into `/project1/eventbus`.
- VCM-600 LED tests work from the device area.
- CNTRLR LED tests work on direct hardware channel 1, including color values and test animations.
- `/project1/state/global_state` holds shared semantic state.
- `/project1/state/global_state` holds feature enable flags.
- Existing channel-selection logic and LED rendering are being migrated from selector-specific toggle state to shared `channel_state`.
- Bitwig is reachable again on `127.0.0.1:8088` and TouchDesigner is listening on `9099`.
- VCM-600 now has a dedicated production LED transport in `devices`; test sending remains separate as debug-only API.
- `/project1/state/channel_state` now stores `focused_track_slot` and `focused_track_linear_index` as the authoritative Bitwig target.
- `/project1/outputs/bitwig_channel_selection` now follows the last selected `track_x.y` slot and applies it to the Bitwig track cursor.
- Channel-selection outputs now react on `channel_state` DAT changes instead of frame-end polling.

## Open Items
- Build `/project1/intent`.
- Decide first concrete Bitwig interaction flow for `clip` mode.
- Decide whether channel enable should continue toggling on `clip` / `cf_asn` or be split from slot selection later.
- Restore the VCM-600 MIDI output device binding so LED transport can send live again without interface warnings.

## Next Step
- Validate the central hybrid channel state flow live on hardware and then define the first `modes` block.
