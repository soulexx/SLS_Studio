import time

MAP_PATH = me.parent().path + '/focus_map'
STATE_PATH = me.parent().path + '/focus_state'
READOUT_PATH = me.parent().path + '/focus_readout'

def _state_table(): return op(STATE_PATH)
def _readout_table(): return op(READOUT_PATH)
def _headers(table): return {table[0, c].val: c for c in range(table.numCols)}

def _set_state(key, value):
    table = _state_table()
    for r in range(1, table.numRows):
        if table[r, 0].val == key:
            table[r, 1] = str(value)
            return
    table.appendRow([str(key), str(value)])

def _source_to_focus(source_control):
    table = op(MAP_PATH)
    h = _headers(table)
    for r in range(1, table.numRows):
        if table[r, h['source_control']].val == source_control:
            return {'focus_control': table[r, h['focus_control']].val, 'bank_id': table[r, h['bank_id']].val}
    return None

def update_from_channel(channel_name, value):
    mapping = _source_to_focus(channel_name)
    if not mapping:
        return False
    _set_state('last_focus_control', mapping['focus_control'])
    _set_state('last_source_channel', channel_name)
    _set_state('last_value', value)
    _set_state('last_update', '{:.3f}'.format(time.time()))
    out = _readout_table()
    out.clear()
    out.appendRow(['field', 'value'])
    out.appendRow(['focus', mapping['focus_control']])
    out.appendRow(['bank_id', mapping['bank_id']])
    out.appendRow(['source', channel_name])
    return True
