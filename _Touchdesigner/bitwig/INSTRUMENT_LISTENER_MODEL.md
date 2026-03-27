# Instrument Listener Model

Diese Datei beschreibt das Zielmodell fuer die naechste stabile Bitwig-/TouchDesigner-Architektur.

## Ziel

Das System soll pro Instrument einen festen, ruecklesbaren Zustand haben:

- TouchDesigner schreibt nach Bitwig
- Bitwig-Aenderungen kommen ueber feste Listener zurueck nach TouchDesigner
- alle aktiven Instrumente koennen gleichzeitig senden
- Undo/Redo arbeitet auf dem zentralen TD-Zustand, nicht auf losen Remote-Nodes

## Slot-Modell

Aktuell:

- `1.1 .. 6.3` = `18` feste Instrument-Slots

Geplante Ausbaustufe:

- `1.1 .. 6.8` = `48` feste Instrument-Slots

Jeder Slot ist ein festes Instrument mit fester Bitwig-Zuordnung.

Keine dynamische Umadressierung:

- kein freies Retargeting ueber zufaellige `Track`-Felder
- keine wechselnden semantischen Rollen pro Slot
- Bitwig-Ziele bleiben fest

## Instrument-Modell

Ein Instrument ist nicht nur ein 8er-Remoteblock.

Ein Instrument enthaelt feste Parameterfamilien:

- `hi_eq`
- `mid_eq`
- `low_eq`
- `pan`
- `send_a`
- `send_b`
- `resonance`
- `frequency`

Fuer jede dieser Familien gibt es drei Ebenen:

- `main`
- `fx_grid`
- `fx_button`

Beispiel fuer einen Slot `2.3`:

- `2.3.hi_eq.main`
- `2.3.hi_eq.fx_grid`
- `2.3.hi_eq.fx_button`
- `2.3.mid_eq.main`
- `2.3.mid_eq.fx_grid`
- `2.3.mid_eq.fx_button`
- ...
- `2.3.frequency.main`
- `2.3.frequency.fx_grid`
- `2.3.frequency.fx_button`

## State-Modell in TouchDesigner

`channel_selector` bleibt verantwortlich fuer:

- welche Slots aktiv sind

`Instrument_Control_Core` wird zentrale Wahrheit fuer:

- alle Instrument-Parameter
- Pickup-Zustaende
- Hybrid-/Gummiband-Anker
- Listener-Rueckmeldungen aus Bitwig
- Undo/Redo-Historie

Empfohlene logische Struktur pro Slot:

- `slot_id`
- `group`
- `subslot`
- `bitwig_track_name`
- `listener_bundle_id`

Pro Parameterfamilie:

- `main_value`
- `fx_grid_value`
- `fx_button_value`
- `pickup_state`
- `last_source`
- `last_update_ts`

## Listener-Modell

### Zielbild

Nicht ein fragiles Sammelsurium von lose reconnecteten Remotes, sondern feste Listener-Bundles.

Ein Listener-Bundle gehoert immer genau zu einem Instrument-Slot.

### Empfohlene erste Ausbaustufe

Pro Instrument-Slot:

- `1` Listener fuer `main`-Werte
- `1` Listener fuer `fx_grid`
- `1` Listener fuer `fx_button`

Das ergibt:

- `3` Listener pro Instrument

Bei `48` Instrumenten:

- `48 x 3 = 144` Listener

Das liegt unter der im tdBitwig-Code sichtbaren theoretischen Cursor-Grenze:

- `maxCursorCount = 256`

### Empfehlung

Als erste echte Ausbaustufe:

- zuerst `48` Instrumente sauber modellieren
- aber technisch mit einer kleineren verifizierten Teilmatrix starten
- z. B. `6 x 3` oder `6 x 4`
- danach in Richtung `48`

### Ruecklese-Regel

Jeder Listener soll:

- auf ein festes Bitwig-Ziel zeigen
- Aenderungen in Bitwig lesen
- diese Aenderungen in den korrekten TD-Slot zurueckschreiben

Nicht erlaubt:

