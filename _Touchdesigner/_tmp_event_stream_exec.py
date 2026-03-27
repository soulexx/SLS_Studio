
import math
import time

SELECTOR_BUTTONS = {'cf_asn', 'clip', 'track'}
CONTROL_REMAP = {
    'eq_hi': 'hi_eq', 'eq_mid': 'mid_eq', 'eq_low': 'low_eq', 'pan': 'pan', 'send_a': 'send_a', 'send_b': 'send_b',
    'resonance': 'resonance', 'frequency': 'frequency', 'hi_cut': 'hi', 'mid_cut': 'mid', 'low_cut': 'low',
    'mute': 'mute', 'solo': 'solo', 'cf_asn': 'cf_asn', 'clip': 'clip', 'track': 'track', 'stop': 'stop', 'play': 'play'
}
CONTROL_ORDER = ['hi_eq','mid_eq','low_eq','pan','send_a','send_b','resonance','frequency','hi','mid','low','mute','solo','cf_asn','clip','track','stop','play']
HYBRID_CONTROLS = ['hi_eq','mid_eq','low_eq','pan','send_a','send_b','resonance','frequency']
MEMORY_PATH = '/project1/project_memory/channel_value_memory'
HYBRID_STATE_PATH = '/project1/Instrument_Control_Core/hybrid_fader_state'
FX_GRID_MEMORY_PATH = '/project1/project_memory/fx_grid_memory'
FX_GRID_CONTROL_MEMORY_PATH = '/project1/project_memory/fx_grid_control_memory'
FOCUS_CONTEXT_STATE_PATH = '/project1/focus_context/focus_state'
MODULAR_FX_GRID_PATH = '/project1/vcm600_processing/fx_grid/out1'
GUMMIBAND_CORE_PATH = '/project1/gummiband_master/gummiband_core'
PICKUP_THRESHOLD = 0.03
EPSILON = 0.0001
FX_GRID_CONTROLS = ['hi_eq','mid_eq','low_eq','pan','send_a','send_b','resonance','frequency']
FX_GRID_ORDER = [
    'vcm600_global_fx_grid_1_1',
    'vcm600_global_fx_grid_1_2',
    'vcm600_global_fx_grid_1_3',
    'vcm600_global_fx_grid_1_4',
    'vcm600_global_fx_grid_2_1',
    'vcm600_global_fx_grid_2_2',
    'vcm600_global_fx_grid_2_3',
    'vcm600_global_fx_grid_2_4',
]


def _clamp(v):
    return max(0.0, min(1.0, float(v)))


def _format_number(value):
    try:
        value = float(value)
    except Exception:
        return str(value)
    if abs(value - round(value)) < 1e-6:
        return str(int(round(value)))
    return '{:.3f}'.format(value)


def _memory():
    return op(MEMORY_PATH)


def _ensure_memory():
    d = _memory()
    if not d:
        return None
    if d.numRows == 0:
        d.appendRow(['slot', 'group', 'sub', 'control', 'value', 'pickup_attached', 'last_diff'])
    existing = set()
    for row in range(1, d.numRows):
        existing.add((d[row, 0].val, d[row, 3].val))
    for group in range(1, 7):
        for sub in (1, 2, 3):
            slot = '{}.{}'.format(group, sub)
            for control in CONTROL_ORDER:
                if (slot, control) not in existing:
                    d.appendRow([slot, str(group), str(sub), control, '0', '1', '0'])
    return d


def _memory_row(group, slot, control_name):
    d = _ensure_memory()
    if not d:
        return None, None
    for row in range(1, d.numRows):
        if d[row, 1].val == str(group) and d[row, 2].val == str(slot) and d[row, 3].val == control_name:
            return d, row
    return d, None


def _memory_value(group, slot, control_name):
    d, row = _memory_row(group, slot, control_name)
    if d is None or row is None:
        return 0.0
    try:
        return float(d[row, 4].val)
    except Exception:
        return 0.0


def _write_memory_value(group, slot, control_name, value, attached='1', last_diff='0'):
    d, row = _memory_row(group, slot, control_name)
    if d is None or row is None:
        return
    d[row, 4] = _format_number(value)
    d[row, 5] = str(attached)
    d[row, 6] = str(last_diff)


