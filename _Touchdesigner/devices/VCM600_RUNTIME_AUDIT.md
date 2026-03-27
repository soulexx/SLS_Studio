# VCM600 Runtime Audit

## Current Active Roles
- `/project1/vcm600/state_out`
  - active device-state foundation inside the `vcm600` block
  - currently feeds `/project1/vcm600/out1`
- `/project1/vcm600/out1`
  - visible raw/control export of the VCM-600 block
  - now again feeds the visible root selector flow directly
  - now again serves as the direct live source for `fx_grid` snapshots and core live-value readout
- `/project1/vcm600/vcm600_state`
  - stable table state
  - still remains the stable table source for normalized device state

## Reduction Rule
- Do not remove `state_out` or `out1` while they still serve one of the above active roles.
- Prefer keeping the device block lean and moving only truly necessary semantic helper logic downstream.
