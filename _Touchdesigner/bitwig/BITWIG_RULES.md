# Bitwig Rules

Diese Datei ist die Arbeitsreferenz fuer die Bitwig-Integration in diesem Projekt.
Sie wird angepasst, wenn sich Struktur, Ports, verifizierte Verbindungsregeln oder Arbeitskonventionen aendern.

## Ziel

Die Bitwig-Anbindung soll nachvollziehbar, testbar und stabil bleiben.

Speichern:
- verifizierte Port- und Verbindungsdaten
- klare Benennung der zentralen Bitwig-Komponenten
- bekannte Datenfluesse zwischen Bitwig und TouchDesigner
- verifizierte Debug- und Testhinweise

Nicht speichern:
- Vermutungen ohne Test
- veraltete Verbindungsdaten
- doppelte Regeln, die bereits in `AGENTS.md` stehen

## Zentrale Bereiche

Bitwig liegt in TouchDesigner aktuell unter:

- `/project1/bitwig`

Wichtige bekannte Komponenten:

- `/project1/bitwig/bitwigTrack/bitwigTrack`
- `/project1/bitwig/group_tracks/group_track_1` bis `group_track_6`
- `/project1/bitwig/DEMO1/project1/bitwigMain`
- `/project1/bitwig/DEMO1/project1/projectRemotesMacros1`

## Verbindungsregeln

Aktuell verifizierte Kernparameter:

- `Bitwigipaddress = 127.0.0.1`
- `Bitwigport = 8088`
- `Touchdesignerinport = 9099`
- `Connect = true`
- `Enableoutgoingosc = true`
- `Enableincomingosc = true`
- `Enableincomingtime = true`

Wenn sich diese Daten aendern:

1. Live-Konfiguration pruefen
2. diese Datei aktualisieren
3. falls relevant den Stand in `PROJECT_STATE.md` anpassen

## Arbeitsregeln

- Bei Arbeiten an der Bitwig-Integration zuerst die zentrale Konfiguration in `/project1/bitwig/DEMO1/project1/bitwigMain` pruefen.
- Fuer track-bezogene tdBitwig-Steuerung den bestehenden Cursor in `/project1/bitwig/bitwigTrack/bitwigTrack` oder die festen `/project1/bitwig/group_tracks/group_track_*` bevorzugen.
- Fuer 8er-Deep-Parameterbaenke den bestehenden tdBitwig-Remote-Block `/project1/bitwig/DEMO1/project1/projectRemotesMacros1` bevorzugen, bevor ein neuer eigener Remote-Comp gebaut wird.
- Vor strukturellen Aenderungen an Bitwig-Komponenten bestehende OSC-, AsyncIO- und Callback-Pfade pruefen.
- Live-Test hat Vorrang vor Annahmen.
- Wenn keine Live-Daten sichtbar sind, zwischen Struktur korrekt und Verbindung verifiziert unterscheiden.
- `bitwigRemotesTrack*` nicht per Script reconnecten, wenn ein echter tdBitwig-Neuaufbau noetig ist; der manuelle `Connect`-Reconnect im UI ist im aktuellen Projekt verifiziert stabiler als `Connect`-/Listener-Resets per Python.

## Deep Mapping

- Der sichtbare tdBitwig-Deep-Pfad liegt jetzt auf Root als `vcm600 -> Instrument_Control_Core -> bitwigRemotesTrackx_y`; die Hilfslogik fuer Fokus, `fx_grid` und Subbank-Mapping sitzt dabei intern im `Instrument_Control_Core`.
- `/project1/Instrument_Control_Core/fx_subbank_map` liefert fuer den Deep-Pfad semantische `deep_1..8`-Kanaele plus Metadaten (`deep_slot_active`, `deep_focus_valid`, `deep_bank_id`, `deep_page_index`).
- `/project1/Instrument_Control_Core/deep_bus` ist jetzt der zentrale Deep-Ausgang fuer den aktuell fokussierten Kanal; die gruppierten `bitwigRemotesTrackx_y`-Ziele bleiben dabei vorerst ein experimenteller Ziel-Layer und sind noch keine verifizierte feste `x.y`-Adressierung.
- Die rohen acht VCM-600-Deep-Fader werden im `Instrument_Control_Core` als `fx_grid_1 .. fx_grid_8` angezeigt und lesen direkt aus dem internen `fx_grid`-Router, nicht aus dem bereits gegateten Deep-Bus.
- Aktuell sind direkte `Remotecontrol0..7`-Schreibzugriffe live verifiziert.
- Remote-Page-Umschaltung ist strukturell vorbereitet, aber noch nicht live verifiziert, solange `projectRemotesMacros1` keine belegten `PageNames` meldet.
- Die aktuelle Root-Reihe `bitwigRemotesTrack1_1 .. 6_3` kann nach Script-Resets in einen scheinbar verbundenen, aber intern falsch gebundenen Zustand geraten; wenn Track-/Parameter-Spiegelungen auftreten, zuerst die betroffenen Remotes manuell im UI reconnecten und erst danach weiterdebuggen.

## Debug-Regeln

- TouchDesigner-Errors und Warnings im Bitwig-Bereich zuerst pruefen.
- Bei Verbindungsproblemen zuerst Ports, OSC-In/Out und `Connect` pruefen.
- Fehlende Live-Daten nicht automatisch als Konfigurationsfehler werten.

## Pflege

Wenn sich etwas aendert:

- nur den aktuellen Stand stehen lassen
- veraltete Regeln entfernen statt sammeln
- verifizierte Live-Erkenntnisse bevorzugen
