SELECTOR_PATH      = '/project1/active_instruments_logic/selector_in'
FOCUS_PATH         = '/project1/active_instruments_logic/focus_in'
FOCUS_STATE_PATH   = '/project1/active_instruments_logic/focus_state'
VCM_PATH           = '/project1/active_instruments_logic/vcm_in'
STATE_PATH         = '/project1/active_instruments_logic/write_state'
OUT_PATH           = '/project1/active_instruments_logic/prepared_values'
GUMMIBAND_STATE_PATH = '/project1/gummiband/gummiband_state'
TABLE_PATH         = '/project1/Instrument_Control_Core/current_values_all'
CVA_PATH           = '/project1/Instrument_Control_Core/current_values_all'
VM_PATH            = '/project1/project_memory/value_memory'
MIS_PATH           = '/project1/Instrument_Control_Core/memory_in_sync'
MW_PATH            = '/project1/project_memory/memory_write'


# Remote Controls: eq_hi..frequency -> Remotecontrol0..7
REMOTE_CTRL_MAP = [
    'eq_hi', 'eq_mid', 'eq_low', 'pan', 'send_a', 'send_b', 'resonance', 'frequency'
]
REMOTE_CTRL_IDX = {c: i for i, c in enumerate(REMOTE_CTRL_MAP)}

# fx_grid_1..8 -> bitwigTrackN.Send0..7
FX_GRID_MAP = {'fx_grid_{}'.format(i): i - 1 for i in range(1, 9)}

def _table_dict(dat):
    values = {}
    if not dat or dat.numRows < 2:
        return values
    for row in range(1, dat.numRows):
        key = dat[row, 0].val
        if key:
            values[key] = dat[row, 1].val if dat.numCols > 1 else ''
    return values


def _float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default


_active_slots_cache = None
_active_slots_sig   = None

def _active_slots():
    global _active_slots_cache, _active_slots_sig
    dat = op(SELECTOR_PATH)
    if not dat or dat.numRows < 2:
        return []
    sig = ''.join(dat[r, 1].val for r in range(1, dat.numRows))
    if sig == _active_slots_sig and _active_slots_cache is not None:
        return _active_slots_cache
    active = [dat[r, 0].val for r in range(1, dat.numRows) if dat[r, 1].val == '1']
    _active_slots_cache = active
    _active_slots_sig   = sig
    return active


def _set_state(status, topic='', prepared=''):
    st = op(STATE_PATH)
    rows = [['field','value'],['status',status],['topic',topic],['prepared',prepared]]
    if st.numRows == 4 and st.numCols == 2:
        for r, row in enumerate(rows): st[r,0]=row[0]; st[r,1]=row[1]
    else:
        st.clear()
        for row in rows: st.appendRow(row)


def _fmt(v):
    try:
        return '{:.3f}'.format(round(float(v), 3))
    except Exception:
        return v


def _emit(rows):
    out = op(OUT_PATH)
    all_rows = [['slot','control','value']] + [[slot, control, _fmt(value)] for slot, control, value in rows]
    if out.numRows == len(all_rows) and out.numCols == 3:
        for r, row in enumerate(all_rows):
            out[r, 0] = row[0]; out[r, 1] = row[1]; out[r, 2] = row[2]
    else:
        out.clear()
        for row in all_rows:
            out.appendRow(row)


def _write_direct(rows):
    """Schreibt direkt in CVA + value_memory — bypassed alle inDAT-Grenzen."""
    if not rows:
        return
    try:
        mis     = op(MIS_PATH).module
        mw      = op(MW_PATH).module
        cva     = op(CVA_PATH)
        vm      = op(VM_PATH)
        ctrl_row = getattr(mis, '_control_row_cache', {})
        tgt_col  = getattr(mis, '_target_col_cache', {})
        vm_cache = getattr(mw,  '_cache', {})
        for slot, control, value in rows:
            v_str = '{:.3f}'.format(float(value))
            row = ctrl_row.get(control)
            col = tgt_col.get(slot)
            if row is not None and col is not None:
                if str(cva[row, col]) != v_str:
                    cva[row, col] = v_str
            vm_row = vm_cache.get((slot, control))
            if vm_row is not None:
                if str(vm[vm_row, 2]) != v_str:
                    vm[vm_row, 2] = v_str
    except Exception as e:
        debug('_write_direct error: {}'.format(e))


def _bw_ch_path(group):
    """bitwigRemotesTrack_6 hat fuehrendes _ — alle anderen nicht."""
    if str(group) == '6':
        return '/project1/bitwigRemotesTrack_6'
    return '/project1/bitwigRemotesTrack{}'.format(group)