def _ensure_fx_grid_memory():
    table = op(FX_GRID_MEMORY_PATH)
    if not table:
        return None
    header = ['slot', 'group', 'sub'] + ['fx_grid_{}'.format(i) for i in range(1, 9)]
    if table.numRows == 0:
        table.appendRow(header)
    elif table.numCols != len(header) or any(table[0, i].val != header[i] for i in range(len(header))):
        table.clear()
        table.appendRow(header)
    existing = set()
    for row in range(1, table.numRows):
        existing.add((table[row, 1].val, table[row, 2].val))
    for group in range(1, 7):
        for slot in (1, 2, 3):
            key = (str(group), str(slot))
            if key not in existing:
                table.appendRow(['{}.{}'.format(group, slot), str(group), str(slot)] + ['0'] * 8)
    return table


def _ensure_fx_grid_control_memory():
    table = op(FX_GRID_CONTROL_MEMORY_PATH)
    if not table:
        return None
    header = ['slot', 'group', 'sub', 'control'] + ['fx_grid_{}'.format(i) for i in range(1, 9)]
    if table.numRows == 0:
        table.appendRow(header)
    elif table.numCols != len(header) or any(table[0, i].val != header[i] for i in range(len(header))):
        table.clear()
        table.appendRow(header)
    existing = set()
    for row in range(1, table.numRows):
        existing.add((table[row, 1].val, table[row, 2].val, table[row, 3].val))
    for group in range(1, 7):
        for slot in (1, 2, 3):
            for control in FX_GRID_CONTROLS:
                key = (str(group), str(slot), control)
                if key not in existing:
                    table.appendRow(['{}.{}'.format(group, slot), str(group), str(slot), control] + ['0'] * 8)
    return table


def _focus_control():
    d = op(FOCUS_CONTEXT_STATE_PATH)
    if not d:
        return ''
    for row in range(1, d.numRows):
        if d[row, 0].val == 'focus_control':
            return d[row, 1].val or ''
    return ''


def _write_fx_grid_snapshot(group, slot):
    table = _ensure_fx_grid_memory()
    control_table = _ensure_fx_grid_control_memory()
    src = op(MODULAR_FX_GRID_PATH)
    if not table or not src:
        return
    values = []
    for name in FX_GRID_ORDER:
        ch = src.chan(name.replace('vcm600_global_', ''))
        try:
            values.append(_format_number(float(ch[0])))
        except Exception:
            values.append('0')
    for row in range(1, table.numRows):
        if table[row, 1].val == str(group) and table[row, 2].val == str(slot):
            for idx, value in enumerate(values, start=3):
                table[row, idx] = value
            break
    control_name = _focus_control()
    if control_table and control_name in FX_GRID_CONTROLS:
        for row in range(1, control_table.numRows):
            if control_table[row, 1].val == str(group) and control_table[row, 2].val == str(slot) and control_table[row, 3].val == control_name:
                for idx, value in enumerate(values, start=4):
                    control_table[row, idx] = value
                break


def _name_to_parts(channel_name):
    prefix = 'vcm600_channel_'
    if not channel_name.startswith(prefix):
        return None, None, None, None
    rest = channel_name[len(prefix):]
    if '_' not in rest:
        return None, None, None, None
    group, control = rest.split('_', 1)
    topic = 'vcm600/channel/{}/{}'.format(group, control)
    etype = 'note' if control in {'hi_cut','mid_cut','low_cut','mute','solo','cf_asn','clip','track','stop','play'} else 'cc'
    label = 'Channel {} {}'.format(group, control.replace('_', ' ').title())
    return int(group), control, topic, {'etype': etype, 'label': label}


def _refresh_selector_outputs():
    op('/project1/channel_selector/selection_out').cook(force=True)
    router = op('/project1/channel_selector/bitwig_midi_router/router_core')
    env = {'op': op, 'me': router, 'time': time}
    exec(router.text, env)
    env['refresh']()


def _selection_for_topic(topic):
    selector_map = op('/project1/channel_selector/selector_logic/selector_map')
    if not selector_map:
        return None
    header = {selector_map[0, c].val: c for c in range(selector_map.numCols)}
    for r in range(1, selector_map.numRows):
        if selector_map[r, header['topic']].val == topic:
            return selector_map[r, header['selection']].val
    return None


