MEMORY_PATH = '/project1/Instrument_Control_Core/channel_value_memory'
FX_GRID_MEMORY_PATH = '/project1/Instrument_Control_Core/fx_grid_memory'
SELECTOR_PATH = '/project1/channel_selector/channel_selector_state'
OUT_PATH = '/project1/Instrument_Control_Core/current_values_all'
DEEP_STATE_PATH = '/project1/Instrument_Control_Core/deep_state'
FOCUS_STATE_PATH = '/project1/Instrument_Control_Core/focus_router/focus_state'
FX_GRID_PATH = '/project1/Instrument_Control_Core/fx_grid_router/fx_grid_out'
CONTROL_ORDER = ['hi_eq','mid_eq','low_eq','pan','send_a','send_b','resonance','frequency','hi','mid','low','mute','solo','cf_asn','clip','track','stop','play']
FX_GRID_ORDER = [
    ('vcm600_global_fx_grid_1_1', 'fx_grid_1'),
    ('vcm600_global_fx_grid_1_2', 'fx_grid_2'),
    ('vcm600_global_fx_grid_1_3', 'fx_grid_3'),
    ('vcm600_global_fx_grid_1_4', 'fx_grid_4'),
    ('vcm600_global_fx_grid_2_1', 'fx_grid_5'),
    ('vcm600_global_fx_grid_2_2', 'fx_grid_6'),
    ('vcm600_global_fx_grid_2_3', 'fx_grid_7'),
    ('vcm600_global_fx_grid_2_4', 'fx_grid_8'),
]
HEADER = ['control', 'live_1', '1.1', '1.2', '1.3', 'live_2', '2.1', '2.2', '2.3', 'live_3', '3.1', '3.2', '3.3', 'live_4', '4.1', '4.2', '4.3', 'live_5', '5.1', '5.2', '5.3', 'live_6', '6.1', '6.2', '6.3']
EMPTY_CELLS = [''] * (len(HEADER) - 2)


def _format_value(v):
    try:
        v = float(v)
    except Exception:
        return str(v)
    if abs(v - round(v)) < 1e-6:
        return str(int(round(v)))
    return '{:.3f}'.format(v)


def _selector_active(group, slot):
    d = op(SELECTOR_PATH)
    if not d:
        return '0'
    key = 'track_{}.{}'.format(group, slot)
    for row in range(1, d.numRows):
        if d[row, 0].val == key:
            return '1' if d[row, 1].val == '1' else '0'
    return '0'


def _memory_value(group, slot, control):
    d = op(MEMORY_PATH)
    if not d:
        return '0'
    key = '{}.{}'.format(group, slot)
    for row in range(1, d.numRows):
        if d[row, 0].val == key and d[row, 3].val == control:
            val = d[row, 4].val
            if d[row, 5].val != '1':
                return val + ' p'
            return val
    return '0'


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


def _fx_grid_memory_value(group, slot, label):
    table = _ensure_fx_grid_memory()
    if not table:
        return '0'
    col = None
    for c in range(table.numCols):
        if table[0, c].val == label:
            col = c
            break
    if col is None:
        return '0'
    for row in range(1, table.numRows):
        if table[row, 1].val == str(group) and table[row, 2].val == str(slot):
            return table[row, col].val or '0'
    return '0'


def _live_value(group, control):
    src = op('/project1/Instrument_Control_Core/in{}'.format(group))
    ch = src.chan(control) if src else None
    if ch is None:
        return '0'
    try:
        return _format_value(float(ch[0]))
    except Exception:
        return '0'


def _deep_state_value(key, default='-'):
    d = op(DEEP_STATE_PATH)
    if not d:
        return default
    for row in range(1, d.numRows):
        if d[row, 0].val == key:
            return d[row, 1].val or default
    return default


def _focus_state_value(key, default='-'):
    d = op(FOCUS_STATE_PATH)
    if not d:
        return default
    for row in range(1, d.numRows):
        if d[row, 0].val == key:
            return d[row, 1].val or default
    return default


def _fx_grid_value(name):
    src = op(FX_GRID_PATH)
    ch = src.chan(name) if src else None
    if ch is None:
        return '0'
    try:
        return _format_value(float(ch[0]))
    except Exception:
        return '0'


def _summary_row(label, value):
    return [label, str(value)] + list(EMPTY_CELLS)


def _focus_channel_row():
    focus_group = int(float(_deep_state_value('focus_group', '0') or 0))
    row = ['focus_channel']
    for group in range(1, 7):
        row.append(str(group) if group == focus_group and focus_group > 0 else '')
        row.extend(['', '', ''])
    return row


def _active_slots_summary(group):
    active = [str(slot) for slot in range(1, 4) if _selector_active(group, slot) == '1']
    return ','.join(active) if active else '-'


def _active_slots_row():
    row = ['active_slots']
    for group in range(1, 7):
        row.append(_active_slots_summary(group))
        row.extend(['', '', ''])
    return row


def _focus_control_row():
    row = ['focus_control']
    for group in range(1, 7):
        row.append(_focus_state_value('focus_group_{}'.format(group), '-'))
        row.extend(['', '', ''])
    return row


def _fx_grid_row(label, source_name):
    focus_group = int(float(_deep_state_value('focus_group', '0') or 0))
    fx_value = _fx_grid_value(source_name)
    row = [label]
    for group in range(1, 7):
        row.append(fx_value if group == focus_group else '')
        for slot in range(1, 4):
            row.append(_fx_grid_memory_value(group, slot, label))
    return row


def refresh():
    out = op(OUT_PATH)
    if not out:
        return
    out.clear()
    out.appendRow(HEADER)
    out.appendRow(_focus_channel_row())
    out.appendRow(_focus_control_row())
    out.appendRow(_summary_row('page_index', _deep_state_value('page_index', '0')))
    out.appendRow(_active_slots_row())
    out.appendRow(_summary_row('deep_valid', _deep_state_value('focus_valid', '0')))
    active_row = ['active']
    for group in range(1,7):
        active_row.append('')
        active_row.extend([_selector_active(group, 1), _selector_active(group, 2), _selector_active(group, 3)])
    out.appendRow(active_row)
    for control in CONTROL_ORDER:
        row = [control]
        for group in range(1,7):
            row.append(_live_value(group, control))
            row.extend([_memory_value(group, 1, control), _memory_value(group, 2, control), _memory_value(group, 3, control)])
        out.appendRow(row)
    for source_name, label in FX_GRID_ORDER:
        out.appendRow(_fx_grid_row(label, source_name))


def onFrameEnd(frame):
    refresh()
    return
