# SLS Studio Project Rules

## Purpose
This project contains the TouchDesigner setup and related project files for SLS Studio.

The goal of this file is to provide stable instructions that should apply in every new chat for this project.

## Startup Routine
At the beginning of every new chat in this project:

1. Read `AGENTS.md`.
2. Read `PROJECT_STATE.md`.
3. Inspect the relevant project area before proposing changes.
4. Prefer updating project documentation when the current state changes.

## Source Of Truth
- Stable project rules live in `AGENTS.md`.
- Current working context lives in `PROJECT_STATE.md`.
- Human-readable change history lives in `WORKLOG.md`.
- Technical file history should live in Git commits and GitHub.

## Project Structure
- `_Touchdesigner/` contains the TouchDesigner-related project assets and support files.
- TouchDesigner runtime project currently centers around `/project1`.
- Known main areas inside `/project1`:
  - `bitwig`
  - `devices`
  - `mcp_webserver_base`
- Device-specific mapping conventions live in `_Touchdesigner/devices/DEVICE_RULES.md`.
- Bitwig-specific conventions live in `_Touchdesigner/bitwig/BITWIG_RULES.md`.

## Working Rules
- Keep documentation concise and current.
- Do not replace durable rules in this file with temporary session notes.
- Put temporary progress, current focus, and next actions in `PROJECT_STATE.md`.
- Add short dated entries to `WORKLOG.md` for meaningful changes or milestones.
- When uncertain about intent or architecture, ask before making irreversible structural changes.
- Prefer incremental edits over broad refactors.
- Before modifying TouchDesigner logic, inspect the relevant COMP/DAT/CHOP/TOP structure first.
- When adding project support nodes in TouchDesigner, use a logical layout and grouping instead of leaving nodes loose in the root.

## Documentation Rules
- `PROJECT_STATE.md` should stay short and operational.
- `WORKLOG.md` should contain brief chronological notes, not long narratives.
- Record verified system status when it materially changes.
- Record open issues and next steps explicitly.
- Documentation and rules files in the DEV workspace should always be represented inside TouchDesigner as synced `textDAT` nodes.
- Project documentation and rules that should be visible in TouchDesigner must live under logical TouchDesigner areas as file-synced `textDAT`s.
- Mirrored documentation nodes should be grouped in a dedicated logical area, not scattered across `/project1`.
- When relevant project parts are added, removed, replaced, or significantly reorganized, ask whether `PROJECT_STATE.md` and `WORKLOG.md` should be updated.
- When the active focus changes, ask whether `PROJECT_STATE.md` should be updated.
- When durable project rules change, update `AGENTS.md`.

## TouchDesigner Notes
- Check for TouchDesigner errors and warnings when validating the project state.
- When reviewing device logic, inspect mappings, callbacks, lookup tables, and active MIDI I/O nodes.
- Treat external files referenced by DATs as part of the project context.
- Keep important DEV documentation mirrored in TouchDesigner so project context is available from both the filesystem and the TD network.
- When working in `devices`, read `_Touchdesigner/devices/DEVICE_RULES.md` as the authoritative device-mapping reference.
- When working in `bitwig`, read `_Touchdesigner/bitwig/BITWIG_RULES.md` as the authoritative Bitwig integration reference.
- Prefer clear spatial organization in the TouchDesigner network:
  - group related nodes inside a dedicated COMP when appropriate
  - keep root-level layout readable
  - place documentation, support, and runtime areas in clearly separated regions
- Rules `textDAT` nodes should appear at the beginning of a logical TouchDesigner area so they are immediately visible.
- For TouchDesigner node layout, sort related blocks in this order when possible:
  - Rules
  - I/O
  - Verarbeitung
  - Bus
  - Debug
  - Tests

## Change Tracking
- Use Git for real version history.
- Prefer small, focused commits with clear messages.
- Use GitHub as the remote backup and collaboration history.

## Default Assistant Behavior
- Be concise and practical.
- Explain assumptions when they matter.
- If the requested change affects project conventions, update documentation too.