def _set_pickup_for_slot(group, slot):
    d = _ensure_memory()
    if not d:
        return
    for control_name in CONTROL_ORDER:
        if control_name in HYBRID_CONTROLS:
            continue
        _, row = _memory_row(group, slot, control_name)
        if row is None:
            continue
        stored = _memory_value(group, slot, control_name)
        live = _live_value(group, control_name)
        diff = live - stored
        d[row, 5] = '1' if abs(diff) <= PICKUP_THRESHOLD else '0'
        d[row, 6] = str(diff)


def _hybrid_state():
    return op(HYBRID_STATE_PATH)


def _active_slots(group):
    d = op('/project1/channel_selector/channel_selector_state')
    active = []
    if not d:
        return active
    for slot in (1,2,3):
        key = 'track_{}.{}'.format(group, slot)
        for row in range(1, d.numRows):
            if d[row,0].val == key and d[row,1].val == '1':
                active.append(slot)
                break
    return active


def _selector_active(group, slot):
    d = op('/project1/channel_selector/channel_selector_state')
    if not d:
        return '0'
    key = 'track_{}.{}'.format(group, slot)
    for row in range(1, d.numRows):
        if d[row, 0].val == key:
            return '1' if d[row, 1].val == '1' else '0'
    return '0'


def _active_mask(group):
    active = set(_active_slots(group))
    return ''.join('1' if i in active else '0' for i in (1,2,3))


def _live_value(group, control_name):
    src = op('/project1/Instrument_Control_Core/in{}'.format(group))
    src.cook(force=True)
    ch = src.chan(control_name) if src else None
    try:
        return float(ch[0])
    except Exception:
        return 0.0


def _ensure_hybrid():
    d = _hybrid_state()
    if not d:
        return None
    expected = ['group','control','mask','last_live','base_1','base_2','base_3','out_1','out_2','out_3','epsilon']
    needs_reset = d.numRows == 0 or d.numCols != len(expected)
    if not needs_reset and any(d[0, i].val != expected[i] for i in range(len(expected))):
        needs_reset = True
    if needs_reset:
        d.clear()
        d.appendRow(expected)
    existing = set()
    for row in range(1, d.numRows):
        existing.add((d[row,0].val, d[row,1].val))
    for group in range(1, 7):
        for control in HYBRID_CONTROLS:
            if (str(group), control) not in existing:
                d.appendRow([str(group), control, '000', '0', '0', '0', '0', '0', '0', '0', str(EPSILON)])
    return d


def _hybrid_row(group, control_name):
    d = _ensure_hybrid()
    if not d:
        return None, None
    for row in range(1, d.numRows):
        if d[row,0].val == str(group) and d[row,1].val == control_name:
            return d, row
    return d, None


def _anchor_hybrid(group, control_name):
    d, row = _hybrid_row(group, control_name)
    if d is None or row is None:
        return
    mask = _active_mask(group)
    live = _live_value(group, control_name)
    active = set(_active_slots(group))
    bases = []
    for slot in (1, 2, 3):
        md, mrow = _memory_row(group, slot, control_name)
        stored = 0.0
        attached = True
        if md is not None and mrow is not None:
            try:
                stored = float(md[mrow, 4].val)
            except Exception:
                stored = 0.0
            attached = md[mrow, 5].val == '1'
        # Only bootstrap a newly active hybrid slot from the current live value
        # when it still has no meaningful memory yet.
        if slot in active and (not attached) and abs(stored) <= EPSILON and abs(live) > EPSILON:
            stored = live
            _write_memory_value(group, slot, control_name, stored, '1', '0')
        base = _clamp(stored)
        bases.append(base)
    d[row, 2] = mask
    d[row, 3] = _format_number(live)
    for idx, base in enumerate(bases, start=1):
        d[row, 3 + idx] = _format_number(base)
        d[row, 6 + idx] = _format_number(base)
    d[row, 10] = str(EPSILON)


def _apply_hybrid_motion(bases, active, start_fader, fader):
    core = op(GUMMIBAND_CORE_PATH)
    if not core:
        return list(bases)
    env = {'op': op, 'me': core}
    exec(core.text, env)
    return env['apply_motion'](bases, active, start_fader, fader, EPSILON)