def _write_bitwig_remotes(rows):
    """Schreibt direkt auf bitwigRemotesTrack*-Parameter."""
    for slot, control, value in rows:
        # Remote Controls (eq_hi..frequency) -> bitwigRemotesTrack
        rc_idx = REMOTE_CTRL_IDX.get(control)
        if rc_idx is not None:
            par_name = 'Remotecontrol{}'.format(rc_idx)
            v = float(value)
            if slot.startswith('CH_'):
                bw = op(_bw_ch_path(slot[3:]))
                if bw: bw.par[par_name].val = v
            elif '.' in slot:
                parts = slot.split('.')
                bw = op('/project1/bitwigRemotesTrack{}_{}'.format(parts[0], parts[1]))
                if bw: bw.par[par_name].val = v
        # FX Grid (fx_grid_1..8) -> bitwigTrack{focus_ch}.Send0..7
        # Nur wenn kein Instrument fuer focus_ch angewaehlt ist
        send_idx = FX_GRID_MAP.get(control)
        if send_idx is not None and slot == 'global':
            fs = op(FOCUS_STATE_PATH)
            focus_ch = ''
            if fs:
                for _r in range(1, fs.numRows):
                    if str(fs[_r, 0]) == 'focus_ch':
                        focus_ch = str(fs[_r, 1])
                        break
            if focus_ch:
                # Slot-Check: kein Instrument aktiv fuer diesen Channel?
                sel = op('/project1/active_instruments_logic/selector_in')
                group_has_slot = sel and any(
                    str(sel[_r, 1]) == '1'
                    for _r in range(1, sel.numRows)
                    if str(sel[_r, 0]).startswith(focus_ch + '.')
                )
                if not group_has_slot:
                    bw = op('/project1/bitwigTrack{}'.format(focus_ch))
                    if bw:
                        bw.par['Send{}'.format(send_idx)].val = float(value)
        # Master Level -> bitwigTrackMaster.Volume (immer)
        if slot == 'global' and control == 'master_level':
            bw = op('/project1/bitwigTrackMaster')
            if bw:
                bw.par.Volume.val = float(value)
            _update_focus('master')

def _update_focus(group):
    """Schreibt focus_ch in focus_state (kanonische Quelle) und
    pulst bitwigTrackN.Makevisibleinmixer nur bei echtem Kanalwechsel."""
    fs = op(FOCUS_STATE_PATH)
    if not fs:
        return
    current = ''
    for r in range(1, fs.numRows):
        if str(fs[r, 0]) == 'focus_ch':
            current = str(fs[r, 1])
            break
    if str(group) == current:
        return
    for r in range(1, fs.numRows):
        if str(fs[r, 0]) == 'focus_ch':
            fs[r, 1] = str(group)
            break
    bw_name = 'bitwigTrackMaster' if str(group) == 'master' else 'bitwigTrack{}'.format(group)
    bw = op('/project1/{}'.format(bw_name))
    if bw:
        bw.par.Makevisibleinmixer.pulse()


def _signature(active_subs):
    return ','.join(sorted(active_subs))


def _ensure_gummiband_row(group, control):
    table = op(GUMMIBAND_STATE_PATH)
    if table.numRows == 0:
        table.appendRow(['group','control','active_signature','start_fader','base_1','base_2','base_3'])
    for row in range(1, table.numRows):
        if table[row,0].val == str(group) and table[row,1].val == str(control):
            return row
    table.appendRow([str(group), str(control), '', '0.0', '0.0', '0.0', '0.0'])
    return table.numRows - 1


def _read_gummiband_row(row):
    table = op(GUMMIBAND_STATE_PATH)
    return {
        'active_signature': table[row,2].val,
        'start_fader':      table[row,3].val,
        'base_1':           table[row,4].val,
        'base_2':           table[row,5].val,
        'base_3':           table[row,6].val,
    }


def _write_gummiband_row(row, signature, start_fader, bases):
    table = op(GUMMIBAND_STATE_PATH)
    table[row,2] = signature
    table[row,3] = '{:.3f}'.format(_float(start_fader))
    table[row,4] = '{:.3f}'.format(_float(bases[0]))
    table[row,5] = '{:.3f}'.format(_float(bases[1]))
    table[row,6] = '{:.3f}'.format(_float(bases[2]))


