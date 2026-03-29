# Project State

Last Updated: 2026-03-30
Worked On: 2026-03-30

## Current Status
- Core routing architecture is present and live in `/project1`.
- `/project1` currently reports 0 node errors.
- Root project docs are `/project1/docs_AGENTS_md` and `/project1/docs_PROJECT_STATE_md`.
- This state was re-audited against the live `.toe` on 2026-03-30 via MCP.
- Clip Shuffle planning Phase 0 is now fixed as a project specification and may be used as the basis for Phase 1 implementation.
- Root network layout in `/project1` was reorganized on 2026-03-29 and refined again on 2026-03-30 for operator readability; no node paths or live logic were changed.
- Key observability tables on root were enlarged and visually prioritized to serve as a central read surface for selection, target resolution, clip runtime, clip commit, and clip ops status.

## Critical Documentation Status
- There are no canonical project documentation files outside the TouchDesigner project for this workflow.
- Canonical project docs live in root textDATs:
  - `/project1/docs_AGENTS_md`
  - `/project1/docs_PROJECT_STATE_md`
- Project documentation must be read and updated through MCP against the live `.toe`.
- When a project doc DAT is edited, update its `Last Updated` / `Worked On` date.

## Active .toe
- Active `.toe`: `SLS_Studio_1.2.17.toe`
- TD auto-backup: `SLS_Studio_1.2.toe`
- Runtime root: `/project1`
- Direct children in `/project1`: 189 (verified 2026-03-30)

## Current Live Test Snapshot
- `test__cases`: 121 cases
- `test__results`: 120 `PASS`, 0 `FAIL`, 1 `VISUAL`
- Latest snapshot verified live on 2026-03-30

## Live Architecture Snapshot
**Maps:**
`maps__selector`, `maps__led_slots`, `maps__led_colors`, `maps__bitwig_send`, `maps__bitwig_paths`, `maps__bitwig_remote`, `maps__bitwig_special`, `maps__cntrlr_led_slots`

**Logic:**
`logic__map_reader`, `logic__control_exec`, `logic__domain_updater`, `logic__control_resolver`, `logic__event_normalizer`, `logic__priority_resolver`, `logic__selection_effective_merge`, `logic__channel_selector`, `logic__gummiband`

**State:**
`state__resolved_targets_raw`, `state__resolved_targets`, `state__selection_base`, `state__selection_temp`, `state__selection_effective`, `state__current_values`, `state__value_memory`, `state__modifier`, `state__focus`

**Outputs:**
`out__bitwig_router`, `out__led_router`, `out__view_router`, `out__debug_router`, `out__vcm600_leds`, `out__cntrlr_leds`

**Debug / Ops / Docs / Test:**
`debug__perf`, `debug__event`, `debug__state`, `debug__errors`, `debug__resolve`, `debug__targets`, `debug__conflicts`, `debug__action_log`
`ops__health`, `ops__metrics`, `ops__feature_flags`, `ops__recovery`, `ops__snapshots`
`docs__system_map`, `docs__resolver_rules`, `docs__runbook`
`test__cases`, `test__runner`, `test__results`, `run__tests`

## Verified Bitwig Surface
- `bitwigMain`
- `bitwigTrack1`–`bitwigTrack6`, `bitwigTrackMaster`
- `bitwigClipSlot1_1`–`bitwigClipSlot6_3` (18 live clip slot nodes)
- `bitwigRemotesTrack1`–`bitwigRemotesTrack6`
- `bitwigRemotesTrack1_1`–`bitwigRemotesTrack6_3`
- `bitwigClipLauncherCallbacks1`–`bitwigClipLauncherCallbacks18`

## Known Documentation Mismatches
- `docs__system_map` still contains a legacy row for `group_level_bridge` marked `soft_removed`, but no live node named `group_level_bridge` exists in `/project1`.
- No live node named `debug__bitwig_writes` exists in `/project1`; any documentation claiming it is active is stale.
- Legacy references to `docs__agents` / `docs__project_state` are stale; the live root docs are `docs_AGENTS_md` / `docs_PROJECT_STATE_md`.

