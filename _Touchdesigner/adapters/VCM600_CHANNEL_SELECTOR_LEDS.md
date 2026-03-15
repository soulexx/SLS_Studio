# VCM600 Channel Selection LEDs

## Purpose
- Renders VCM-600 LED feedback from shared channel-selection state.
- This block is state-driven.

## Input
- `/project1/state/channel_state`

## Output
- VCM-600 LED messages through the existing VCM-600 LED transport path.

## Internal Layers
- `state_in`
- `led_map`
- `desired_led_state`
- `render_led_diff`
- `render_core`
- `led_out_debug`

## Rule
- Do not render from raw button events.
- Read semantic channel state.
- Build a desired LED image.
- Compare against the last rendered image.
- Send only changes unless a full refresh is requested.

## LED Semantics
- exact focused `track_x.y` slot = bright
- other slots inside enabled channels = medium
- inactive channel = off
