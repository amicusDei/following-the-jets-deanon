# firms_hq.csv — Käufer-Firmen & Hauptsitze (133 Firmen)

**Was:** Die getrackten Akquirer-Firmen (S&P 500, deren Jets sich namentlich/adressbasiert zuordnen ließen) mit geocodiertem Hauptsitz.
**Eine Zeile =** eine Firma.

**Spalten:** `firm_id` (interner Schlüssel) · `name` · `ticker` (Börsenkürzel) · `tier` (Zuordnungs-Sicherheitsstufe) · `hq_address`/`hq_zip` · `hq_lat`/`hq_lon` (Hauptsitz als Koordinaten) · `n_jets` (Zahl zugeordneter Jets).

**Wozu:** Der Firmen-Hauptsitz dient als „Home-Airport"-Ausschluss im Matching — Landungen nahe dem *eigenen* HQ zählen nicht als Ziel-Besuch (sonst nicht von „nach Hause fliegen" unterscheidbar).

**Quelle:** S&P-500-Konstituenten + Geocoding. **Caveat:** Dies ist die Originalkohorte (133 Firmen); eine de-anonymisierte Erweiterung auf ~170+ Firmen existiert separat (backtest_wide.db).