- ein Listener, der mal diesem und mal jenem Instrument gehoert
- dynamische Wiederverwendung eines instabilen Cursor-Ziels fuer mehrere Slots

## Writer-Modell

Die Sendelogik bleibt zustandsgetrieben:

- `channel_selector` markiert aktive Slots
- `Instrument_Control_Core` berechnet Werte
- der Writer sendet an alle aktiven Slots

Fuer `fx_grid` und spaeter weitere Deep-Familien gilt:

- Werte werden pro Gruppe mit `gummiband` berechnet
- gesendet wird danach an alle aktiven Slots

## Undo / Redo

Undo/Redo soll auf dem zentralen TD-State passieren, nicht ueber Bitwig-internes Undo.

### Warum

- Bitwig-Undo wuerde auch fremde DAW-Aktionen erfassen
- TD braucht reproduzierbare Rueckspruenge fuer genau die Instrument-Parameter
- Undo muss auf dieselbe Logik wie Pickup/Hybrid/Listener-Rueckmeldung zugreifen

### Modell

Jede relevante Zustandsaenderung erzeugt einen History-Eintrag:

- `slot_id`
- `parameter_path`
- `old_value`
- `new_value`
- `source`
- `timestamp`
- `transaction_id`

Beispiel:

- `slot_id = 2.3`
- `parameter_path = hi_eq.fx_grid`
- `old_value = 0.41`
- `new_value = 0.66`
- `source = vcm600`

### Undo

- letzten History-Block rueckgaengig machen
- TD-State auf `old_value` setzen
- den Ruecksprung wieder nach Bitwig schreiben

### Redo

- zuletzt rueckgaengig gemachten Block erneut anwenden
- TD-State auf `new_value` setzen
- den Zustand wieder nach Bitwig schreiben

### Wichtige Regel

Undo/Redo sollte in Transaktionen arbeiten:

- ein einzelner Fader-Move mit mehreren aktiven Instrumenten = ein Undo-Block
- nicht 18 komplett unabhhaengige Undo-Schritte fuer dieselbe Geste

## Empfohlene Datenstruktur

Empfohlen fuer spaeteren TD-Tabellen-/DAT-Aufbau:

1. `instrument_slots`
- ein Row pro Slot
- feste Slot-Metadaten

2. `instrument_values_main`
- `slot_id`
- `control`
- `value`

3. `instrument_values_fx_grid`
- `slot_id`
- `control`
- `value`

4. `instrument_values_fx_button`
- `slot_id`
- `control`
- `value`

5. `instrument_listener_map`
- `slot_id`
- `bundle_type`
- `bitwig_target`
- `listener_index`
- `page_name`
- `status`

6. `instrument_history`
- Undo/Redo-Historie

## Listener-Aufbau-Hinweis

Praxis-Hinweis aus dem aktuellen Projekt:

- Manuelles Reconnecten in tdBitwig ist aktuell stabiler als Script-Reconnect.
- Der Hinweis aus dem Live-Test lautet, dass ueber `Next`/Track-Navigation der benoetigte Zieltrack besser getroffen werden kann als ueber aggressive Script-Resets.

Das sollte in der naechsten Bauphase bewusst genutzt werden:

- Listener-Bundles langsam und verifiziert auf die Zieltracks setzen
- pro Bundle direkt pruefen
- erst danach vervielfaeltigen

## Empfehlung fuer den naechsten echten Bauschritt

1. Ein Referenz-Instrument komplett definieren
- Werte
- Listener
- Ruecklesen
- Undo/Redo-Transaktion

2. Eine kleine Matrix bauen
- z. B. `1.1`, `1.2`, `1.3`, `2.1`, `2.2`, `2.3`

3. Erst wenn diese stabil ist:
- auf `6 x 8 = 48` erweitern

## Kurzfazit

Die richtige Einheit ist nicht mehr nur ein einzelner Remote-Node.

Die richtige Einheit ist:

- `1 Instrument-Slot`
- mit mehreren festen Parameterfamilien
- mehreren festen Listener-Bundles
- zentralem TD-State
- Undo/Redo-Historie
