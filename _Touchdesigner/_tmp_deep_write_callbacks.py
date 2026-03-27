FOCUS_STATE_PATH = '/project1/Instrument_Control_Core/focus_in'
SELECTOR_STATE_PATH = '/project1/Instrument_Control_Core/selector_in'
WRITE_STATE_PATH = '/project1/Instrument_Control_Core/deep_write_state'
DEEP_SOURCE_PATH = '/project1/Instrument_Control_Core/in7'


def _focus_value(key, default=''):
    table = op(FOCUS_STATE_PATH)
    if not table or table.numRows < 2:
        return default
    for row in range(1, table.numRows):
        if table[row, 0].val == key:
            return table[row, 1].val or default
    return default


def _active_slots():
    table = op(SELECTOR_STATE_PATH)
    active = []
    if not table or table.numRows < 2:
        return active
    for row in range(1, table.numRows):
        slot = table[row, 0].val
        state = table[row, 1].val if table.numCols > 1 else '0'
        if state == '1':
            active.append(slot)
    return active


def _set_write_state(rows):
    table = op(WRITE_STATE_PATH)
    if not table:
        return
    table.clear()
    table.appendRow(['field', 'value'])
    for key, value in rows:
        table.appendRow([str(key), str(value)])


def _deep_ready():
    src = op(DEEP_SOURCE_PATH)
    return bool(src) and getattr(src, 'numChans', 0) > 0


def refresh():
    focus_slot = _focus_value('focus_slot', '')
    focus_control = _focus_value('focus_control', '')
    focus_ch = _focus_value('focus_ch', '')
    active_slots = _active_slots()
    if not focus_slot or not focus_control:
        _set_write_state([
            ('channel', focus_ch or '-'),
            ('focus', focus_control or '-'),
            ('write_status', 'waiting_focus'),
            ('targets_written', 0),
            ('target_paths', '-'),
        ])
        return

    if not active_slots:
        _set_write_state([
            ('channel', focus_ch or '-'),
            ('focus', focus_control),
            ('write_status', 'waiting_targets'),
            ('targets_written', 0),
            ('target_paths', '-'),
        ])
        return

    if not _deep_ready():
        _set_write_state([
            ('channel', focus_ch or '-'),
            ('focus', focus_control),
            ('write_status', 'waiting_deep_source'),
            ('targets_written', 0),
            ('target_paths', ', '.join(active_slots)),
        ])
        return

    _set_write_state([
        ('channel', focus_ch or '-'),
        ('focus', focus_control),
        ('write_status', 'ready'),
        ('targets_written', len(active_slots)),
        ('target_paths', ', '.join(active_slots)),
    ])
