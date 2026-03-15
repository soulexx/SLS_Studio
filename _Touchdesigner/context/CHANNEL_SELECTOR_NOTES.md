Channel selection logic.

Reads normalized channel events from the eventbus and updates shared channel truth in `/project1/state/channel_state`.
The feature sets one `focused_channel` and maintains explicit `channel_n_enabled` flags for the enabled set.
