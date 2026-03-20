# Bitwig Channel Selection Output

## Purpose
- Resolves semantic `track_x.y` slot selections to the correct Bitwig track positions.
- Moves the existing Bitwig track cursor from shared `channel_state`.

## Input
- `/project1/state/channel_state`

## Internal Layers
- `state_in`
- `bitwig_track_map`
- `output_core`
- `state_datexec`
- `debug`

## Rule
- Keep Bitwig-specific track-index mapping in `bitwig_track_map`.
- Use the existing `/project1/bitwig/bitwigTrack/bitwigTrack` cursor instead of duplicating Bitwig transport logic in the feature layer.
- Trigger on DAT changes from shared state instead of frame-end polling.