def _row_key_from_topic(parts):
    if len(parts) >= 4 and parts[0] == 'vcm600' and parts[1] == 'channel':
        return parts[3]
    if len(parts) >= 3 and parts[0] == 'vcm600' and parts[1] == 'global':
        family = parts[2]
        if family == 'fx_grid' and len(parts) >= 5:
            try:
                row = int(parts[3]); col = int(parts[4])
            except Exception:
                return family
            return 'fx_grid_{}'.format((row - 1) * 4 + col)
        if family == 'fx_btn_grid' and len(parts) >= 5:
            try:
                row = int(parts[3]); col = int(parts[4])
            except Exception:
                return family
            return 'fx_button_{}'.format((row - 1) * 4 + col)
        if len(parts) > 3:
            return '{}_{}'.format(family, '_'.join(parts[3:]))
        return family
    return parts[-1] if parts else ''


def refresh(event_override=None):
    event = event_override if event_override is not None else _table_dict(op(VCM_PATH))
    topic = event.get('topic', '')
    value = _float(event.get('value', '0'))
    parts = topic.split('/') if topic else []
    if not parts:
        _emit([])
        return

    row_key = _row_key_from_topic(parts)
    if not row_key:
        _emit([])
        return

    prepared = [('global', row_key, value)]

    group = ''
    if len(parts) >= 4 and parts[0] == 'vcm600' and parts[1] == 'channel':
        group = parts[2]
    elif len(parts) >= 3 and parts[0] == 'vcm600' and parts[1] == 'global':
        focus = _table_dict(op(FOCUS_PATH))
        group = focus.get('focus_ch', '')

    # Focus: letzter bewegter Level-Fader bestimmt focus_channel
    if row_key == 'level' and group:
        _update_focus(group)

    if not group:
        _emit(prepared)
        _write_direct(prepared)
        _write_bitwig_remotes(prepared)
        return

    prepared.append(('live_' + group, row_key, value))

    active_subs = []
    for slot in _active_slots():
        if slot.startswith(group + '.'):
            sub = slot.split('.', 1)[1]
            if sub in ('1','2','3'):
                active_subs.append(sub)

    if not active_subs:
        prepared.append(('CH_' + group, row_key, value))
        _emit(prepared)
        _write_direct(prepared)
        _write_bitwig_remotes(prepared)
        return

    if len(active_subs) == 1:
        prepared.append((group + '.' + active_subs[0], row_key, value))
        _emit(prepared)
        _write_direct(prepared)
        _write_bitwig_remotes(prepared)
        return

    table = op(TABLE_PATH)
    headers   = {table[0,c].val: c for c in range(table.numCols)}
    row_index = next((r for r in range(1, table.numRows) if table[r,0].val == row_key), None)
    if row_index is None:
        for sub in active_subs:
            prepared.append((group + '.' + sub, row_key, value))
        _emit(prepared)
        _write_direct(prepared)
        _write_bitwig_remotes(prepared)
        return

    start_live   = _float(table[row_index, headers['live_' + group]].val if headers.get('live_' + group) is not None else 0)
    slot_values  = {sub: _float(table[row_index, headers[group + '.' + sub]].val if headers.get(group + '.' + sub) is not None else 0) for sub in ('1','2','3')}
    gb_row       = _ensure_gummiband_row(group, row_key)
    current      = _read_gummiband_row(gb_row)
    signature    = _signature(active_subs)
    start_fader  = _float(current['start_fader'], start_live)
    bases        = [_float(current['base_1'], slot_values['1']),
                    _float(current['base_2'], slot_values['2']),
                    _float(current['base_3'], slot_values['3'])]
    if current['active_signature'] != signature:
        start_fader = start_live
        bases       = [slot_values['1'], slot_values['2'], slot_values['3']]
        _write_gummiband_row(gb_row, signature, start_fader, bases)

    gummiband_owner = None
    try:
        base = parent()
        if base and len(base.inputConnectors) > 3 and base.inputConnectors[3].connections:
            gummiband_owner = base.inputConnectors[3].connections[0].owner
    except Exception:
        gummiband_owner = None
    gummiband_core = gummiband_owner.op('gummiband_core') if gummiband_owner else None
    if not gummiband_core:
        for sub in active_subs:
            prepared.append((group + '.' + sub, row_key, value))
        _emit(prepared)
        _write_direct(prepared)
        _write_bitwig_remotes(prepared)
        return

    outs = gummiband_core.module.apply_motion(bases, [int(s) for s in active_subs], start_fader, value)
    for idx, sub in enumerate(('1','2','3')):
        if sub in active_subs:
            prepared.append((group + '.' + sub, row_key, outs[idx]))
    _emit(prepared)
    _write_direct(prepared)
    _write_bitwig_remotes(prepared)
