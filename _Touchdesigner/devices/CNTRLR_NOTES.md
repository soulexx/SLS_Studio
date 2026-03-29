# cntrlr
#
# Device adapter for the Livid CNTRLR.
#
# Responsibilities:
# - accept raw MIDI from cntrlr_midi_in
# - map raw events to semantic topics via cntrlr_map
# - normalize values and forward them into /project1/logic__control_exec
#
# LED meaning lives at root level in /project1/out__cntrlr_leds.
# This container should not own LED behavior decisions.
#
# 4x4 grid note order was calibrated live against the hardware.
