# Mapping Rules

Diese Datei ist die Arbeitsreferenz fuer den Aufbau von Controller-Mappings in diesem Projekt.
Sie wird angepasst, wenn sich Benennung, Struktur oder verifizierte Regeln aendern.

## Ziel

Mappings sollen hardwareorientiert, lesbar und live verifizierbar sein.

Nicht speichern:
- alte Script-Semantik, wenn sie nicht live bestaetigt ist
- vermischte Topic-Logik mit nicht nachvollziehbaren Kurzformen

Speichern:
- physische Eingangsstruktur
- klare Topics
- klare Labels
- Live-Korrekturen aus echten Tests

## Grundstruktur

Jeder Controller liegt in TouchDesigner unter:

- `/project1/devices/<device>`

Typische Nodes pro Geraet:

- `<device>_midi_in`
- `<device>_lookup`
- `<device>_callbacks`
- `<device>_debug`
- `<device>_last_match`
- `<device>_bus_events`
- `<device>_map`
- optional `<device>_led_map`
- optional weitere Tabellen wie `*_roles`, `*_meta`, `*_translation`, `*_sysex`

## Topic-Regeln

### Allgemein

- Topics beginnen mit dem Geraetenamen
- Zaehlen beginnt bei `1`, nie bei `0`
- Fader und andere lineare Reihen bleiben linear
- Matrixartige Bereiche nutzen immer `row/col`

### Beispiele

Linear:

- `cntrlr/faders/1`
- `vcm600/channel/1/play`

Matrix:

- `cntrlr/knobs_left/1/1`
- `cntrlr/knobs_right/2/4`
- `cntrlr/encoders/3/2`
- `cntrlr/encoder_push/1/3`
- `cntrlr/grid_4x4/2/1`
- `cntrlr/grid_2x16/1/16`
- `vcm600/global/effect_grid/2/4`
- `vcm600/global/fx_grid/1/2`

## Label-Regeln

Labels sollen direkt lesbar sein und die physische Flaeche wiedergeben.

Beispiele:

- `Fader 1`
- `Knob Left 1/1`
- `Knob Right 2/4`
- `Encoder 1/3`
- `Encoder Push 3/4`
- `4x4 Grid 2/1`
- `2x16 Grid 1/16`
- `Effect Grid 2/3`
- `FX Grid 1/1`
- `Channel 1 Play`

## Group-Regeln

Groups sollen hardwarebezogen und knapp sein.

### CNTRLR

- `faders`
- `knobs_left`
- `knobs_right`
- `encoders`
- `encoder_push`
- `grid_4x4`
- `grid_2x16`

Hinweis:
- In den aktuellen Tabellen kann bei CNTRLR intern noch `group=grid` oder `group=buttons_main` stehen, wenn die Daten noch nicht vollstaendig vereinheitlicht wurden. Ziel bleibt das Schema oben.

### VCM-600

- `channel_buttons`
- `channel_controls`
- `effect_buttons`
- `effect_controls`
- `fx_buttons`
- `master_buttons`
- `global_buttons`
- `global_controls`

## Verifikationsregeln

Wenn reale Hardware von Dokumentation oder Fremd-Script abweicht:

1. Live-Test hat Vorrang
2. Wert im Mapping direkt korrigieren
3. `notes`-Feld auf live verifiziert setzen
4. Falls noetig `led_map` mitziehen

Typische Notiz:

- `Live corrected by hardware test`

## CNTRLR-Regeln

### Leseregel

Bei Matrixen wird von oben nach unten und dann von links nach rechts gedacht.

Beispiel:

- `1/1`, `2/1`, `3/1` bilden die erste Spalte
- danach `1/2`, `2/2`, `3/2`

### Bestaetigte Bereiche

Fader:

- `5, 9, 13, 17, 21, 25, 29, 33`

Knob Left 3x4:

- row 1: `2, 6, 10, 14`
- row 2: `3, 7, 11, 15`
- row 3: `4, 8, 12, 16`

Knob Right 3x4:

- row 1: `18, 22, 26, 30`
- row 2: `19, 23, 27, 31`
- row 3: `20, 24, 28, 32`

Encoder 3x4:

- row 1: `49, 52, 55, 58`
- row 2: `50, 53, 56, 59`
- row 3: `51, 54, 57, 60`

Encoder Push 3x4:

- gleiche Matrix wie Encoder
- Typ ist `note`
- Push sendet `Note On` mit Wert `64`

4x4 Grid:

- row 1: `1, 5, 9, 13`
- row 2: `2, 6, 10, 14`
- row 3: `3, 7, 11, 15`
- row 4: `4, 8, 12, 16`

2x16 Grid:

- row 1: `17` bis `32`
- row 2: `33` bis `48`

## VCM-600-Regeln

### Grundidee

Der VCM-600 wird nicht als ein grosses Raster behandelt, sondern als:

- Kanalzuege
- globale Controls
- globale Button-/Grid-Flaechen

### Bestaetigte globale Raster

2x4 Effect Grid:

- `13, 14, 15, 16`
- `17, 18, 19, 20`

2x4 FX Grid:

- `71, 72, 73, 74`
- `75, 76, 77, 78`

## Pflege

Wenn sich etwas aendert:

- diese Datei aktualisieren
- nur den aktuellen Stand stehen lassen
- veraltete Regeln entfernen statt ansammeln

Wenn ein Mapping nur vermutet ist, muss das hier kenntlich sein.
