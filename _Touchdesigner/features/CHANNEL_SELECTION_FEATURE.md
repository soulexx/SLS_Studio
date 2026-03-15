# Channel Selection Feature

## Purpose
- Bundles semantic channel selection logic as one feature block.

## Model
- Shared truth lives in `/project1/state/channel_state`.
- The feature reads normalized bus events and updates:
  - `focused_channel`
  - `focused_track_slot`
  - `focused_track_linear_index`
  - `channel_1_enabled` to `channel_8_enabled`

## Scope
- semantic interpretation of channel input
- focus changes down to the exact `track_x.y` slot
- enabled-channel toggles
- debug and tests for the channel-selection logic

## Rule
- The feature does not own LED rendering.
- The feature does not talk directly to Bitwig.
- If `channel_selection_active = 0`, input is ignored.
- Output consumers read the same shared channel state.
- The last selected `track_x.y` slot is the authoritative Bitwig target.
