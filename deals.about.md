# deals.csv — Betrachtete M&A-Deals & Ziel-Hauptsitze (1434 Deals)

**Was:** Alle Übernahme-/Fusionsdeals der getrackten Firmen, mit Ziel-Hauptsitz (das geografische Ziel, das die Jets potenziell ansteuern).
**Eine Zeile =** ein Deal (Käufer kauft Ziel).

**Spalten:** `deal_id` · `firm_id`/`acquirer`/`acquirer_parent` (Käufer) · `target` (Zielfirma) · `announcement_date`/`completion_date`/`withdrawn_date` · `status` · `deal_value_musd` (Volumen in Mio USD) · `target_nation_code` · `target_hq_lat`/`target_hq_lon` (**Ziel-Hauptsitz** als Koordinaten — der Anker des Tests) · `hq_source`/`hq_confidence` (Herkunft/Güte des Geocodings) · `is_self_deal` (1 = Aktienrückkauf, Ziel=Käufer; aus der Analyse ausgeschlossen).

**Schlüsselzahlen:** 459/1434 mit geocodiertem Ziel-HQ (Rest = kleine/undisclosed Privatdeals); 203 Self-Deals (ausgeschlossen).

**Quelle:** SDC/WRDS-M&A + Ziel-HQ-Geocoding (Compustat für börsennotierte Ziele, Web-Research für private). **Wozu:** Das `announcement_date` definiert das 90-Tage-Pre-Fenster; das Ziel-HQ ist der Ort, dessen Besuche gezählt werden.
