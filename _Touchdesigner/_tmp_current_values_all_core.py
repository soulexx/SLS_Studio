MEMORY_PATH = '/project1/project_memory/channel_value_memory'
FX_GRID_MEMORY_PATH = '/project1/project_memory/fx_grid_memory'
FX_GRID_CONTROL_MEMORY_PATH = '/project1/project_memory/fx_grid_control_memory'
SELECTOR_STATE_PATH = '/project1/Instrument_Control_Core/selector_in'
FOCUS_STATE_PATH = '/project1/Instrument_Control_Core/focus_in'
VCM_EVENT_PATH = '/project1/Instrument_Control_Core/vcm_in'
OUT_PATH = '/project1/Instrument_Control_Core/current_values_all'
MAIN_PATH = '/project1/Instrument_Control_Core/current_values_main'
FX_GRID_PATH = '/project1/Instrument_Control_Core/current_values_fx_grid'
FX_GRID_CONTROL_PATH = '/project1/Instrument_Control_Core/current_values_fx_grid_by_control'

CONTROL_ORDER = [
    'eq_hi', 'eq_mid', 'eq_low', 'pan', 'send_a', 'send_b', 'resonance', 'frequency',
    'hi_cut', 'mid_cut', 'low_cut', 'mute', 'solo', 'cf_asn', 'clip', 'track', 'stop', 'play', 'level'
]
FX_GRID_CONTROLS = ['eq_hi', 'eq_mid', 'eq_low', 'pan', 'send_a', 'send_b', 'resonance', 'frequency']
FX_GRID_LABELS = ['fx_grid_{}'.format(i) for i in range(1, 9)]
HEADER = [
    'control',
    'live_1', '1.1', '1.2', '1.3',
    'live_2', '2.1', '2.2', '2.3',
    'live_3', '3.1', '3.2', '3.3',
    'live_4', '4.1', '4.2', '4.3',
    'live_5', '5.1', '5.2', '5.3',
    'live_6', '6.1', '6.2', '6.3',
]
EMPTY_CELLS = [''] * (len(HEADER) - 2)
PAGE_BY_CONTROL = {
    'eq_hi': 0,
    'eq_mid': 1,
    'eq_low': 2,
    'pan': 3,
    'send_a': 4,
    'send_b': 5,
    'resonance': 6,
    'frequency': 7,
}
SUMMARY_ROWS = {'focus_channel', 'focus_control', 'page_index', 'active_slots', 'deep_valid', 'active'}


def _format_value(value):
    try:
        number = float(value)
    except Exception:
        return str(value)
    if abs(number - round(number)) < 1e-6:
        return str(int(round(number)))
    return '{:.3f}'.format(number)


def _table_dict(dat):
    values = {}
    if not dat or dat.numRows < 2:
        return values
    for row in range(1, dat.numRows):
        key = dat[row, 0].val
        if not key:
            continue
        values[key] = dat[row, 1].val if dat.numCols > 1 else ''
    return values


def _selector_state():
    active = set()
    dat = op(SELECTOR_STATE_PATH)
    if not dat or dat.numRows < 2:
        return active
    for row in range(1, dat.numRows):
        slot = dat[row, 0].val
        state = dat[row, 1].val if dat.numCols > 1 else '0'
        if state == '1':
            active.add(slot)
    return active


def _channel_memory():
    values = {}
    dat = op(MEMORY_PATH)
    if not dat or dat.numRows < 2:
        return values
    for row in range(1, dat.numRows):
        try:
            group = dat[row, 1].val
            sub = dat[row, 2].val
            control = dat[row, 3].val
            value = dat[row, 4].val
        except Exception:
            continue
        values[(group, sub, control)] = value
    return values


def _vcm_event():
    return _table_dict(op(VCM_EVENT_PATH))


def _fx_grid_memory():
    values = {}
    dat = op(FX_GRID_MEMORY_PATH)
    if not dat or dat.numRows < 2:
        return values
    col_map = {dat[0, c].val: c for c in range(dat.numCols)}
    for row in range(1, dat.numRows):
        group = dat[row, col_map['group']].val
        sub = dat[row, col_map['sub']].val
        for label in FX_GRID_LABELS:
            values[(group, sub, label)] = dat[row, col_map[label]].val
    return values


def _fx_grid_control_memory():
    values = {}
    dat = op(FX_GRID_CONTROL_MEMORY_PATH)
    if not dat or dat.numRows < 2:
        return values
    col_map = {dat[0, c].val: c for c in range(dat.numCols)}
    for row in range(1, dat.numRows):
        group = dat[row, col_map['group']].val
        sub = dat[row, col_map['sub']].val
        control = dat[row, col_map['control']].val
        for label in FX_GRID_LABELS:
            values[(group, sub, control, label)] = dat[row, col_map[label]].val
    return values


def _group_slots(group, active_slots):
    return [slot for slot in ('1', '2', '3') if '{}.{}'.format(group, slot) in active_slots]


def _preferred_slot(group, active_slots, focus_slot):
    active_group_slots = _group_slots(group, active_slots)
    if focus_slot and focus_slot.startswith(str(group) + '.') and focus_slot in active_slots:
        return focus_slot.split('.', 1)[1]
    if active_group_slots:
        return active_group_slots[0]
    return '1'


def _summary_row(label, value):
    return [label, str(value)] + list(EMPTY_CELLS)


def _copy_rows(dst, rows):
    if not dst:
        return
    dst.clear()
    for row in rows:
        dst.appendRow(row)


