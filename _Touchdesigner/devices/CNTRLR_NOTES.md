# CNTRLR Notes

## Input Status
- CNTRLR input mapping is live-corrected and organized by physical groups.
- Matrix groups use `row/col`.
- Faders remain linear.

## Confirmed Layout
- Faders: `5, 9, 13, 17, 21, 25, 29, 33`
- Knob Left 3x4:
  - row 1: `2, 6, 10, 14`
  - row 2: `3, 7, 11, 15`
  - row 3: `4, 8, 12, 16`
- Knob Right 3x4:
  - row 1: `18, 22, 26, 30`
  - row 2: `19, 23, 27, 31`
  - row 3: `20, 24, 28, 32`
- Encoders 3x4:
  - row 1: `49, 52, 55, 58`
  - row 2: `50, 53, 56, 59`
  - row 3: `51, 54, 57, 60`
- Encoder Push 3x4:
  - same positions as encoders
  - `note`
  - push sends `Note On` value `64`
- 4x4 Grid:
  - row 1: `1, 5, 9, 13`
  - row 2: `2, 6, 10, 14`
  - row 3: `3, 7, 11, 15`
  - row 4: `4, 8, 12, 16`
- 2x16 Grid:
  - row 1: `17` to `32`
  - row 2: `33` to `48`

## LED Status
- Direct hardware LED tests use MIDI channel `1`.
- Confirmed hardware color values:
  - `white = 2`
  - `yellow = 64`
  - `cyan = 4`
  - `magenta = 8`
  - `red = 16`
  - `green = 127`
  - `blue = 32`
  - `off = 0`

## Encoder Behavior
- Endless encoders should not be treated as absolute `0..1` controls.
- Current device callback derives direction from the difference to the previous value with wraparound handling.
- Current normalized bus output is directional:
  - one direction = `-1`
  - the other direction = `1`

## Test Area
- CNTRLR LED test helpers live in `/project1/devices/cntrlr`.
- `cntrlr_led_test_api` is a test-only tool, not the future production LED adapter.
