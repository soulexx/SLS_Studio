# VCM-600 Notes

## Principles
- `vcm600` is the device adapter.
- `vcm600_map` is now the minimal physical input map.
- `vcm600_led_state` on root owns LED meaning.
- `vcm600` only renders that LED state back to MIDI.

## Current Runtime Areas
- Rules: `vcm600_notes`
- I/O: `led_in`, `vcm600_in`
- Verarbeitung: `vcm600_lookup`, `vcm600_callbacks`
- Bus: `current_bus_event`, `out1`, `vcm600_map`, `out2`
- LED: `vcm600_led_exec`, `vcm600_led_renderer`, `led_output_state`, `vcm600_midi_out`, `vcm600_led_send_log`
- Tests: `vcm600_all_leds_on`, `vcm600_all_leds_off`

## Map Rule
- `vcm600_map` now only contains: `etype`, `ch`, `idx`, `topic`
- no extra semantic columns live in the device map anymore

## Documentation Rule
- If live tests disagree with manuals or copied mappings, update the live map directly and keep this note short.
