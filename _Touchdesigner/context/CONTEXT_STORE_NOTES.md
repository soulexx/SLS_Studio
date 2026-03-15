# Context Store Notes

## Purpose
- Holds the active semantic interaction state for the system.
- This is the shared context read later by intent blocks and adapters.

## Stored Fields
- `mode`
- `target`
- `selection`
- `page`

## Rule
- Store readable semantic values.
- Do not store raw MIDI or hardware-specific event data here.
