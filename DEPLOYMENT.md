# Deployment-Anleitung für Render.com

## Schritt-für-Schritt-Anleitung

### 1. PostgreSQL-Datenbank erstellen

1. Gehen Sie zu [dashboard.render.com](https://dashboard.render.com)
2. Klicken Sie auf "New +" → "PostgreSQL"
3. Geben Sie einen Namen ein (z.B. "arbeitszeiten-db")
4. Wählen Sie einen kostenlosen oder kostenpflichtigen Plan
5. Klicken Sie auf "Create Database"
6. Warten Sie, bis die Datenbank erstellt wurde
7. Notieren Sie sich die Verbindungsinformationen:
   - Host (Internal Database URL)
   - Database Name
   - Username
   - Password
   - Port (normalerweise 5432)

### 2. GitHub-Repository vorbereiten

1. Stellen Sie sicher, dass alle Änderungen committed sind:
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

### 3. Web Service auf Render.com erstellen

1. Gehen Sie zurück zum Render Dashboard
2. Klicken Sie auf "New +" → "Web Service"
3. Wählen Sie "Build and deploy from a Git repository"
4. Verbinden Sie Ihr GitHub-Konto (falls noch nicht geschehen)
5. Wählen Sie Ihr Repository aus
6. Konfigurieren Sie den Service:

   **Basic Settings:**
   - Name: `arbeitszeiten-api`
   - Region: Wählen Sie die Region Ihrer Datenbank
   - Branch: `main`
   - Root Directory: (leer lassen)
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn api_main:app --bind 0.0.0.0:$PORT`

   **Environment Variables:**
   Fügen Sie folgende Umgebungsvariablen hinzu:
   
   - `uname`: Der Username Ihrer PostgreSQL-Datenbank
   - `db`: Der Datenbankname
   - `password`: Das Datenbankpasswort
   - `host`: Der interne Host der Datenbank (z.B. `dpg-xxxxx-a`)
   - `port`: `5432`
   - `scheme`: Der Datenbankname (gleich wie `db`)

   **Wichtig:** Verwenden Sie die **Internal Database URL** Komponenten, nicht die External!

7. Wählen Sie einen Plan (Free oder Paid)
8. Klicken Sie auf "Create Web Service"

### 4. Deployment abwarten

1. Render.com wird nun:
   - Den Code von GitHub pullen
   - Dependencies installieren
   - Die Anwendung starten
2. Sie können den Deployment-Fortschritt in den Logs verfolgen
3. Nach erfolgreichem Deployment erhalten Sie eine URL wie:
   `https://arbeitszeiten-api.onrender.com`

### 5. API testen

Testen Sie die API mit curl oder Postman:

```bash
# Health Check
curl https://ihre-app.onrender.com/api/health

# Erwartete Antwort:
# {"status": "healthy", "message": "API is running"}
```

### 6. In iOS-App integrieren

Aktualisieren Sie die Base URL in Ihrer iOS-App:

```swift
let baseURL = "https://ihre-app.onrender.com/api"
```

## Troubleshooting

### Problem: "Application failed to respond"

**Lösung:**
- Überprüfen Sie die Logs im Render Dashboard
- Stellen Sie sicher, dass alle Umgebungsvariablen korrekt gesetzt sind
- Überprüfen Sie, dass der Start Command korrekt ist

### Problem: Datenbankverbindung fehlgeschlagen

**Lösung:**
- Verwenden Sie die **Internal Database URL** Komponenten
- Stellen Sie sicher, dass Host, Port, Username und Password korrekt sind
- Überprüfen Sie, dass die Datenbank in der gleichen Region wie der Web Service ist

### Problem: "Module not found"

**Lösung:**
- Stellen Sie sicher, dass `requirements.txt` alle Dependencies enthält
- Build Command sollte sein: `pip install -r requirements.txt`

### Problem: Port-Binding-Fehler

**Lösung:**
- Stellen Sie sicher, dass der Start Command `$PORT` verwendet:
  `gunicorn api_main:app --bind 0.0.0.0:$PORT`

## Automatische Deployments

Render.com deployt automatisch bei jedem Push zu Ihrem Main Branch:

```bash
git add .
git commit -m "Update API"
git push origin main
```

Das neue Deployment startet automatisch!

## Kosten

- **Free Plan**: 
  - 750 Stunden pro Monat
  - Service schläft nach 15 Minuten Inaktivität
  - Erste Anfrage nach dem Aufwachen kann 30+ Sekunden dauern

- **Starter Plan ($7/Monat)**:
  - Service läuft 24/7
  - Keine Schlafzeit
  - Schnellere Performance

## Monitoring

1. **Logs anzeigen:**
   - Gehen Sie zum Render Dashboard
   - Klicken Sie auf Ihren Service
   - Tab "Logs" öffnen

2. **Metrics anzeigen:**
   - Tab "Metrics" im Dashboard
   - Zeigt CPU, Memory und Response Times

## Backup der Datenbank

1. Gehen Sie zur PostgreSQL-Datenbank im Dashboard
2. Tab "Backups"
3. Klicken Sie auf "Create Manual Backup"

## Custom Domain (Optional)

1. Gehen Sie zum Web Service
2. Tab "Settings"
3. Scrollen Sie zu "Custom Domains"
4. Fügen Sie Ihre Domain hinzu
5. Folgen Sie den DNS-Anweisungen
