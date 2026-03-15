# Context Notes

## Purpose
- `/project1/context` holds the current interaction context for the control system.
- It does not read raw MIDI directly.
- It does not send commands directly to Bitwig or LEDs.

## Core Fields
- `mode`
- `target`
- `selection`
- `page`

## Meaning
- `mode`: the active operating mode, for example `clip`, `fx`, `mixer`
- `target`: the target system or target area, for example `bitwig`
- `selection`: the currently selected object, for example `track_1`
- `page`: the current subpage or view, for example `launcher`

## First Example
- `mode = clip`
- `target = bitwig`
- `selection = track_1`
- `page = launcher`

In this state, VCM-600 selection buttons can choose the active Bitwig track, and the CNTRLR grid can represent the Bitwig clip launcher for that track.

## Test And Management
- `context_state` is the active current state.
- `context_presets` stores named preset states for quick testing.
- `context_api` applies and edits state values.
- `context_debug` mirrors the active state so changes are easy to verify.

## First State-Changing Input
- `vcm600/channel/1..6/cf_asn`
- `vcm600/channel/1..6/clip`
- `vcm600/channel/1..6/track`

These are currently treated as selection controls.

Example:
- `vcm600/channel/3/clip` -> `selection = track_3.2`

This is intentionally a context change, not yet a direct Bitwig command.

Current selector convention:
- `cf_asn` -> `.1`
- `clip` -> `.2`
- `track` -> `.3`

Examples:
- channel 1 -> `track_1.1`, `track_1.2`, `track_1.3`
- channel 2 -> `track_2.1`, `track_2.2`, `track_2.3`

## Design Rule
- Keep context semantic.
- Avoid numeric mode names like `mode_0` if a readable name exists.
- Devices produce events.
- Context stores meaning.
- Intent turns event + context into user intent.
