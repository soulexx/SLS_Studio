# Mapping Rules

## General
- Prefer live-confirmed values over manuals.
- Keep device-specific quirks in device maps, not in shared callbacks, unless the behavior is proven global and stable.
- Use 1-based numbering in user-facing topics.

## Topics
- Linear controls:
  - `device/faders/1`
- Matrix controls:
  - `device/grid_4x4/1/1`
  - `device/knobs_left/1/1`
  - `device/encoders/1/1`

## Labels
- Use readable labels that match the physical layout.
- Matrix labels should be explicit, for example:
  - `4x4 Grid 1/1`
  - `2x16 Grid 2/4`
  - `Encoder Push 1/3`

## Event Preparation
- Device callbacks prepare events before they reach the eventbus.
- Eventbus should stay minimal.
- Button values: `0` or `1`
- Standard CC values: `0..1`
- Endless encoders: step values such as `-1`, `0`, `1`

## VCM-600
- Maps are corrected directly to confirmed values.
- `vcm600_map` and `vcm600_led_map` should reflect actual hardware values.
- Only button-style controls belong in `vcm600_led_map`.
- Current live-confirmed global grid corrections:
  - `vcm600/global/fx_grid/*/*` uses indices `12..19`
  - `vcm600/global/fx_btn_grid/*/*` uses indices `70..77`

## CNTRLR
- Direct LED hardware tests use channel 1.
- Confirmed hardware color values:
  - `2` white
  - `64` yellow
  - `4` cyan
  - `8` magenta
  - `16` red
  - `127` green
  - `32` blue
  - `0` off
- Endless encoders are evaluated by difference to previous value, with wraparound handling.
