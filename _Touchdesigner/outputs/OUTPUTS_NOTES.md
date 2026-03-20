# Outputs Notes

## Purpose
- Holds downstream consumers that read shared project state and drive external targets.
- Keeps target-specific logic out of features.

## Rule
- Outputs read shared truth.
- Outputs do not reinterpret raw device events.
- Target-specific mapping tables should stay close to the output that uses them.
