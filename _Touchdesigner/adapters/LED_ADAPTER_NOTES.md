# LED Adapter Notes

## Purpose
- LED handling should be state-driven, not event-driven.
- Adapters translate semantic state into hardware LED output.

## Core Flow
- `input event -> context/state mutation -> desired_led_state -> midi transport`

## Why
- The hardware button event is not the source of truth for LEDs.
- The current semantic state is the source of truth.
- LEDs should reflect the current state, not just the last press.

## Responsibilities

### `state_in`
- Reads only the relevant semantic state.
- Examples:
  - `selected_channel`
  - `active_layer`
  - `armed_channels`
  - local toggle states such as `channel_selector/toggle_state`

### `led_map`
- Knows only the mapping between semantic state targets and physical LED targets.
- Example:
  - `track_1.2 -> vcm600/channel/1/clip`

### `desired_led_state`
- Builds the intended LED image from semantic state.
- Example:
  - `vcm600/channel/1/clip = 127`
  - `vcm600/channel/2/track = 0`

### `render_led_diff`
- Compares previous LED image and current desired LED image.
- Sends only changed values when possible.
- Can also support a full refresh mode.

### `midi transport`
- Converts the LED render result into actual MIDI note/CC output.

### `led_out_debug`
- Shows:
  - input state snapshot
  - resolved LED target
  - desired value
  - sent value
  - changed / unchanged

## Design Rule
- Do not wire LEDs directly from input events.
- First mutate state.
- Then derive the LED image from state.

## First Planned Use
- `context/channel_selector/toggle_state`
- to
- `adapters/vcm600_channel_selector_leds`

This adapter should read the 18 independent toggle states and render the matching VCM-600 LEDs.
