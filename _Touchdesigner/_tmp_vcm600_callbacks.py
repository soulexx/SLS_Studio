# vcm600_callbacks
#
# Called by vcm600_in on each MIDI message.
# It translates the message into a VCM-600 topic and writes the result to
# visible tables.


def _load_lookup_helpers():
    env = {'op': op}
    exec(op('/project1/devices/vcm600/vcm600_lookup').text, env)
    return env


def _normalize_index(index):
    # The VCM-600 input arrives offset by +1 in TD for this device.
    # Normalize once here so input and LED output stay 1:1 against the maps.
    try:
        return max(0, int(index) - 1)
    except Exception:
        return index


def _normalize_value_for_bus(etype, value):
    try:
        v = float(value)
    except:
        return 0
    if etype == 'note':
        return 1 if v > 0 else 0
    if etype == 'cc':
        return round(max(0.0, min(1.0, v / 127.0)), 3)
    return round(v, 3)


def onReceiveMIDI(dat, rowIndex, message, channel, index, value, input, bytes):
    env = _load_lookup_helpers()
    msg = str(message).strip()
    if msg in ('Note On', 'Note Off'):
        etype = 'note'
    elif msg == 'Control Change':
        etype = 'cc'
    else:
        etype = 'other'
        match = None
        env['write_debug_result'](msg, channel, index, value, match)
        env['write_last_match'](msg, channel, index, value, etype, match)
        env['append_bus_event']('vcm600', etype, channel, index, value, match)
        return

    mapped_index = _normalize_index(index)
    match = env['find_vcm600_topic'](etype, str(channel), str(mapped_index))
    env['write_debug_result'](msg, channel, mapped_index, value, match)
    env['write_last_match'](msg, channel, mapped_index, value, etype, match)
    env['append_bus_event']('vcm600', etype, channel, mapped_index, value, match)
    topic = match.get('topic', '') if isinstance(match, dict) else ''
    label = match.get('label', '') if isinstance(match, dict) else ''
    group = match.get('group', '') if isinstance(match, dict) else ''
    bus_env = {'op': op, 'me': op('/project1/eventbus/bus_api')}
    exec(op('/project1/eventbus/bus_api').text, bus_env)
    norm_value = _normalize_value_for_bus(etype, value)
    bus_env['append_event']('vcm600', etype, channel, index, norm_value, topic, label, group)
    return
