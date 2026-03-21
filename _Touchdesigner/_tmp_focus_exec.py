
def onValueChange(channel, sampleIndex, val, prev):
    if val == prev:
        return
    env = {'op': op, 'me': me}
    exec(op(me.parent().path + '/focus_core').text, env)
    env['update_from_channel'](channel.name, float(val))
    op(me.parent().path + '/focus_out').cook(force=True)
    return
