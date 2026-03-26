CURRENT_VALUES_ALL_PATH = '/project1/Instrument_Control_Core/current_values_all'
CURRENT_VALUES_ALL_CORE_PATH = '/project1/Instrument_Control_Core/current_values_all_core'

_control_row_cache = {}
_target_col_cache  = {}
_mem_in_shape      = (0, 0)  # (numRows, numCols) — detect structural changes


def _rebuild_caches():
    global _control_row_cache, _target_col_cache
    _control_row_cache = {}
    _target_col_cache  = {}
    table = op(CURRENT_VALUES_ALL_PATH)
    if not table or table.numRows == 0:
        return
    for col in range(1, table.numCols):
        t = table[0, col].val
        if t:
            _target_col_cache[t] = col
    for row in range(1, table.numRows):
        c = table[row, 0].val
        if c:
            _control_row_cache[c] = row


def _refresh():
    try:
        op(CURRENT_VALUES_ALL_CORE_PATH).module.refresh()
    except Exception:
        pass
    _rebuild_caches()


def onCellChange(dat, cells, prev):
    if cells[0].col != 2:
        return
    row_in  = cells[0].row
    target  = dat[row_in, 0].val
    control = dat[row_in, 1].val
    row = _control_row_cache.get(control)
    col = _target_col_cache.get(target)
    if row is None or col is None:
        _refresh()
        row = _control_row_cache.get(control)
        col = _target_col_cache.get(target)
        if row is None or col is None:
            return
    table = op(CURRENT_VALUES_ALL_PATH)
    if table:
        table[row, col] = cells[0].val


def onTableChange(dat):
    global _mem_in_shape
    new_shape = (dat.numRows, dat.numCols)
    if new_shape != _mem_in_shape:
        # Struktur hat sich geaendert — full refresh noetig
        _mem_in_shape = new_shape
        _refresh()
    # reine Value-Aenderung: onCellChange hat das bereits erledigt


def onRowChange(dat, rows):  _refresh()
def onColChange(dat, cols):  _refresh()
def onSizeChange(dat):       _refresh()
