# Projekt-Änderungen: Web-App → RESTful API

## Übersicht der Änderungen

Ihr Projekt wurde erfolgreich von einer Flask-Web-App mit HTML-Templates in eine vollständige RESTful API umgewandelt, die als Backend für eine native iOS-App verwendet werden kann.

## Neue Dateien

### Hauptdateien
- **`api_main.py`**: Neuer Haupteinstiegspunkt der API
  - Ersetzt `main.py` für die API
  - Konfiguriert Flask, CORS und alle API-Endpoints
  - Initialisiert die Datenbank

### API-Ressourcen
- **`api_resources/auth.py`**: Neue Authentifizierungs-Endpoints
  - Registrierung, Login, Logout
  - Passwort/Benutzername ändern
  - Account löschen
  - Token-basierte Authentifizierung (Decorator `@token_required`)

### Dokumentation
- **`README.md`**: Vollständige API-Dokumentation
  - Alle Endpoints mit Beispielen
  - iOS-Integration-Beispiele (Swift)
  - Token-Management in iOS

- **`DEPLOYMENT.md`**: Deployment-Anleitung für Render.com
  - Schritt-für-Schritt-Anweisungen
  - Troubleshooting
  - Monitoring und Backups

- **`.env.example`**: Beispiel für Umgebungsvariablen

## Aktualisierte Dateien

### API-Ressourcen
- **`api_resources/data.py`**: Komplett überarbeitet
  - Von Session- auf Token-Authentifizierung umgestellt
  - Neue Klasse `DataByDate` für datumsspezifische Operationen
  - GET, POST, PATCH, DELETE Methoden
  - Bessere Fehlerbehandlung
  - Filterung nach Datum und Kategorie

- **`api_resources/category.py`**: Komplett überarbeitet
  - Von Session- auf Token-Authentifizierung umgestellt
  - Neue Klasse `CategoryById` für einzelne Kategorien
  - GET, POST, PUT, DELETE Methoden
  - Konflikt-Prüfung bei Namen

- **`api_resources/api_check.py`**: Vereinfacht
  - Health-Check-Endpoint für Monitoring

- **`api_resources/__init__.py`**: Aktualisiert
  - Importiert alle neuen Ressourcen

### Konfigurationsdateien
- **`requirements.txt`**: Aktualisiert
  - `Flask-CORS` hinzugefügt (für iOS-App)
  - Überflüssige Dependencies entfernt
  - Besser kommentiert

- **`Procfile`**: Aktualisiert
  - Verwendet jetzt `api_main:app` statt `main:app`

- **`render.yaml`**: Aktualisiert
  - Konfiguration für Render.com Deployment
  - Umgebungsvariablen definiert

- **`runtime.txt`**: Aktualisiert
  - Python 3.12.0 spezifiziert

## Architektur-Änderungen

### Authentifizierung
**Vorher:**
- Session-basiert (Flask Session Cookies)
- Funktioniert nur für Web-Browser

**Nachher:**
- Token-basiert (Bearer Token)
- Funktioniert für mobile Apps und Web
- Token im Authorization-Header
- 7 Tage Gültigkeit

### API-Struktur
**Vorher:**
```
/login (GET, POST) → HTML-Seite
/register (GET, POST) → HTML-Seite
/home (GET, POST) → HTML-Seite
/api/data → JSON
/api/categories → JSON
```

**Nachher:**
```
/api/auth/register → JSON
/api/auth/login → JSON
/api/auth/logout → JSON
/api/auth/user → JSON
/api/auth/change-password → JSON
/api/auth/change-username → JSON
/api/auth/delete-account → JSON
/api/categories → JSON
/api/categories/<id> → JSON
/api/data → JSON
/api/data/<date> → JSON
/api/health → JSON
```

### CORS-Unterstützung
- Aktiviert für alle `/api/*` Routen
- Erlaubt alle Origins (kann eingeschränkt werden)
- Unterstützt alle HTTP-Methoden
- Ermöglicht iOS-App den API-Zugriff

## Alte Dateien (können gelöscht werden)

Diese Dateien werden nicht mehr benötigt:

### Frontend
- `templates/` (alle HTML-Templates)
- `static/` (CSS, JavaScript, Bilder)

### Alte Python-Module
- `main.py` (ersetzt durch `api_main.py`)
- `login.py` (Logik in `api_resources/auth.py` integriert)
- `api.py` (nicht mehr benötigt)
- `api_resources/check_existence.py` (nicht mehr benötigt)

## Datenbank

**Keine Änderungen am Schema!**
- Alle Tabellen bleiben gleich
- `models.py` bleibt unverändert
- Bestehende Daten bleiben erhalten

## Deployment

### Lokal testen
```bash
# Virtuelle Umgebung aktivieren
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt

# API starten
python api_main.py
```

Die API läuft auf `http://localhost:5000`

### Auf Render.com deployen
Folgen Sie der Anleitung in `DEPLOYMENT.md`

## iOS-Integration

### Beispiel: Login
```swift
let url = URL(string: "https://your-app.onrender.com/api/auth/login")!
var request = URLRequest(url: url)
request.httpMethod = "POST"
request.setValue("application/json", forHTTPHeaderField: "Content-Type")

let body = ["username": "test", "password": "test123"]
request.httpBody = try? JSONEncoder().encode(body)

let (data, _) = try await URLSession.shared.data(for: request)
let response = try JSONDecoder().decode(LoginResponse.self, from: data)

// Token speichern
UserDefaults.standard.set(response.token, forKey: "authToken")
```

### Beispiel: Authentifizierte Anfrage
```swift
var request = URLRequest(url: url)
request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
```

## Nächste Schritte

1. ✅ API lokal testen
2. ✅ Auf Render.com deployen
3. ✅ iOS-App entwickeln
4. ✅ Token-Management in iOS implementieren
5. ✅ API-Endpoints in iOS-App integrieren

## Support

Bei Fragen zur API-Dokumentation siehe `README.md`
Bei Deployment-Problemen siehe `DEPLOYMENT.md`
