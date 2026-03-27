# Instrument Listener Testmatrix 18

Diese Datei definiert die erste reale Teststufe fuer die neue feste Listener-Architektur.

Ziel:

- kleine, verifizierbare Matrix
- feste Slot-Zuordnung
- getrennte Listener fuer `main`, `fx_grid`, `fx_button`
- Bitwig -> TD Ruecklesen
- TD -> Bitwig Schreiben
- keine dynamische Umadressierung

## Umfang

Testslots:

- `1.1`
- `1.2`
- `1.3`
- `2.1`
- `2.2`
- `2.3`

Bundles pro Slot:

- `main`
- `fx_grid`
- `fx_button`

Gesamt:

- `6` Slots
- `3` Bundles pro Slot
- `18` Listener

## Zweck

Mit dieser Testmatrix soll geprueft werden:

- saubere feste Track-Zuordnung
- saubere Listener-Trennung
- kein Crosstalk
- sauberes Ruecklesen aus Bitwig
- sauberes gleichzeitiges Senden an alle aktiven Slots

## Listener-Index-Plan

Kanal 1:

- `1.1.main = 0`
- `1.1.fx_grid = 1`
- `1.1.fx_button = 2`
- `1.2.main = 3`
- `1.2.fx_grid = 4`
- `1.2.fx_button = 5`
- `1.3.main = 6`
- `1.3.fx_grid = 7`
- `1.3.fx_button = 8`

Kanal 2:

- `2.1.main = 24`
- `2.1.fx_grid = 25`
- `2.1.fx_button = 26`
- `2.2.main = 27`
- `2.2.fx_grid = 28`
- `2.2.fx_button = 29`
- `2.3.main = 30`
- `2.3.fx_grid = 31`
- `2.3.fx_button = 32`

Hinweis:

- Die Luecke zwischen `8` und `24` ist Absicht.
- So bleibt die spaetere 48er-Blocklogik konsistent.
- Kanal 1 reserviert `0..23`
- Kanal 2 reserviert `24..47`

## Bundle-Bedeutung

### `main`

Enthaelt die Hauptparameter:

- `hi_eq`
- `mid_eq`
- `low_eq`
- `pan`
- `send_a`
- `send_b`
- `resonance`
- `frequency`

### `fx_grid`

Enthaelt die Ruecklese-/Write-Bank fuer:

- `fx_grid_1 .. fx_grid_8`

### `fx_button`

Enthaelt die Ruecklese-/Write-Bank fuer:

- `fx_button_1 .. fx_button_8`

Wenn spaeter mehr als `8` Buttons noetig sind, bleibt das Bundle gleich, nur die interne Parametertabelle wird erweitert.

## Slot-Tabelle

Empfohlene Referenztabelle `instrument_listener_bundles_test18`:

| slot_id | bundle_type | listener_index | target_track | page_name | verified |
| --- | --- | --- | --- | --- | --- |
| 1.1 | main | 0 | 1.1 | Main | 0 |
| 1.1 | fx_grid | 1 | 1.1 | FX Grid | 0 |
| 1.1 | fx_button | 2 | 1.1 | FX Buttons | 0 |
| 1.2 | main | 3 | 1.2 | Main | 0 |
| 1.2 | fx_grid | 4 | 1.2 | FX Grid | 0 |
| 1.2 | fx_button | 5 | 1.2 | FX Buttons | 0 |
| 1.3 | main | 6 | 1.3 | Main | 0 |
| 1.3 | fx_grid | 7 | 1.3 | FX Grid | 0 |
| 1.3 | fx_button | 8 | 1.3 | FX Buttons | 0 |
| 2.1 | main | 24 | 2.1 | Main | 0 |
| 2.1 | fx_grid | 25 | 2.1 | FX Grid | 0 |
| 2.1 | fx_button | 26 | 2.1 | FX Buttons | 0 |
| 2.2 | main | 27 | 2.2 | Main | 0 |
| 2.2 | fx_grid | 28 | 2.2 | FX Grid | 0 |
| 2.2 | fx_button | 29 | 2.2 | FX Buttons | 0 |
| 2.3 | main | 30 | 2.3 | Main | 0 |
| 2.3 | fx_grid | 31 | 2.3 | FX Grid | 0 |
| 2.3 | fx_button | 32 | 2.3 | FX Buttons | 0 |

## Empfohlene TD-Zielstruktur

Die neue Testmatrix sollte nicht als lose Root-Reihe ohne Typunterscheidung enden.

Empfohlen:

- `/project1/bitwig_listener_test`
  - `rules`
  - `slots`
  - `debug`

Darunter pro Slot ein klarer Block:

- `slot_1_1`
  - `main_listener`
  - `fx_grid_listener`
  - `fx_button_listener`

- `slot_1_2`
  - `main_listener`
  - `fx_grid_listener`
  - `fx_button_listener`

usw.

## Rueckschreib-Ziele in TD

Die drei Bundle-Typen sollen nicht in dieselbe TD-Tabelle schreiben.

Empfohlen:

- `main_listener -> instrument_values_main`
- `fx_grid_listener -> instrument_values_fx_grid`
- `fx_button_listener -> instrument_values_fx_button`

So bleiben Quelle und Bedeutung sauber getrennt.

## Verifikation pro Slot

Ein Slot gilt erst als verifiziert, wenn alle drei Punkte stimmen:

1. `Track`
- zeigt auf den richtigen Bitwig-Track

2. `Write`
- TD-Aenderung kommt in Bitwig am richtigen Ziel an

3. `Readback`
- Bitwig-Aenderung kommt in TD im richtigen Bundle zurueck

## Verifikation pro Bundle

### `main`

Pruefen:

- `hi_eq .. frequency` lesen
- `hi_eq .. frequency` schreiben
- keine Spiegelung auf andere Slots

### `fx_grid`

Pruefen:

- `fx_grid_1 .. 8` lesen
- `fx_grid_1 .. 8` schreiben
- Gummiband-/Gruppenlogik bleibt korrekt

### `fx_button`

Pruefen:

- einzelne Buttons lesen
- einzelne Buttons schreiben
- keine Vermischung mit `main` oder `fx_grid`

## Minimaler Live-Bauplan

1. Neue Testbasis unter `/project1/bitwig_listener_test` anlegen
2. Nur `slot_1_1` mit `main/fx_grid/fx_button`
3. Ruecklesen pruefen
4. `slot_1_2` und `slot_1_3`
5. Danach `slot_2_1 .. slot_2_3`

Erst danach:

- vorhandene alte `bitwigRemotesTrack`-Reihe ersetzen oder ablösen

## Wichtige Regel fuer den Live-Aufbau

Wenn ein Bundle nicht sauber reconnectet:

- nicht skriptbasiert hart resetten
- manuell im UI pruefen
- Zieltrack direkt verifizieren
- erst dann als `verified = 1` markieren

## Erfolgskriterium

Die Testmatrix ist erfolgreich, wenn:

- `1.1 .. 2.3` jeweils drei getrennte Bundle-Listener haben
- alle sechs Slots gleichzeitig ruecklesbar sind
- alle aktiven Slots gleichzeitig beschrieben werden koennen
- kein Crosstalk mehr zwischen den Slots entsteht
