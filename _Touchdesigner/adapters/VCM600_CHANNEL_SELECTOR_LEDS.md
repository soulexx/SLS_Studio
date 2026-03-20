# VCM600 Channel Selector LEDs

## Purpose
- Renders VCM-600 LED feedback from `/project1/state/channel_selector_state`.
- This block is state-driven.

## Behavior
- Each of the 18 selector slots is an independent toggle.
- If `track_x.y` is active, its matching selector LED is on.
- If `track_x.y` is inactive, its matching selector LED is off.
- There is no per-group exclusivity and no single-focus replacement logic.
