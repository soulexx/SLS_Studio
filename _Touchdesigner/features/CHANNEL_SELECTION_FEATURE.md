# Channel Selection Feature

## Purpose
- Bundles semantic channel selection logic as one feature block.

## Model
- Shared truth lives in `/project1/state/channel_state`.
- The feature reads normalized bus events and updates:
  - `focused_channel`
  - `focused_track_slot`
  - `focused_track_name`
  - `channel_1_enabled` to `channel_6_enabled`

## Scope
- semantic interpretation of channel input
- focus changes down to the exact `track_x.y` slot
- enabled-channel state
- debug and tests for the channel-selection logic

## Rule
- The feature does not own LED rendering.
- The feature does not talk directly to Bitwig.
- If `channel_selector_active = 0`, input is ignored.
- Output consumers read the same shared channel state.
- Bitwig-specific slot-to-track-index mapping lives in the output layer.
