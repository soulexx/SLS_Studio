# Project State

## Current Focus
Use the established project workflow while keeping documentation, TouchDesigner mirrors, and Git history current.
Migrate channel interaction toward a stable hybrid model with explicit shared state and output consumers.

## Last Position
- TouchDesigner project at `/project1` was inspected.
- Main areas found: `bitwig`, `devices`, `mcp_webserver_base`.
- No TouchDesigner errors or warnings were found during the last health check.
- Project documentation is mirrored in TouchDesigner under `/project1/project_docs`.
- Git repository initialized and connected to GitHub.
- Device network layout was normalized for `vcm600`, `cntrlr`, `midicon`, and `midicraft`.
- Device mapping conventions are now maintained in `_Touchdesigner/devices/DEVICE_RULES.md` and mirrored in TouchDesigner as `/project1/devices/device_rules`.
- Rule text blocks are positioned at the beginning of their logical TouchDesigner areas.
- TouchDesigner and Bitwig are both running locally with `9099` and `8088` open as documented.
- Existing channel-selection logic still uses selector-era toggle state and is ready for migration to hybrid `channel_state`.
- VCM-600 production LED output is now separated from the debug test API.
- The shared channel state now includes exact slot focus for `track_1.1` to `track_6.3`, and Bitwig follows that slot.
- Channel-selection outputs now react to state DAT changes instead of polling each frame.

## Open Tasks
- Document device-specific logic as work continues.
- Decide on the preferred day-to-day commit cadence and branch routine.
- Continue documenting device-specific logic as work progresses.
- Apply the same layout discipline to future device or support areas when they are changed.
- Finish migrating channel selection toward `focused_channel` plus explicit enabled flags.
- Decide whether channel-enabled toggles should remain tied to slot presses or become a separate interaction.
- Restore the VCM-600 MIDI output binding so live LED sends work without the current MIDI interface warning.

## Next Step
Continue with actual project work, complete the channel-state migration, and keep `PROJECT_STATE.md` / `WORKLOG.md` updated when relevant parts are added, removed, replaced, or reorganized.

## Known Rules
- Stable rules belong in `AGENTS.md`.
- Current context belongs in `PROJECT_STATE.md`.
- Short chronological notes belong in `WORKLOG.md`.
- Important DEV documentation should also exist in TouchDesigner as synced `textDAT` nodes under `/project1`.
- DEV documentation and rules files should always be mirrored in TouchDesigner as synced `textDAT` nodes.
- Support/documentation nodes in TouchDesigner should be arranged in a logical grouped layout.
- Relevant project changes should trigger a check whether `PROJECT_STATE.md` and `WORKLOG.md` need updating.
- Device areas in TouchDesigner should be laid out in this order when possible: `I/O -> Verarbeitung -> Bus -> Debug -> Tests`.
- TouchDesigner layout order should start with `Rules` when a rules `textDAT` exists for that area.
- `_Touchdesigner/devices/DEVICE_RULES.md` is the authoritative source for device-mapping conventions.

## Last Verified
- Date: 2026-03-15
- TouchDesigner MCP reachable
- `/project1` structure inspected
- No TD errors or warnings detected
- `/project1/project_docs` created with synced documentation DATs
- Git initialized in project root
- GitHub remote connected and initial push completed
- `vcm600`, `cntrlr`, `midicon`, and `midicraft` reordered to the standard device layout
- `DEVICE_RULES.md` is synced into TouchDesigner at `/project1/devices/device_rules`
- `bitwig_rules` and `device_rules` are positioned at the beginning of their respective TouchDesigner areas
- TouchDesigner and Bitwig are both running with the documented OSC ports open
