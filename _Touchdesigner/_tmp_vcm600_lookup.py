# vcm600_lookup
#
# Reusable lookup helper for the VCM-600.

import time


def _headers(table):
    return {table[0, c].val: c for c in range(table.numCols)}


def find_vcm600_topic(etype, ch, idx):
    table = op('/project1/devices/vcm600/vcm600_map')
    if not table or table.numRows < 2:
        return None
    headers = _headers(table)
    for r in range(1, table.numRows):
        row_etype = table[r, headers['etype']].val.strip()
        row_ch = table[r, headers['ch']].val.strip()
        row_idx = table[r, headers['idx']].val.strip()
        if row_etype != str(etype):
            continue
        if row_ch not in (str(ch), '*'):
            continue
        if row_idx != str(idx):
            continue
        return {
            'topic': table[r, headers['topic']].val,
            'label': table[r, headers['label']].val,
            'group': table[r, headers['group']].val,
            'page': table[r, headers['page']].val,
            'led_target': table[r, headers['led_target']].val,
            'notes': table[r, headers['notes']].val,
        }
    return None


def write_debug_result(message, channel, index, value, match):
    out = op('/project1/devices/vcm600/vcm600_debug')
    out.clear()
    out.appendRow(['field', 'value'])
    out.appendRow(['message', str(message)])
    out.appendRow(['channel', str(channel)])
    out.appendRow(['index', str(index)])
    out.appendRow(['value', str(value)])
    if match:
        out.appendRow(['topic', match['topic']])
        out.appendRow(['label', match['label']])
        out.appendRow(['group', match['group']])
        out.appendRow(['page', match['page']])
        out.appendRow(['led_target', match['led_target']])
    else:
        out.appendRow(['topic', 'NO_MATCH'])


def write_last_match(message, channel, index, value, etype, match):
    out = op('/project1/devices/vcm600/vcm600_last_match')
    out.clear()
    out.appendRow(['field', 'value'])
    out.appendRow(['etype', etype])
    out.appendRow(['message', str(message)])
    out.appendRow(['channel', str(channel)])
    out.appendRow(['index', str(index)])
    out.appendRow(['value', str(value)])
    if match:
        out.appendRow(['topic', match['topic']])
        out.appendRow(['label', match['label']])
        out.appendRow(['group', match['group']])
        out.appendRow(['page', match['page']])
    else:
        out.appendRow(['topic', 'NO_MATCH'])


def append_bus_event(src, etype, channel, index, value, match):
    table = op('/project1/devices/vcm600/vcm600_bus_events')
    if table.numRows == 0:
        table.appendRow(['ts', 'src', 'etype', 'ch', 'idx', 'val', 'topic', 'label'])
    topic = match['topic'] if match else 'NO_MATCH'
    label = match['label'] if match else ''
    table.appendRow([str(round(time.time(), 3)), src, etype, str(channel), str(index), str(value), topic, label])
    while table.numRows > 41:
        table.deleteRow(1)