## Clip Shuffle Phase 0

### Goal
Fix the clip-shuffle domain in unambiguous terms before any new nodes are added.
Phase 0 defines vocabulary, scope, identity keys, and edge-case behavior only.

### Fixed Domain Definitions
- `instrument` = `group` `1..6`; one instrument maps to exactly one Bitwig track column via `maps__bitwig_paths`.
- `track` = the Bitwig track node for a group, e.g. `bitwigTrack1` for group `1`.
- `slot` = observed clip slot inside one instrument, currently only `1..3`, 1-based.
- `channel` = existing selection key in `state__selection_effective`, formatted as `group.slot`, e.g. `1.2`.
- `active instrument` = a group for which at least one channel row `group.slot` is active in `state__selection_effective`.
- Multiple active channels within the same group still count as exactly one active instrument for clip-shuffle decisions.
- `clip surface` for V1 = only the live observed nodes `bitwigClipSlot{1-6}_{1-3}`.
- `has_clip` = domain flag indicating whether an observed slot currently contains a clip.
- `block` = a contiguous run of observed slots with `has_clip=1` inside one instrument.
- Empty slot(s) split blocks hard; multiple empty slots still act as one separator region.
- `current_block` = the block currently associated with an instrument runtime state.
- `play` = for each active instrument, choose one slot from the current block using that block's shuffle-bag, then launch it.
- `shift+play` = for each active instrument, choose a random other block in the same instrument; set `current_block`; then perform normal `play`.
- `other block` means block id `!= current_block`; if only one block exists, the current block remains unchanged.
- `shuffle` = no repetition within a block cycle; when the bag becomes empty, refill from the block's slot list and increment cycle state.
- `simultaneous` = one action batch covering all active instruments for the trigger.
- `domain state leads` = TD state decides selection/runtime; Bitwig performs execution and provides feedback for reconciliation.
- `external start` inside the observed 6x3 clip surface is adopted by reconciliation.
- `external start` outside the observed 6x3 clip surface is out of V1 scope and is not modeled as a reliable clip-runtime source.

### Explicit Edge-Case Decisions
- If an instrument has `0` blocks, `play` and `shift+play` emit no launch action for that instrument.
- If an instrument has exactly `1` block, `shift+play` stays on that block.
- If a block has exactly `1` slot, shuffle always returns that slot.
- If several channels of the same group are active, the clip action still targets the group once, not once per active channel.
- Phase 0 does not assume hidden scenes, paged clip banks, or track content beyond the observed `1..3` slots.
- Clip-domain runtime is separate from `state__selection_effective`; selection determines eligible instruments, not clip history.

### Definition of Done
- Every term above can be mapped to a live project object, table, or node naming scheme.
- The difference between `instrument`, `track`, `slot`, and `channel` is fixed with no ambiguity.
- The active-instrument rule is fixed and derived from `state__selection_effective`.
- The V1 clip observation scope is fixed to `bitwigClipSlot{1-6}_{1-3}`.
- Edge cases for `0` blocks, `1` block, `1` slot, and external starts are explicitly decided.
- The separation between selection-state and clip-runtime-state is fixed.

### Audit
- Question: Are `1.1`, `1.2`, and `1.3` three instruments?
  Answer: No. They are three channels inside one instrument/group.
- Question: If `1.1` and `1.2` are active, how many clip decisions does group 1 receive on `play`?
  Answer: Exactly one.
- Question: What happens on `shift+play` when only one block exists?
  Answer: Stay on the same block and continue with normal shuffle.
- Question: What happens when no clips exist for an active instrument?
  Answer: No launch action is produced for that instrument.
