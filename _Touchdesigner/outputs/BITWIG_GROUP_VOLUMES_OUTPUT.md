# Bitwig Group Volumes Output

## Purpose
- Maps VCM-600 channel faders 1 to 6 to Bitwig group-track volume.
- Keeps the group-name mapping close to the Bitwig output that uses it.

## Input
- `/project1/state/group_volume_state`

## Internal Layers
- `bitwig_group_volumes_notes`
- `group_volume_map`
- `output_core`
- `output_debug`

## Rule
- `group_volume_map` is the source of truth for `channel -> Bitwig track name`.
- State stores normalized `channel_n_volume` values.
- The output applies those values to the existing `/project1/bitwig/bitwigTrack/bitwigTrack` component.
- If live Bitwig group names differ from the provisional defaults, correct them directly in `group_volume_map`.
