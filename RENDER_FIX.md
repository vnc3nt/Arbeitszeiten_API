# Render.com Deployment - Fehlerbehebung

## Problem: ImportError beim Deployment

Der Fehler tritt auf, weil Render.com versucht, die alte `main.py` statt `api_main.py` zu laden.

## ✅ Lösung: Start Command in Render.com Dashboard ändern

### Schritt 1: Render.com Dashboard öffnen
1. Gehe zu [dashboard.render.com](https://dashboard.render.com)
2. Klicke auf deinen Web Service

### Schritt 2: Start Command ändern
1. Gehe zum Tab **"Settings"**
2. Scrolle zu **"Build & Deploy"**
3. Finde **"Start Command"**
4. Ändere den Befehl zu:
   ```
   gunicorn api_main:app --bind 0.0.0.0:$PORT
   ```
5. Klicke auf **"Save Changes"**

### Schritt 3: Manuellen Redeploy auslösen
1. Gehe zum Tab **"Manual Deploy"**
2. Klicke auf **"Deploy latest commit"**
3. Warte, bis der Deployment-Prozess abgeschlossen ist

## Alternative: Über Git pushen

Nachdem die `api.py` Datei korrigiert wurde, kannst du auch einfach pushen:

```bash
git add .
git commit -m "Fix: Remove CheckExistence import"
git push origin main
```

Render.com wird automatisch ein neues Deployment starten.

## ✅ Überprüfung nach Deployment

Teste ob die API läuft:

```bash
curl https://deine-app.onrender.com/api/health
```

Erwartete Antwort:
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

## 🔍 Weitere Überprüfungen

### 1. Logs ansehen
Im Render Dashboard → Tab "Logs" siehst du:
- Build-Logs
- Runtime-Logs
- Fehler

### 2. Environment Variables prüfen
Im Render Dashboard → Tab "Environment":
- ✅ `uname` (DB Username)
- ✅ `db` (Database Name)
- ✅ `password` (DB Password)
- ✅ `host` (DB Host - Internal URL!)
- ✅ `port` (normalerweise 5432)
- ✅ `scheme` (Database Schema)

**WICHTIG:** Verwende die **Internal Database URL** Komponenten, nicht die External!

### 3. Datenbank-Verbindung testen

Wenn die API startet aber Datenbankfehler auftreten:

1. Überprüfe die Umgebungsvariablen
2. Stelle sicher, dass die PostgreSQL-Datenbank läuft
3. Verwende den Internal Host (z.B. `dpg-xxxxx-a.oregon-postgres.render.com`)

## 📝 Wichtige Dateien im Repository

Nach der Korrektur sollten folgende Dateien korrekt sein:

- ✅ `api_main.py` - Haupteinstiegspunkt (NEU)
- ✅ `api.py` - Alte Blueprint-Datei (korrigiert, kein CheckExistence mehr)
- ✅ `Procfile` - Enthält: `web: gunicorn api_main:app --bind 0.0.0.0:$PORT`
- ✅ `render.yaml` - Enthält korrekten startCommand
- ✅ `api_resources/__init__.py` - Importiert keine CheckExistence mehr

## 🚀 Nach erfolgreichem Deployment

1. **Notiere deine API-URL**: z.B. `https://arbeitszeiten-api.onrender.com`

2. **Teste die Endpoints:**
   ```bash
   # Health Check
   curl https://deine-app.onrender.com/api/health
   
   # Registrierung testen
   curl -X POST https://deine-app.onrender.com/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"username":"testuser","password":"test12345"}'
   ```

3. **Aktualisiere die iOS-App:**
   In Xcode → `Constants.swift`:
   ```swift
   static let baseURL = "https://deine-app.onrender.com/api"
   ```

## ⚠️ Häufige Fehler

### "Application failed to respond"
- Start Command ist falsch → Prüfe ob `api_main:app` verwendet wird
- Port-Binding fehlt → Muss `0.0.0.0:$PORT` sein

### "Module not found"
- `requirements.txt` fehlt oder ist unvollständig
- Build Command sollte sein: `pip install -r requirements.txt`

### "Database connection failed"
- Falsche Umgebungsvariablen
- External statt Internal DB URL verwendet
- Datenbank ist in anderer Region als Web Service

## 📞 Support

Bei weiteren Problemen:
- Render Logs im Dashboard ansehen
- GitHub Issues checken
- Render Community Forum: [community.render.com](https://community.render.com)