- Question: What happens if Bitwig starts a clip outside the observed `1..3` surface?
  Answer: V1 treats it as out of scope for reliable runtime reconciliation.
- Question: Is `state__selection_effective` allowed to store shuffle/runtime history?
  Answer: No. Clip runtime must live in its own clip-domain state.

### Phase 0 Test Cases
1. Selection example: `1.1=1`, `1.2=1`, `2.3=1` -> active instruments are `{1,2}`.
2. Group slots `[x x _]` -> exactly one block with slots `[1,2]`.
3. Group slots `[x _ x]` -> two blocks: `[1]` and `[3]`.
4. Group slots `[_ _ _]` -> zero blocks.
5. One instrument, one block, one slot -> every `play` returns that slot.
6. One instrument, one block, `shift+play` -> stays on same block.
7. Two instruments active at once -> one action batch containing up to one launch per active instrument.
8. External Bitwig start on observed slot `2.3` -> reconciliation may adopt instrument `2`, slot `3`, and its containing block.
9. External Bitwig start outside observed surface -> ignored as V1 runtime authority.

### Phase 0 Result
Phase 0 is complete as a specification baseline.
Phase 1 may now define observer nodes, normalization output, and raw clip-slot state against this domain.

## Clip Shuffle Phase 1

### Goal
Transform the fixed observed 6x3 Bitwig clip surface into one stable, raw, auditable domain truth.
Phase 1 covers only observers, normalization, raw state, and minimal rebuild consistency.
No block semantics, shuffle semantics, or playback decisions exist in this phase.

### Scope
Included in Phase 1:
- fixed observer / adapter layer for the live 6x3 clip surface
- normalization into domain rows
- `state__clip_slots_raw`
- minimal observer health / rebuild visibility

Excluded from Phase 1:
- block building
- shuffle logic
- play / shift-play selection
- runtime reconciliation
- UI / colors / musical semantics

### Planned Architecture
- `in__bitwig_clip_observers`
- `logic__clip_normalizer`
- `state__clip_slots_raw`
- `out__clip_debug_router` for minimal visibility

### Fixed Observer Model
- Phase 1 uses exactly 18 fixed observer instances.
- Observer surface is `bitwigClipSlot1_1` through `bitwigClipSlot6_3`.
- No dynamic observer creation is part of V1.
- Each observer has one fixed domain address and may only write to that address.

### Raw State Schema
`instrument | lane | observer_id | track_token | slot | has_clip | clip_name | source_epoch`

Field meaning:
- `instrument` = group / track column `1..6`
- `lane` = observed lane within the fixed V1 surface `1..3`
- `observer_id` = stable observer identity such as `1_2`
- `track_token` = stable technical link back to the observer / track binding
- `slot` = observed vertical slot index
- `has_clip` = `0` or `1`
- `clip_name` = clip name or empty string when no clip exists
- `source_epoch` = rebuild / sync generation marker

### Fixed Design Decisions
- Phase 1 stores a full raster, not sparse rows.
- Every observed slot has an explicit row, including empty slots.
- `clip_name` must be normalized to `""` when `has_clip=0`.
- `observer_id` is stored explicitly for audit/debug reasons.
- `state__clip_slots_raw` must not depend on `state__selection_effective`.
- Repeating the same rebuild over unchanged Bitwig state must yield identical raw content except for `source_epoch` if intentionally incremented.

### Definition of Done
- All 18 fixed observer instances feed `state__clip_slots_raw`.
- Each row is uniquely identifiable by `instrument + lane + slot`.
- No duplicate or contradictory rows exist.
- Clip add, delete, and rename operations inside the observed 6x3 surface are reflected correctly.
- The raw state makes no claims outside the observed 6x3 surface.
- Selection changes do not alter the raw clip state.
- Rebuild of unchanged source data is deterministic.
- Observer failures or missing data become visible in a debug/error surface and do not fail silently.

