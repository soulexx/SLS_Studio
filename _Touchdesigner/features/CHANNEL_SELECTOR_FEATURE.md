Channel Selector Feature

Purpose
- Bundles the channel selector behavior as one feature block.

Current Scope
- VCM-600 mapping
- selector event handling
- VCM-600 LED rendering for shared selector state
- shared active flag via /project1/state/global_state: channel_selector_active

Rule
- Shared selector truth lives in /project1/state/channel_selector_state.
- This feature reads events, mutates that shared truth, and renders LEDs from the same truth.
- If channel_selector_active = 0, selector input is ignored and selector LEDs render off.