def _hybrid_outputs(group, control_name, value):
    active = _active_slots(group)
    if not active:
        return False
    d, row = _hybrid_row(group, control_name)
    if d is None or row is None:
        return False
    mask = ''.join('1' if i in active else '0' for i in (1,2,3))
    if d[row, 2].val != mask:
        _anchor_hybrid(group, control_name)
    bases = []
    for idx in range(1, 4):
        try:
            bases.append(float(d[row, 3 + idx].val or 0))
        except Exception:
            bases.append(0.0)
    try:
        start_fader = float(d[row, 3].val or 0)
    except Exception:
        start_fader = value
    if len(active) == 1:
        slot = active[0]
        out_value = _clamp(value)
        _write_memory_value(group, slot, control_name, out_value, '1', '0')
        d[row, 2] = mask
        d[row, 3] = _format_number(value)
        for idx in range(1, 4):
            mem_val = _memory_value(group, idx, control_name)
            d[row, 3 + idx] = _format_number(mem_val)
            d[row, 6 + idx] = _format_number(mem_val)
        return True
    outs = _apply_hybrid_motion(bases, active, start_fader, value)
    for slot in active:
        _write_memory_value(group, slot, control_name, outs[slot - 1], '1', '0')
    d[row, 2] = mask
    for idx in range(1, 4):
        d[row, 6 + idx] = _format_number(outs[idx - 1])
    return True


def _update_control(group, control, value):
    control_name = CONTROL_REMAP.get(control)
    if not control_name:
        return
    if control_name in HYBRID_CONTROLS:
        _hybrid_outputs(group, control_name, value)
        return
    d = _ensure_memory()
    if not d:
        return
    for slot in _active_slots(group):
        _, row = _memory_row(group, slot, control_name)
        if row is None:
            continue
        stored = _memory_value(group, slot, control_name)
        try:
            prev_diff = float(d[row, 6].val)
        except Exception:
            prev_diff = value - stored
        diff = value - stored
        attached = d[row, 5].val == '1'
        crossed = (prev_diff <= 0 <= diff) or (prev_diff >= 0 >= diff)
        if (not attached) and (abs(diff) <= PICKUP_THRESHOLD or crossed):
            d[row, 5] = '1'
            attached = True
        d[row, 6] = str(diff)
        if attached:
            d[row, 4] = _format_number(value)


def _refresh_overview():
    core = op('/project1/Instrument_Control_Core/current_values_all_core')
    env = {'op': op, 'me': core}
    exec(core.text, env)
    env['refresh']()

def _refresh_leds(full=False):
    render = op('/project1/channel_selector/vcm600_leds/render_core')
    if not render:
        return
    render.module.render(bool(full))


def _refresh_outputs(group=None):
    if group is None:
        for i in range(1,7):
            op('/project1/Instrument_Control_Core/mapped_midi_{}'.format(i)).cook(force=True)
    else:
        op('/project1/Instrument_Control_Core/mapped_midi_{}'.format(group)).cook(force=True)
    _refresh_overview()


def onValueChange(channel, sampleIndex, val, prev):
    if val == prev:
        return
    _ensure_memory()
    _ensure_hybrid()
    group, control, topic, meta = _name_to_parts(channel.name)
    if not group:
        return
    value = float(val)
    if control in SELECTOR_BUTTONS and value > 0:
        selection = _selection_for_topic(topic)
        if selection:
            slot = int(selection.split('.')[-1])
            if _selector_active(group, slot) == '1':
                _write_fx_grid_snapshot(group, slot)
        event_in = op('/project1/channel_selector/selector_logic/event_in')
        if event_in:
            event_in.appendRow([
                str(time.time()),
                'vcm600',
                meta['etype'],
                str(group),
                '',
                str(value),
                topic,
                meta['label'],
                'vcm600',
                str(value),
            ])
        core = op('/project1/channel_selector/selector_logic/selector_core')
        changed = False
        if core:
            env = {'op': op, 'me': core, 'time': time}
            exec(core.text, env)
            changed = bool(env['process_latest'](False))
        if changed:
            _refresh_selector_outputs()
            if selection:
                slot = int(selection.split('.')[-1])
                _set_pickup_for_slot(group, slot)
            for control_name in HYBRID_CONTROLS:
                _anchor_hybrid(group, control_name)
            _refresh_overview()
            _refresh_leds(False)
        return
    _update_control(group, control, value)
    _refresh_outputs(group)
    return