### Audit
- Mapping audit: `bitwigClipSlot2_3` may only affect `instrument=2`, `lane=3`.
- Slot audit: slot indices remain stable and show no off-by-one drift.
- Change audit: clip insert, delete, rename, empty tracks, full tracks, and gap patterns are reflected exactly.
- Idempotence audit: two identical rebuilds produce the same raw content.
- Boundary audit: changes outside the observed 6x3 surface do not change raw state.
- Separation audit: selection-state changes do not change raw state.

### Phase 1 Test Cases
1. `P1-T01` empty observed track -> all rows present, all `has_clip=0`, all `clip_name=""`.
2. `P1-T02` single clip -> exactly one row `has_clip=1`, all others empty.
3. `P1-T03` gap pattern `x x _ x _ _ x` -> raw occupancy matches exactly; no block semantics yet.
4. `P1-T04` rename -> `clip_name` changes, `has_clip` stays stable.
5. `P1-T05` delete -> `has_clip` becomes `0`, `clip_name` becomes `""`.
6. `P1-T06` observer mapping -> change on `bitwigClipSlot4_2` affects only `instrument=4`, `lane=2`.
7. `P1-T07` full rebuild -> identical state content on unchanged source, except `source_epoch` if designed that way.
8. `P1-T08` out-of-scope change -> no effect on `state__clip_slots_raw`.

### Phase 1 Result
Phase 1 is complete when the project can say with certainty and auditability which observed slots in the live 6x3 surface contain clips.
No semantics beyond raw occupancy belong here.

## Clip Shuffle Phase 2

### Goal
Derive deterministic clip blocks from `state__clip_slots_raw`.
Phase 2 starts semantic segmentation, but still does not decide playback, shuffle order, or runtime behavior.

### Scope
Included in Phase 2:
- block building from raw clip occupancy
- `logic__clip_block_builder`
- `state__clip_blocks`
- deterministic rebuild rules for block segmentation
- debug visibility for block boundaries and counts

Excluded from Phase 2:
- runtime state
- shuffle bags
- current block switching
- play / shift-play decisions
- reconciliation logic

### Planned Architecture
- `logic__clip_block_builder`
- `state__clip_blocks`
- optional extension in `out__clip_debug_router` for block visibility

### Input Contract
- Phase 2 reads only normalized raw clip truth from `state__clip_slots_raw`.
- Phase 2 must not read selection state to decide block structure.
- Phase 2 must not infer unseen slots outside the Phase-1 observer scope.

### Block Rules
- A block is a contiguous run of rows within one instrument with `has_clip=1`.
- Empty rows split blocks hard.
- Multiple adjacent empty rows still act only as a separator; they do not create phantom blocks.
- Block order is positional and deterministic.
- For V1, block building is restricted to the observed slot surface produced in Phase 1.

### Block State Schema
`instrument | block_id | start_slot | end_slot | slot_list | clip_count | source_epoch`

Field meaning:
- `instrument` = group / track column `1..6`
- `block_id` = deterministic block index within one instrument, ordered from top to bottom
- `start_slot` = first slot in the block
- `end_slot` = last slot in the block
- `slot_list` = ordered slot list for the block, e.g. `1,2,3`
- `clip_count` = number of clip-bearing slots in the block
- `source_epoch` = inherited or rebuilt generation marker tied to the raw source snapshot

### Fixed Design Decisions
- `block_id` is positional and must be recomputed deterministically from the current raw state.
- `slot_list` preserves ordered slot membership exactly as observed.
- Empty instruments produce zero block rows.
- Single-slot blocks are valid blocks.
- Phase 2 stores no runtime fields such as `current_block`, `last_slot`, or shuffle bag contents.
- Phase 2 must remain a pure transformation from raw occupancy to block segmentation.

