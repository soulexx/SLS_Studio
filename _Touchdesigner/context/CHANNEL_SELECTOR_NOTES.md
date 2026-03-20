Channel selection logic.

Reads selector button events and updates shared selector truth in `/project1/state/channel_selector_state`.

Behavior
- `cf_asn` toggles `track_x.1`
- `clip` toggles `track_x.2`
- `track` toggles `track_x.3`
- all 18 slots are independent toggles
- no per-group exclusivity
- no single-focus replacement logic
