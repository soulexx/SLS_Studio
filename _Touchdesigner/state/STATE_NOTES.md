# State Notes

## Purpose
- Holds shared project state that should not live inside a single device.
- Stores current truth, not raw input.
- Reusable feature truth belongs here when more than one block reads it.

## Examples
- active mode
- active page
- target app
- shared selections or shared assignments
- feature state reused by LEDs, intent, or other features

## Rule
- State stores truth.
- It should be readable and semantic.
- Events belong in `eventbus`.
- Shared truth belongs in `state`.