### Definition of Done
- Every instrument's raw occupancy can be segmented into zero or more blocks with no ambiguity.
- Block boundaries match empty-slot separators exactly.
- `state__clip_blocks` contains no overlapping or contradictory blocks.
- `start_slot`, `end_slot`, `slot_list`, and `clip_count` agree with one another.
- Rebuilding from unchanged raw state yields identical block rows in identical order.
- Changes in raw clip occupancy rebuild blocks deterministically.
- Selection-state changes do not alter block structure.

### Audit
- Boundary audit: pattern `[x x x _ x x _ x]` yields three blocks with exact boundaries.
- Minimal audit: `[x]` yields one single-slot block.
- Empty audit: `[_ _ _]` yields zero blocks.
- Count audit: `clip_count` matches the length of `slot_list` for every row.
- Idempotence audit: repeated builds over unchanged raw state produce identical block rows.
- Separation audit: selection-state changes do not affect `state__clip_blocks`.
- Source audit: every block can be explained entirely by rows in `state__clip_slots_raw`.

### Phase 2 Test Cases
1. `P2-T01` `[x x x _ x x _ x]` -> blocks `[1,2,3]`, `[5,6]`, `[8]`.
2. `P2-T02` `[x]` -> one block with `start_slot=end_slot=1`.
3. `P2-T03` `[_ _ _]` -> zero blocks.
4. `P2-T04` `[x _ x]` -> two single-slot blocks.
5. `P2-T05` `[x x _ _ x]` -> exactly two blocks; double gap is only one separator region.
6. `P2-T06` rebuild with unchanged raw state -> identical `state__clip_blocks` content.
7. `P2-T07` rename-only change in Phase-1 raw state -> block structure unchanged.
8. `P2-T08` delete middle clip from `[x x x]` -> result becomes two blocks `[1]` and `[3]`.

### Phase 2 Result
Phase 2 is complete when the project can explain, for every instrument in the observed scope, exactly which contiguous clip blocks exist and why.
Playback semantics still do not belong to this phase.

## Next Work
1. Keep docs aligned with the live `.toe`.
2. Repair `docs__system_map` when node add/remove work happens.
3. Phase 8 operability is live; next likely step is Phase 9 polish / operator runbook refinement.

## Last Verified
- Date: 2026-03-30
- TD MCP reachable
- `/project1` has 0 reported TD node errors
- Root docs verified: `/project1/docs_AGENTS_md`, `/project1/docs_PROJECT_STATE_md`
- `test__cases` = 121
- `test__results` = 120 PASS, 0 FAIL, 1 VISUAL
- Live docs mismatch noted for `group_level_bridge` row in `docs__system_map`

## Test Maintenance Rule
- Tests are mandatory project assets, not optional follow-up work.
- New logic must ship with matching tests in `test__cases` / `test__runner` when the feature belongs to the automated test surface.
- Tests that no longer match the live architecture must be updated or removed in the same change.
- Test maintenance is automatic project hygiene and is required on every relevant implementation pass.


## Clip Shuffle Phase 2 Status
- Implemented in live TD project on 2026-03-29.
- New nodes:
  - `/project1/logic__clip_block_builder`
  - `/project1/state__clip_blocks`
  - `/project1/debug__clip_blocks`
- Phase 2 reads only from `/project1/state__clip_slots_raw`.
- Block segmentation is deterministic per `instrument + lane` and stores:
  - `block_id`
  - `start_slot`
  - `end_slot`
  - `slot_list`
  - `slot_count`
  - `source_epoch`
- Phase-2 tests were added to `test__cases` and `test__runner`:
  - `P2-T01` .. `P2-T10`
  - fixture-backed via `/project1/test__clip_phase1_fixtures`
  - current result: all `P2-*` tests PASS
- Important implementation detail:
  - Phase-2 logic follows the actual raw slot axis from Phase 1, including slot `0` when present.


