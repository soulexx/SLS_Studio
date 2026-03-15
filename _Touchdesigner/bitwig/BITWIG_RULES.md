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

- `/project1/bitwig/bitwigMain`
- `/project1/bitwig/bitwigMain/bitwigMain`

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

- Bei Arbeiten an der Bitwig-Integration zuerst die zentrale Konfiguration in `/project1/bitwig/bitwigMain/bitwigMain` pruefen.
- Vor strukturellen Aenderungen an Bitwig-Komponenten bestehende OSC-, AsyncIO- und Callback-Pfade pruefen.
- Live-Test hat Vorrang vor Annahmen.
- Wenn keine Live-Daten sichtbar sind, zwischen Struktur korrekt und Verbindung verifiziert unterscheiden.

## Debug-Regeln

- TouchDesigner-Errors und Warnings im Bitwig-Bereich zuerst pruefen.
- Bei Verbindungsproblemen zuerst Ports, OSC-In/Out und `Connect` pruefen.
- Fehlende Live-Daten nicht automatisch als Konfigurationsfehler werten.

## Pflege

Wenn sich etwas aendert:

- nur den aktuellen Stand stehen lassen
- veraltete Regeln entfernen statt sammeln
- verifizierte Live-Erkenntnisse bevorzugen
