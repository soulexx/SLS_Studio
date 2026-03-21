STATE_PATH = '/project1/Instrument_Control_Core/deep_state'
BUS_PATH = '/project1/Instrument_Control_Core/deep_bus'
WRITE_STATE_PATH = '/project1/Instrument_Control_Core/deep_write_state'
FX_GRID_MEMORY_PATH = '/project1/Instrument_Control_Core/fx_grid_memory'
FX_GRID_HYBRID_STATE_PATH = '/project1/Instrument_Control_Core/fx_grid_hybrid_state'
GUMMIBAND_CORE_PATH = '/project1/gummiband_master/gummiband_core'
EPSILON = 0.0001


def _state_value(key, default=''):
    table = op(STATE_PATH)
    if not table:
        return default
    for r in range(1, table.numRows):
        if table[r, 0].val == key:
            return table[r, 1].val or default
    return default


def _bus_values():
    src = op(BUS_PATH)
    values = {}
    if not src:
        return values
    src.cook(force=True)
    for ch in src.chans():
        try:
            values[ch.name] = float(ch[0])
        except Exception:
            values[ch.name] = 0.0
    return values


def _active_slots():
    raw = _state_value('active_slots', '')
    if not raw or raw == '-':
        return []
    out = []
    for part in raw.split(','):
        part = part.strip()
        if not part:
            continue
        try:
            out.append(int(part))
        except Exception:
            pass
    return out


def _target(group, slot):
    return op('/project1/bitwigRemotesTrack{}_{}'.format(group, slot))


def _format_number(value):
    try:
        value = float(value)
    except Exception:
        return str(value)
    if abs(value - round(value)) < 1e-6:
        return str(int(round(value)))
    return '{:.3f}'.format(value)


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
        return 0.0
    col = None
    for c in range(table.numCols):
        if table[0, c].val == label:
            col = c
            break
    if col is None:
        return 0.0
    for row in range(1, table.numRows):
        if table[row, 1].val == str(group) and table[row, 2].val == str(slot):
            try:
                return float(table[row, col].val)
            except Exception:
                return 0.0
    return 0.0


def _write_fx_grid_memory(group, slot, deep_values):
    table = _ensure_fx_grid_memory()
    if not table:
        return
    for row in range(1, table.numRows):
        if table[row, 1].val == str(group) and table[row, 2].val == str(slot):
            for offset, value in enumerate(deep_values, start=3):
                table[row, offset] = str(value)
            return


def _ensure_fx_grid_hybrid_state():
    table = op(FX_GRID_HYBRID_STATE_PATH)
    if not table:
        return None
    header = ['group', 'control', 'mask', 'last_live', 'base_1', 'base_2', 'base_3', 'out_1', 'out_2', 'out_3', 'epsilon']
    if table.numRows == 0:
        table.appendRow(header)
    elif table.numCols != len(header) or any(table[0, i].val != header[i] for i in range(len(header))):
        table.clear()
        table.appendRow(header)
    existing = set()
    for row in range(1, table.numRows):
        existing.add((table[row, 0].val, table[row, 1].val))
    for group in range(1, 7):
        for idx in range(1, 9):
            label = 'fx_grid_{}'.format(idx)
            if (str(group), label) not in existing:
                table.appendRow([str(group), label, '000', '0', '0', '0', '0', '0', '0', '0', str(EPSILON)])
    return table


def _fx_grid_hybrid_row(group, label):
    table = _ensure_fx_grid_hybrid_state()
    if not table:
        return None, None
    for row in range(1, table.numRows):
        if table[row, 0].val == str(group) and table[row, 1].val == label:
            return table, row
    return table, None


def _apply_gummiband(bases, active, start_fader, fader):
    core = op(GUMMIBAND_CORE_PATH)
    if not core:
        return list(bases)
    env = {'op': op, 'me': core}
    exec(core.text, env)
    return env['apply_motion'](bases, active, start_fader, fader, EPSILON)


def _anchor_fx_grid(group, label, live, active_slots):
    table, row = _fx_grid_hybrid_row(group, label)
    if table is None or row is None:
        return
    mask = ''.join('1' if slot in active_slots else '0' for slot in (1, 2, 3))
    table[row, 2] = mask
    table[row, 3] = _format_number(live)
    for slot in (1, 2, 3):
        base = _fx_grid_memory_value(group, slot, label)
        table[row, 3 + slot] = _format_number(base)
        table[row, 6 + slot] = _format_number(base)
    table[row, 10] = str(EPSILON)