## Clip Shuffle Phase 3 Status
- Implemented in live TD project on 2026-03-29.
- New nodes:
  - `/project1/logic__clip_runtime_builder`
  - `/project1/logic__clip_shuffle_builder`
  - `/project1/state__clip_runtime`
  - `/project1/state__clip_shuffle`
  - `/project1/debug__clip_runtime`
  - `/project1/debug__clip_shuffle`
  - `/project1/test__clip_phase3_blocks`
- Runtime state is now maintained per `instrument + lane`.
- Shuffle state is now maintained per block and uses a structural `signature` for persistence across rebuilds.
- Phase-3 tests were added to `test__cases` and `test__runner`:
  - `P3-T01` .. `P3-T10`
  - fixture-backed via `/project1/test__clip_phase3_blocks`
  - current result: all `P3-*` tests PASS
- Phase 3 remains separate from trigger logic and selection-state semantics.


## Clip Shuffle Phase 4 Status
- Implemented in live TD project on 2026-03-29.
- New nodes:
  - `/project1/logic__clip_target_reader`
  - `/project1/logic__clip_selector`
  - `/project1/state__clip_selection_plan`
  - `/project1/state__clip_selection_effects`
  - `/project1/debug__clip_selector`
  - `/project1/test__clip_phase4_targets`
- Active clip unit is now the concrete target `instrument.lane`, not only the group.
- `play` uses the current block for each active target.
- `shift_play` chooses a random other valid block when available, otherwise falls back to the current block.
- Selection remains separate from mutation:
  - plan in `/project1/state__clip_selection_plan`
  - pending changes in `/project1/state__clip_selection_effects`
- Phase-4 tests were added to `test__cases` and `test__runner`:
  - `P4-T01` .. `P4-T10`
  - target fixtures via `/project1/test__clip_phase4_targets`
  - block/runtime fixtures via existing Phase-3 fixture infrastructure
  - current result: all `P4-*` tests PASS
- Phase 4 still performs no Bitwig router execution.
- Play scope is now group-bound by trigger channel in live use: `channel/1/play` only targets active clip lanes inside instrument `1`, `channel/2/play` only inside instrument `2`, etc.


## Clip Shuffle Phase 5 Status
- Implemented in live TD project on 2026-03-29.
- New nodes:
  - `/project1/logic__clip_action_group_builder`
  - `/project1/state__clip_action_group`
  - `/project1/state__clip_actions`
  - `/project1/state__clip_commit_plan`
  - `/project1/debug__clip_action_group`
  - `/project1/test__clip_phase5_groups`
- Phase 5 uses staged commit semantics.
- One `action_group_id` is created per trigger when there is at least one selected target.
- The staged layer now separates:
  - group meta in `/project1/state__clip_action_group`
  - per-target actions in `/project1/state__clip_actions`
  - pending state mutation in `/project1/state__clip_commit_plan`
- Phase-5 tests were added to `test__cases` and `test__runner`:
  - `P5-T01` .. `P5-T10`
  - trigger fixtures via `/project1/test__clip_phase5_groups`
  - current result: all `P5-*` tests PASS
- Phase 5 performs no router execution and no hidden runtime/shuffle commit.


## Clip Shuffle Phase 6 Status
- Implemented in live TD project on 2026-03-29.
- New nodes:
  - `/project1/out__bitwig_clip_router`
  - `/project1/logic__clip_commit_applier`
  - `/project1/logic__clip_reconciler_v1`
  - `/project1/state__clip_router_log`
  - `/project1/state__clip_reconcile_status`
  - `/project1/debug__clip_commit`
  - `/project1/test__clip_phase6_groups`
- Phase 6 now enforces router-first, group-wide staged commit.
- `out__bitwig_clip_router` remains logically dumb and works from staged actions only.
- `logic__clip_commit_applier` applies only the staged commit plan and refuses commit without routed actions and matching commit rows.
- `logic__clip_reconciler_v1` mirrors observed `playing_slot` into runtime and writes match/pending/mismatch status.
- Phase-6 tests were added to `test__cases` and `test__runner`:
  - `P6-T01` .. `P6-T10`
  - fixture-backed via `/project1/test__clip_phase6_groups`
  - current result: all `P6-*` tests PASS
