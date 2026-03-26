LOOKUP_PATH = '/project1/vcm600/vcm600_lookup'
CURRENT_BUS_EVENT_PATH = '/project1/vcm600/current_bus_event'
OWNER_PATH = '/project1/vcm600'

# Cache: lookup module wird einmalig geparsed, nicht bei jedem MIDI-Event
_lookup_env = None


def _get_lookup_env():
    global _lookup_env
    if _lookup_env is None:
        lookup = op(LOOKUP_PATH)
        source = lookup.text if lookup and hasattr(lookup, 'text') else ''
        env = {'op': op}
        exec(source, env)
        _lookup_env = env
    return _lookup_env


def _normalize_index(index):
    try:
        return max(0, int(index) - 1)
    except Exception:
        return 0


def _normalize_value(etype, value):
    try:
        raw = float(value)
    except Exception:
        raw = 0.0
    if etype == 'note':
        return 1.0 if raw > 0.0 else 0.0
    if etype == 'cc':
        return max(0.0, min(1.0, raw / 127.0))
    return max(0.0, min(1.0, raw))


def _fmt_value(value):
    try:
        return '{:.3f}'.format(float(value))
    except Exception:
        return '0.000'


def _set_current_bus_event(topic, etype, channel, index, value, label):
    table = op(CURRENT_BUS_EVENT_PATH)
    owner = op(OWNER_PATH)
    if not table or not owner:
        return

    event_id = int(owner.fetch('event_id', 0)) + 1
    owner.store('event_id', event_id)

    name = ''
    parts = str(topic).split('/')
    if parts:
        name = parts[-1]

    # event_id wird ZULETZT geschrieben â€” erst wenn alle Daten stehen,
    # triggert vcm_in_sync via event_id-Aenderung write_exec.refresh()
    data_rows = [
        (0, 'field',   'value'),
        (2, 'name',    name),
        (3, 'value',   _fmt_value(value)),
        (4, 'etype',   str(etype)),
        (5, 'channel', str(channel)),
        (6, 'index',   str(index)),
        (7, 'topic',   str(topic)),
        (8, 'label',   str(label)),
    ]
    if table.numRows == 9 and table.numCols == 2:
        for r, f, v in data_rows:
            table[r, 1] = v
        # event_id zuletzt â€” loest downstream dedup aus
        table[1, 1] = str(event_id)
    else:
        rows = [
            ['field', 'value'],
            ['event_id', str(event_id)],
            ['name', name],
            ['value', _fmt_value(value)],
            ['etype', str(etype)],
            ['channel', str(channel)],
            ['index', str(index)],
            ['topic', str(topic)],
            ['label', str(label)],
        ]
        table.clear()
        for row in rows:
            table.appendRow(row)


def onReceiveMIDI(dat, rowIndex, message, channel, index, value, input, bytes):
    msg = str(message).strip()
    if msg in ('Note On', 'Note Off'):
        etype = 'note'
    elif msg == 'Control Change':
        etype = 'cc'
    else:
        return

    env = _get_lookup_env()
    mapped_index = _normalize_index(index)
    match = env['find_vcm600_topic'](etype, str(channel), str(mapped_index))
    if not isinstance(match, dict):
        return

    topic = match.get('topic', '')
    label = match.get('label', '')
    norm = _normalize_value(etype, value)

    if etype == 'note':
        # Note-Events: Bus updaten (channel_selector, focus_context etc.)
        _set_current_bus_event(topic, etype, channel, mapped_index, norm, label)
        # Direkt channel_selector aufrufen — bypasses inDAT single-value loss
        _eid = str(op(OWNER_PATH).fetch('event_id', 0))
        try:
            op('/project1/channel_selector/event_in_exec').module.process(
                topic, norm, _eid)
        except Exception:
            pass

    # CC + Note: write_exec direkt (umgeht inDAT-Latenz bei multi-fader)
    try:
        op('/project1/active_instruments_logic/write_exec').module.refresh({
            'topic': str(topic),
            'value': str(norm),
        })
    except Exception as e:
        pass
