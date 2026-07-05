# flights_business.csv — Geschäftsjet-Flüge (154,388 Flüge, 2018–2025)

**Was:** Alle aus OpenSky rekonstruierten Flüge der **Business-Jets** — die Verkehrs-/Airline-Flotten (die ~83 % des Flugvolumens ausmachen: Southwest, UPS, Delta, American, United, Alaska) sind **ausgeschlossen**, weil sie nichts mit Manager-Diligence zu tun haben.
**Eine Zeile =** ein Flug (ein Start-Lande-Segment eines Jets).

**Spalten:** `icao24` (welcher Jet — Verknüpfung zu jets.csv) · `firm_id` (besitzende Firma) · `day` · `firstseen`/`lastseen` (Start-/End-Zeit als Unix-Zeitstempel UTC) · `callsign` · `dep_airport`/`arr_airport` (Start-/Zielflughafen als ICAO-Code).

**Quelle:** OpenSky Network (ADS-B-Positionsdaten), point-in-time auf Eigentumsfenster geclippt. **Wozu:** Der Rohstoff — landet `arr_airport` ≤50 km von einem Ziel-HQ (deals.csv) derselben Firma im Pre-Fenster?

**Caveats:** Zeitstempel sind **UTC**. Die OpenSky-Abdeckung wuchs über die Jahre stark (~9,7k Flüge 2018 → ~31k 2025) — wichtig bei zeitlichen Vergleichen. Flüge ohne `arr_airport` sind enthalten (Zielflughafen nicht rekonstruierbar).
