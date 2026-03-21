import time

MAP_PATH = me.parent().path + '/focus_map'
STATE_PATH = me.parent().path + '/focus_state'
READOUT_PATH = me.parent().path + '/focus_readout'
SOURCE_TEMPLATE = '/project1/channel_selector/out{}'
CONTROL_NAMES = ['hi_eq','mid_eq','low_eq','pan','send_a','send_b','resonance','frequency','hi','mid','low','mute','solo','cf_asn','clip','track','stop','play']
EPSILON = 1e-6


def _state_table():
    return op(STATE_PATH)


def _readout_table():
    return op(READOUT_PATH)


def _headers(table):
    return {table[0, c].val: c for c in range(table.numCols)} if table and table.numRows else {}


def _set_state(key, value):
    table = _state_table()
    for r in range(1, table.numRows):
        if table[r, 0].val == key:
            table[r, 1] = str(value)
            return
    table.appendRow([str(key), str(value)])


def _get_state(key, default=''):
    table = _state_table()
    for r in range(1, table.numRows):
        if table[r, 0].val == key:
            return table[r, 1].val
    return default


def _source_to_focus(source_control):
    table = op(MAP_PATH)
    h = _headers(table)
    for r in range(1, table.numRows):
        if table[r, h['source_control']].val == source_control:
            return {
                'focus_control': table[r, h['focus_control']].val,
                'bank_id': table[r, h['bank_id']].val,
            }
    return None


def _write_readout(focus_control, bank_id, group, source_channel, last_value):
    out = _readout_table()
    out.clear()
    out.appendRow(['field', 'value'])
    out.appendRow(['group', group])
    out.appendRow(['focus', focus_control or '-'])
    out.appendRow(['bank_id', bank_id])
    out.appendRow(['source', source_channel or '-'])
    out.appendRow(['last_value', '{:.3f}'.format(float(last_value) if last_value not in ('', None) else 0.0)])


def _scan_latest_change():
    prev = me.parent().fetch('prev_values', {})
    current = {}
    best = None
    best_delta = -1.0
    for group in range(1, 7):
        src = op(SOURCE_TEMPLATE.format(group))
        if not src:
            continue
        src.cook(force=True)
        for control in CONTROL_NAMES:
            ch = src.chan(control)
            try:
                val = float(ch[0]) if ch else 0.0
            except Exception:
                val = 0.0
            key = '{}:{}'.format(group, control)
            current[key] = val
            if key in prev:
                delta = abs(val - prev[key])
                if delta > EPSILON and delta >= best_delta:
                    best_delta = delta
                    best = (group, control, val)
    me.parent().store('prev_values', current)
    return best


def _update_from_scan():
    hit = _scan_latest_change()
    if not hit:
        return
    group, control, value = hit
    mapping = _source_to_focus(control)
    _set_state('last_focus_group', group)
    _set_state('last_source_channel', control)
    _set_state('last_value', value)
    _set_state('last_update', '{:.3f}'.format(time.time()))
    if mapping:
        _set_state('last_focus_control', mapping['focus_control'])
        _set_state('focus_group_{}'.format(group), mapping['focus_control'])
        return
    existing_group_focus = _get_state('focus_group_{}'.format(group), '')
    if existing_group_focus:
        _set_state('last_focus_control', existing_group_focus)


def onCook(scriptOp):
    _update_from_scan()
    fmap = op(MAP_PATH)
    scriptOp.clear()
    last_focus = _get_state('last_focus_control', '')
    last_group = int(float(_get_state('last_focus_group', '0') or 0))
    if last_focus and last_group <= 0:
        last_group = 1
        _set_state('last_focus_group', 1)
    bank_id = 0
    h = _headers(fmap)
    for r in range(1, fmap.numRows):
        focus_control = fmap[r, h['focus_control']].val
        ch = scriptOp.appendChan('focus_' + focus_control)
        active = 1.0 if focus_control == last_focus else 0.0
        ch.vals = [active]
        if active > 0:
            bank_id = int(fmap[r, h['bank_id']].val or 0)
    ch = scriptOp.appendChan('focus_valid')
    ch.vals = [1.0 if last_focus and last_group > 0 else 0.0]
    ch = scriptOp.appendChan('focus_bank_id')
    ch.vals = [float(bank_id)]
    ch = scriptOp.appendChan('focus_group')
    ch.vals = [float(last_group)]
    _write_readout(last_focus, bank_id, last_group, _get_state('last_source_channel', ''), _get_state('last_value', '0'))


def onGetCookLevel(scriptOp):
    return CookLevel.ALWAYS