def _existing_live_values(table):
    values = {}
    if not table or table.numRows < 2 or table.numCols < 2:
        return values
    live_cols = {}
    for c in range(table.numCols):
        header = table[0, c].val
        if header.startswith('live_'):
            live_cols[header.replace('live_', '')] = c
    for r in range(1, table.numRows):
        control = table[r, 0].val
        if not control:
            continue
        for group, col in live_cols.items():
            values[(group, control)] = table[r, col].val
    return values


def _refresh_views(out):
    if not out or out.numRows == 0:
        return
    rows = [[out[r, c].val for c in range(out.numCols)] for r in range(out.numRows)]
    header = rows[0]
    body = rows[1:]

    main_rows = [header]
    fx_rows = [header]
    fx_control_rows = [header]
    current_control = None

    for row in body:
        label = row[0]
        if not label:
            continue
        if label in SUMMARY_ROWS or label in CONTROL_ORDER:
            main_rows.append(row)
            continue
        if label.startswith('fx_grid_'):
            fx_rows.append(row)
            continue
        if '_fx_grid_' in label:
            control = label.split('_fx_grid_', 1)[0]
            if current_control is not None and control != current_control:
                fx_control_rows.append([''] * len(header))
            if current_control != control:
                fx_control_rows.append(['[{}]'.format(control)] + [''] * (len(header) - 1))
            pretty = list(row)
            pretty[0] = pretty[0].split('_fx_grid_', 1)[1]
            fx_control_rows.append(pretty)
            current_control = control

    _copy_rows(op(MAIN_PATH), main_rows)
    _copy_rows(op(FX_GRID_PATH), fx_rows)
    _copy_rows(op(FX_GRID_CONTROL_PATH), fx_control_rows)


def _focus_channel_row(focus_ch):
    row = ['focus_channel']
    for group in range(1, 7):
        row.append(str(group) if str(group) == focus_ch and focus_ch else '')
        row.extend(['', '', ''])
    return row


def _focus_control_row(focus_ch, focus_control):
    row = ['focus_control']
    for group in range(1, 7):
        row.append(focus_control if str(group) == focus_ch and focus_control else '')
        row.extend(['', '', ''])
    return row


def _active_slots_row(active_slots):
    row = ['active_slots']
    for group in range(1, 7):
        row.append(','.join(_group_slots(group, active_slots)) or '-')
        row.extend(['', '', ''])
    return row


def _active_row(active_slots):
    row = ['active']
    for group in range(1, 7):
        row.append('')
        for sub in ('1', '2', '3'):
            row.append('1' if '{}.{}'.format(group, sub) in active_slots else '0')
    return row


def _control_row(control, active_slots, focus_slot, channel_values, live_values):
    row = [control]
    for group in range(1, 7):
        row.append(live_values.get((str(group), control), '0'))
        for sub in ('1', '2', '3'):
            row.append(channel_values.get((str(group), sub, control), '0'))
    return row


def _fx_grid_row(label, active_slots, focus_slot, fx_values):
    row = [label]
    for group in range(1, 7):
        preferred = _preferred_slot(group, active_slots, focus_slot)
        row.append(fx_values.get((str(group), preferred, label), '0'))
        for sub in ('1', '2', '3'):
            row.append(fx_values.get((str(group), sub, label), '0'))
    return row


def _fx_grid_control_row(control, label, active_slots, focus_slot, fx_control_values):
    row = ['{}_{}'.format(control, label)]
    for group in range(1, 7):
        preferred = _preferred_slot(group, active_slots, focus_slot)
        row.append(fx_control_values.get((str(group), preferred, control, label), '0'))
        for sub in ('1', '2', '3'):
            row.append(fx_control_values.get((str(group), sub, control, label), '0'))
    return row


def refresh():
    out = op(OUT_PATH)
    if not out:
        return

    existing_live_values = _existing_live_values(out)
    focus = _table_dict(op(FOCUS_STATE_PATH))
    active_slots = _selector_state()
    channel_values = _channel_memory()
    live_event = _vcm_event()
    fx_values = _fx_grid_memory()
    fx_control_values = _fx_grid_control_memory()

    focus_slot = focus.get('focus_slot', '')
    focus_control = focus.get('focus_control', '')
    focus_ch = focus.get('focus_ch', '')
    deep_valid = '1' if focus_slot and focus_control else '0'
    page_index = str(PAGE_BY_CONTROL.get(focus_control, 0))
    live_values = dict(existing_live_values)
    live_topic = live_event.get('topic', '')
    live_value = live_event.get('value', '0')
    parts = live_topic.split('/')
    if len(parts) >= 4 and parts[0] == 'vcm600' and parts[1] == 'channel':
        live_group = parts[2]
        live_control = parts[3]
        live_values[(str(live_group), live_control)] = live_value

    out.clear()
    out.appendRow(HEADER)
    out.appendRow(_focus_channel_row(focus_ch))
    out.appendRow(_focus_control_row(focus_ch, focus_control))
    out.appendRow(_summary_row('page_index', page_index))
    out.appendRow(_active_slots_row(active_slots))
    out.appendRow(_summary_row('deep_valid', deep_valid))
    out.appendRow(_active_row(active_slots))

    for control in CONTROL_ORDER:
        out.appendRow(_control_row(control, active_slots, focus_slot, channel_values, live_values))

    for label in FX_GRID_LABELS:
        out.appendRow(_fx_grid_row(label, active_slots, focus_slot, fx_values))

    out.appendRow([''] + list(EMPTY_CELLS))

    for control in FX_GRID_CONTROLS:
        for label in FX_GRID_LABELS:
            out.appendRow(_fx_grid_control_row(control, label, active_slots, focus_slot, fx_control_values))

    _refresh_views(out)