- Phase 6 is the first effective execution phase, but reconciliation remains deliberately shallow and observational in V1.


## Clip Shuffle Phase 7 Status
- Implemented in live TD project on 2026-03-29.
- New nodes:
  - `/project1/logic__clip_reconciler_v2`
  - `/project1/logic__clip_reconcile_applier`
  - `/project1/state__clip_reconcile_policy`
  - `/project1/state__clip_external_events`
  - `/project1/debug__clip_reconcile_policy`
  - `/project1/test__clip_phase7_reconcile`
- Reconciliation now classifies external starts and desyncs instead of only mirroring them.
- Observed slots are mapped back onto block structure through live `slot_list` membership, not heuristic guessing.
- Runtime may now follow observed in-scope external reality under explicit policy.
- Shuffle is only minimally adjusted during reconciliation:
  - observed slot is pruned from `remaining_slots` when present
  - no aggressive cycle or block resets are performed
- `state__clip_action_group` now carries `reconcile_outcome` as historical trigger outcome.
- Phase-7 tests were added to `test__cases` and `test__runner`:
  - `P7-T01` .. `P7-T10`
  - observed-state fixtures via `/project1/test__clip_phase7_reconcile`
  - current result: all `P7-*` tests PASS


## Clip Shuffle Phase 8 Status
- Implemented in live TD project on 2026-03-29.
- New nodes:
  - `/project1/logic__clip_ops_monitor`
  - `/project1/logic__clip_recovery_manager`
  - `/project1/logic__clip_ops_test_helper`
  - `/project1/ops__clip_health`
  - `/project1/ops__clip_metrics`
  - `/project1/ops__clip_alerts`
  - `/project1/ops__clip_last_events`
  - `/project1/debug__clip_ops`
  - `/project1/state__clip_recovery_actions`
  - `/project1/debug__clip_recovery`
  - `/project1/ops__clip_snapshots`
  - `/project1/test__clip_stress_trigger`
  - `/project1/test__clip_stress_reconcile`
  - `/project1/test__clip_stress_rebuild`
  - `/project1/test__clip_stress_mixed`
  - `/project1/test__clip_replay`
- Phase 8 adds an operational layer over the clip domain:
  - health state in `/project1/ops__clip_health`
  - counters in `/project1/ops__clip_metrics`
  - active alerts in `/project1/ops__clip_alerts`
  - recent events in `/project1/ops__clip_last_events`
  - recovery proposals and applies in `/project1/state__clip_recovery_actions`
  - snapshots in `/project1/ops__clip_snapshots`
- Health states now collapse live clip-domain conditions into `ok`, `warning`, `degraded`, or `error`.
- Recovery remains conservative and visible; no hidden replay or auto-healing was added.
- Snapshot and replay support is fixture-backed for deterministic regression coverage.
- Phase-8 tests were added to `test__cases` and `test__runner`:
  - `P8-T01` .. `P8-T10`
  - current result: all `P8-*` tests PASS


## Known Issue — bitwigClipSlot Reconnect Drift
- Verified live on 2026-03-29.
- After disconnecting and reconnecting all `bitwigClipSlot{1-6}_{1-3}` nodes, some `Track` bindings can drift to the wrong Bitwig channel instead of preserving the expected `g.s` mapping.
- Reproduced immediately after a reconnect cycle.
- Observed mismatches in this session:
  - `/project1/bitwigClipSlot2_1` drifted from expected `2.1` to `1.2`
  - `/project1/bitwigClipSlot3_1` drifted from expected `3.1` to `1.1`
- Current workaround: audit all 18 `Track` parameters after reconnect and reapply the expected `g.s` mapping before continuing clip work.
- This should be treated as a tdBitwig / cursor-rebind issue, not a clip-selector issue.
