# jets.csv — Flugzeug-Identität (499 Jets)

**Was:** Jeder Jet, der einer der getrackten S&P-500-Firmen zugeordnet wurde, mit Identität und Klassifikation.
**Eine Zeile =** ein Flugzeug.

**Spalten:** `icao24` (eindeutiger 24-Bit-Funkcode, der Primärschlüssel im Flugverkehr) · `tail` (Kennung, z. B. N351SD) · `firm_id`/`firm` (besitzende Firma) · `owner` (FAA-Registereintrag) · `type`/`faa_mfr`/`faa_model`/`faa_seats` (Hersteller/Modell/Sitze laut FAA) · `aircraft_class` (**business** = Geschäftsjet vs. **commercial** = Verkehrsflugzeug) · `valid_from`/`valid_to` (Eigentums-Zeitfenster; `valid_to` leer = noch registriert).

**Klassifikation:** 269 business, 230 commercial. Nur die **business**-Jets sind für die Analyse relevant; die commercial-Einträge sind ganze Airline-/Frachtflotten (Southwest, UPS, Delta …), die in der Flugdatei bewusst ausgeschlossen wurden.

**Quelle:** FAA-Register + Modell-Klassifikation. **Caveat:** 86 % der Business-Jets haben eine offene rechte Eigentumskante (`valid_to` leer); `valid_from` ist das Zertifikatsdatum, nicht zwingend das Kaufdatum.
