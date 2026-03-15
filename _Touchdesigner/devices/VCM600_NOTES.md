# VCM-600 Notes

## Principles
- Do not hide corrections in callbacks.
- Correct `vcm600_map` and `vcm600_led_map` directly to live-confirmed values.
- Only button-style controls belong in `vcm600_led_map`.

## Current Test Nodes
- `vcm600_midi_out`
- `vcm600_led_test_api`
- `vcm600_led_send_log`
- `vcm600_all_leds_on`
- `vcm600_all_leds_off`

## Current Confirmed Mapping Notes
- Global upper `fx_grid` is corrected in tables to indices `12..19`.
- Global lower `fx_btn_grid` is corrected in tables to indices `70..77`.
- `all_leds_on/off` is currently driven from the live-confirmed `vcm600_led_map`.

## Documentation Rule
- If live tests disagree with imported manuals or copied mappings, update the tables directly and record the result here.
