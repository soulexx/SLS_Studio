# Instrument Listener Matrix 48

Diese Datei konkretisiert das Zielmodell fuer `6 x 8 = 48` Instrument-Slots.

Sie ist absichtlich technischer als `INSTRUMENT_LISTENER_MODEL.md` und dient als Bauvorlage.

## Zielmatrix

Kanäle:

- `1 .. 6`

Slots pro Kanal:

- `.1 .. .8`

Gesamt:

- `48` feste Instrument-Slots

Slot-IDs:

- `1.1 .. 1.8`
- `2.1 .. 2.8`
- `3.1 .. 3.8`
- `4.1 .. 4.8`
- `5.1 .. 5.8`
- `6.1 .. 6.8`

## Parameterfamilien pro Instrument

Grundfamilien:

- `hi_eq`
- `mid_eq`
- `low_eq`
- `pan`
- `send_a`
- `send_b`
- `resonance`
- `frequency`

Ebenen pro Familie:

- `main`
- `fx_grid`
- `fx_button`

Damit entstehen pro Instrument:

- `8` Familien
- `3` Ebenen
- `24` logisch getrennte Wertefelder

## Listener-Bundles pro Instrument

Empfohlene erste feste Struktur:

- `main_bundle`
- `fx_grid_bundle`
- `fx_button_bundle`

Damit:

- `3` Listener-Bundles pro Instrument

Bei `48` Instrumenten:

- `48 x 3 = 144` Listener-Bundles

## Listener-Gesamtbewertung

Bekannter tdBitwig-Code:

- `maxCursorCount = 256`

Geplante Matrix:

- `144` Instrument-Listener-Bundles

Restbudget fuer Zusatz-Listener:

- `256 - 144 = 112`

Das ist genug fuer:

- Track-Cursor
- ClipSlot-Cursor
- Service-/Test-Listener
- spaetere Erweiterungen

## Feste Regel

Ein Listener-Bundle gehoert immer genau zu:

- `slot_id`
- `bundle_type`

Beispiel:

- `slot_id = 3.5`
- `bundle_type = fx_grid`

Nicht erlaubt:

- dynamisch denselben Listener heute fuer `3.5`, morgen fuer `6.2` verwenden
- beliebiges Re-Pinning als Kernarchitektur

## Empfohlene TD-Datenstruktur

### 1. instrument_slots

Eine Row pro Slot.

Spalten:

- `slot_id`
- `group`
- `subslot`
- `active`
- `bitwig_track_name`
- `instrument_label`
- `status`

Beispiel:

- `3.5 | 3 | 5 | 0 | LEAD_3_5 | lead stab 2 | ready`

### 2. instrument_listener_bundles

Eine Row pro Slot und Bundle.

Spalten:

- `slot_id`
- `bundle_type`
- `listener_index`
- `bitwig_target`
- `page_name`
- `connect_state`
- `verified`

Beispiel:

- `3.5 | main | 72 | LEAD_3_5 | Main | connected | 1`
- `3.5 | fx_grid | 73 | LEAD_3_5 | FX Grid | connected | 1`
- `3.5 | fx_button | 74 | LEAD_3_5 | FX Buttons | connected | 1`

### 3. instrument_values_main

Spalten:

- `slot_id`
- `control`
- `value`
- `last_source`
- `last_update_ts`

### 4. instrument_values_fx_grid

Spalten:

- `slot_id`
- `control`
- `value`
- `last_source`
- `last_update_ts`

### 5. instrument_values_fx_button

Spalten:

- `slot_id`
- `control`
- `value`
- `last_source`
- `last_update_ts`

### 6. instrument_runtime_state

Spalten:

- `slot_id`
- `pickup_state`
- `hybrid_state`
- `gummiband_state`
- `write_enabled`
- `read_enabled`

## Konkrete Slot-Bundle-Zählung

Pro Slot:

- `1` Main-Listener
- `1` FX-Grid-Listener
- `1` FX-Button-Listener

Pro Kanal mit `8` Slots:

- `8 x 3 = 24` Listener

Bei `6` Kanälen:

- `6 x 24 = 144` Listener

## Empfohlene Index-Strategie

Die Indexe sollten nicht improvisiert, sondern blockweise vergeben werden.

Empfohlene Verteilung:

- Kanal 1: `0 .. 23`
- Kanal 2: `24 .. 47`
- Kanal 3: `48 .. 71`
- Kanal 4: `72 .. 95`
- Kanal 5: `96 .. 119`
- Kanal 6: `120 .. 143`

Innerhalb eines Kanals:

- Slot `.1`:
  - `main = +0`
  - `fx_grid = +1`
  - `fx_button = +2`
- Slot `.2`:
  - `main = +3`
  - `fx_grid = +4`
  - `fx_button = +5`
- ...
- Slot `.8`:
  - `main = +21`
  - `fx_grid = +22`
  - `fx_button = +23`

Beispiel:

- Kanal `2`, Slot `.5`
- Kanal-Blockstart `24`
- Slotoffset `4 x 3 = 12`
- ergibt:
  - `main = 36`
  - `fx_grid = 37`
  - `fx_button = 38`

## Formeln

Mit:

- `group in 1..6`
- `slot in 1..8`

Dann:

- `group_base = (group - 1) * 24`
- `slot_base = (slot - 1) * 3`

Listener:

- `main_listener = group_base + slot_base + 0`
- `fx_grid_listener = group_base + slot_base + 1`
- `fx_button_listener = group_base + slot_base + 2`

## Ruecklese-Regel

Bitwig-Aenderungen sollen nie direkt “in freie Luft” gehen.

Jeder gelesene Wert wird sofort auf den zentralen Slot-Zustand geschrieben:

- `main_bundle -> instrument_values_main`
- `fx_grid_bundle -> instrument_values_fx_grid`
- `fx_button_bundle -> instrument_values_fx_button`

## Write-Regel

TouchDesigner schreibt nur an:

- aktive Slots

Dabei gilt:

- `main`-Writes an alle aktiven Zielslots
- `fx_grid`-Writes an alle aktiven Zielslots
- `fx_button`-Writes an alle aktiven Zielslots

Wenn mehrere Slots aktiv sind:

- Gummiband-/Hybrid-Logik bleibt pro Gruppe im Core
- der resultierende Zielwert wird dann pro aktivem Slot geschrieben

## Verifikationsstrategie

Nicht direkt `144` Listener bauen und hoffen.

Stufen:

1. `1.1 .. 1.3`
- je `main`, `fx_grid`, `fx_button`
- ergibt `9` Listener

2. `1.1 .. 2.3`
- ergibt `18` Slots des alten Musters? nein:
- `6` Slots x `3` Bundles = `18` Listener

3. `1.1 .. 2.8`
- `16` Slots x `3` Bundles = `48` Listener

4. komplette `48` Slots
- `144` Listener

## Empfehlung fuer den naechsten Bau-Schritt

Nicht sofort `48` Slots live bauen.

Sinnvoller naechster echter Aufbau:

- `6` Referenz-Slots
- je `3` Bundles
- also `18` Listener

Damit pruefen:

- stabile Track-Zuordnung
- stabile Ruecklese
- keine Cross-Talks
- manuelles Reconnect-Verhalten

Wenn stabil:

- auf `16` Slots
- dann auf `48`

## Kurzfazit

Fuer dein Zielbild ist die richtige Einheit:

- `48` feste Instrument-Slots
- mit je `3` festen Listener-Bundles
- also `144` Listener

Das passt in die theoretische tdBitwig-Grenze von `256`, ist aber nur dann sinnvoll, wenn die Listener als feste Matrix gebaut werden.
