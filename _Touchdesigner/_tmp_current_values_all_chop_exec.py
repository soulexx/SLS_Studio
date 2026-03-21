def onValueChange(channel, sampleIndex, val, prev):
    try:
        op('/project1/Instrument_Control_Core/current_values_all_core').module.refresh()
    except Exception:
        pass
    return