def _fx_grid_outputs(group, label, live, active_slots):
    table, row = _fx_grid_hybrid_row(group, label)
    if table is None or row is None:
        return [0.0, 0.0, 0.0]
    mask = ''.join('1' if slot in active_slots else '0' for slot in (1, 2, 3))
    if table[row, 2].val != mask:
        _anchor_fx_grid(group, label, live, active_slots)
    bases = []
    for slot in (1, 2, 3):
        try:
            bases.append(float(table[row, 3 + slot].val or 0.0))
        except Exception:
            bases.append(0.0)
    try:
        start_fader = float(table[row, 3].val or 0.0)
    except Exception:
        start_fader = live
    if len(active_slots) == 1:
        outs = list(bases)
        outs[active_slots[0] - 1] = max(0.0, min(1.0, float(live)))
    else:
        outs = _apply_gummiband(bases, active_slots, start_fader, live)
    table[row, 2] = mask
    for slot in (1, 2, 3):
        table[row, 6 + slot] = _format_number(outs[slot - 1])
    return outs


def _safe_page_index(target, requested):
    try:
        names = list(target.ext.BitwigRemotesTrackExt.PageNames or [])
    except Exception:
        names = []
    if not names:
        return 0
    requested = max(0, int(requested))
    return min(requested, len(names) - 1)


CORE_PATH = '/project1/Instrument_Control_Core'

def _set_write_state(rows):
    table = op(WRITE_STATE_PATH)
    table.clear()
    table.appendRow(['field', 'value'])
    for key, value in rows:
        table.appendRow([str(key), str(value)])


def refresh():
    values = _bus_values()
    focus_group = int(float(_state_value('focus_group', '0') or 0))
    focus_valid = int(float(_state_value('focus_valid', '0') or 0) > 0.5)
    focus_control = _state_value('focus_control', '-')
    requested_page = int(float(_state_value('page_index', '0') or 0))
    slots = _active_slots()
    raw_deep_values = tuple(round(values.get('deep_{}'.format(i), 0.0), 6) for i in range(1, 9))
    if focus_group <= 0 or not focus_valid or not slots:
        op(CORE_PATH).store('last_write_sig', None)
        _set_write_state([('group', focus_group), ('focus', focus_control), ('write_status', 'idle'), ('targets_written', 0), ('target_paths', '-')])
        return
    per_slot_values = {slot: [] for slot in slots}
    for idx, live in enumerate(raw_deep_values, start=1):
        label = 'fx_grid_{}'.format(idx)
        outs = _fx_grid_outputs(focus_group, label, live, slots)
        for slot in slots:
            per_slot_values[slot].append(round(outs[slot - 1], 6))
    page_indices = []
    target_paths = []
    for slot in slots:
        t = _target(focus_group, slot)
        if not t:
            continue
        target_paths.append(t.path)
        page_indices.append(_safe_page_index(t, requested_page))
    sig = (focus_group, tuple(slots), tuple(page_indices), tuple((slot, tuple(per_slot_values[slot])) for slot in sorted(per_slot_values)))
    if op(CORE_PATH).fetch('last_write_sig', None) == sig:
        _set_write_state([('group', focus_group), ('focus', focus_control), ('write_status', 'held'), ('targets_written', len(target_paths)), ('target_paths', ', '.join(target_paths) if target_paths else '-')])
        return
    written = 0
    for slot in slots:
        t = _target(focus_group, slot)
        if not t:
            continue
        safe_page = _safe_page_index(t, requested_page)
        try:
            if t.par.Remotecontrolpage.menuIndex != safe_page:
                t.par.Remotecontrolpage.menuIndex = safe_page
        except Exception:
            pass
        for i in range(8):
            par = t.par['Remotecontrol{}'.format(i)]
            if par is not None:
                par.val = per_slot_values[slot][i]
        _write_fx_grid_memory(focus_group, slot, per_slot_values[slot])
        written += 1
    op(CORE_PATH).store('last_write_sig', sig)
    _set_write_state([('group', focus_group), ('focus', focus_control), ('write_status', 'active'), ('targets_written', written), ('target_paths', ', '.join(target_paths) if target_paths else '-')])
