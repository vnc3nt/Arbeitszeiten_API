# Arbeitszeiten API

Eine RESTful API für die Zeiterfassung, optimiert für die Verwendung als Backend für native iOS-Apps.

## 🚀 Deployment auf Render.com

### Voraussetzungen
1. PostgreSQL-Datenbank (kann auf Render.com erstellt werden)
2. GitHub-Repository mit diesem Code

### Deployment-Schritte

1. **Datenbank erstellen**
   - Gehen Sie zu [Render.com](https://render.com)
   - Erstellen Sie eine neue PostgreSQL-Datenbank
   - Notieren Sie die Verbindungsinformationen

2. **Web Service erstellen**
   - Klicken Sie auf "New +" → "Web Service"
   - Verbinden Sie Ihr GitHub-Repository
   - Konfigurieren Sie folgende Umgebungsvariablen:
     - `uname`: PostgreSQL Benutzername
     - `db`: Datenbankname
     - `password`: Datenbankpasswort
     - `host`: Datenbank-Host
     - `port`: Datenbank-Port (normalerweise 5432)
     - `scheme`: Datenbankschema (normalerweise der gleiche wie `db`)

3. **Deploy**
   - Render.com wird automatisch `pip install -r requirements.txt` ausführen
   - Die API wird mit Gunicorn gestartet

## 📡 API-Endpoints

Base URL: `https://your-app.onrender.com/api`

### Authentifizierung

Alle geschützten Endpoints benötigen einen Bearer Token im Authorization-Header:
```
Authorization: Bearer <your-token>
```

#### POST `/api/auth/register`
Neuen Benutzer registrieren

**Request Body:**
```json
{
  "username": "testuser",
  "password": "password123"
}
```

**Response (201):**
```json
{
  "message": "Benutzer erfolgreich registriert",
  "user_id": 1,
  "username": "testuser"
}
```

#### POST `/api/auth/login`
Benutzer anmelden

**Request Body:**
```json
{
  "username": "testuser",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "message": "Erfolgreich angemeldet",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": 1,
  "username": "testuser"
}
```

#### POST `/api/auth/logout`
Benutzer abmelden (benötigt Token)

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Erfolgreich abgemeldet"
}
```

#### GET `/api/auth/user`
Aktuelle Benutzerinformationen abrufen (benötigt Token)

**Response (200):**
```json
{
  "user_id": 1,
  "username": "testuser"
}
```

#### POST `/api/auth/change-password`
Passwort ändern (benötigt Token)

**Request Body:**
```json
{
  "current_password": "oldpassword",
  "new_password": "newpassword123"
}
```

**Response (200):**
```json
{
  "message": "Passwort erfolgreich geändert"
}
```

#### POST `/api/auth/change-username`
Benutzername ändern (benötigt Token)

**Request Body:**
```json
{
  "new_username": "newusername"
}
```

**Response (200):**
```json
{
  "message": "Benutzername erfolgreich geändert",
  "username": "newusername"
}
```

#### DELETE `/api/auth/delete-account`
Account löschen (benötigt Token)

**Request Body:**
```json
{
  "password": "password123"
}
```

**Response (200):**
```json
{
  "message": "Account erfolgreich gelöscht"
}
```

---

### Kategorien

#### GET `/api/categories`
Alle Kategorien des Benutzers abrufen (benötigt Token)

**Response (200):**
```json
{
  "categories": [
    {
      "id": 1,
      "name": "Arbeit",
      "color": "#FF5733"
    },
    {
      "id": 2,
      "name": "Überstunden",
      "color": "#3498DB"
    }
  ],
  "total": 2
}
```

#### POST `/api/categories`
Neue Kategorie erstellen (benötigt Token)

**Request Body:**
```json
{
  "name": "Urlaub",
  "color": "#2ECC71"
}
```

**Response (201):**
```json
{
  "message": "Kategorie erfolgreich erstellt",
  "id": 3,
  "name": "Urlaub",
  "color": "#2ECC71"
}
```

#### GET `/api/categories/<category_id>`
Einzelne Kategorie abrufen (benötigt Token)

**Response (200):**
```json
{
  "id": 1,
  "name": "Arbeit",
  "color": "#FF5733"
}
```

#### PUT `/api/categories/<category_id>`
Kategorie aktualisieren (benötigt Token)

**Request Body:**
```json
{
  "name": "Büroarbeit",
  "color": "#E74C3C"
}
```

**Response (200):**
```json
{
  "message": "Kategorie erfolgreich aktualisiert",
  "id": 1,
  "name": "Büroarbeit",
  "color": "#E74C3C"
}
```

#### DELETE `/api/categories/<category_id>`
Kategorie löschen (benötigt Token)

**Response (200):**
```json
{
  "message": "Kategorie erfolgreich gelöscht",
  "deleted_data_entries": 15
}
```

---

### Zeiterfassung

#### GET `/api/data`
Alle Zeiterfassungseinträge abrufen (benötigt Token)

**Query Parameters:**
- `start_date` (optional): YYYY-MM-DD
- `end_date` (optional): YYYY-MM-DD
- `category_id` (optional): Integer

**Beispiel:**
```
GET /api/data?start_date=2025-01-01&end_date=2025-12-31&category_id=1
```

**Response (200):**
```json
{
  "data": [
    {
      "date": "2025-10-03",
      "hours": 8.5,
      "max_hours": 40.0,
      "category": {
        "id": 1,
        "name": "Arbeit",
        "color": "#FF5733"
      }
    },
    {
      "date": "2025-10-02",
      "hours": 7.0,
      "max_hours": 40.0,
      "category": {
        "id": 1,
        "name": "Arbeit",
        "color": "#FF5733"
      }
    }
  ],
  "total_entries": 2
}
```

#### POST `/api/data`
Neuen Eintrag erstellen oder aktualisieren (benötigt Token)

**Request Body:**
```json
{
  "date": "2025-10-03",
  "category_id": 1,
  "hours": 8.5,
  "max_hours": 40.0
}
```

**Response (201 oder 200):**
```json
{
  "message": "Daten erfolgreich hinzugefügt",
  "date": "2025-10-03",
  "category_id": 1,
  "hours": 8.5
}
```

#### GET `/api/data/<date>`
Alle Einträge für ein bestimmtes Datum abrufen (benötigt Token)

**Beispiel:**
```
GET /api/data/2025-10-03
```

**Response (200):**
```json
{
  "date": "2025-10-03",
  "entries": [
    {
      "date": "2025-10-03",
      "hours": 8.5,
      "max_hours": 40.0,
      "category": {
        "id": 1,
        "name": "Arbeit",
        "color": "#FF5733"
      }
    }
  ],
  "total_hours": 8.5
}
```

#### PATCH `/api/data/<date>`
Eintrag für ein bestimmtes Datum aktualisieren (benötigt Token)

**Request Body:**
```json
{
  "category_id": 1,
  "hours": 9.0
}
```

Oder mit Inkrement (z.B. +0.5 oder -0.5 Stunden):
```json
{
  "category_id": 1,
  "increment": 0.5
}
```

**Response (200):**
```json
{
  "message": "Eintrag erfolgreich aktualisiert",
  "date": "2025-10-03",
  "hours": 9.0
}
```

#### DELETE `/api/data/<date>`
Alle Einträge für ein bestimmtes Datum löschen (benötigt Token)

**Response (200):**
```json
{
  "message": "2 Einträge gelöscht",
  "date": "2025-10-03"
}
```

---

### Health Check

#### GET `/api/health`
API-Status überprüfen (kein Token erforderlich)

**Response (200):**
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

---

## 📱 iOS-Integration

### Swift-Beispiel für Login

```swift
import Foundation

struct LoginRequest: Codable {
    let username: String
    let password: String
}

struct LoginResponse: Codable {
    let message: String
    let token: String
    let user_id: Int
    let username: String
}

func login(username: String, password: String) async throws -> LoginResponse {
    let url = URL(string: "https://your-app.onrender.com/api/auth/login")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    
    let loginData = LoginRequest(username: username, password: password)
    request.httpBody = try JSONEncoder().encode(loginData)
    
    let (data, response) = try await URLSession.shared.data(for: request)
    
    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw URLError(.badServerResponse)
    }
    
    return try JSONDecoder().decode(LoginResponse.self, from: data)
}
```

### Swift-Beispiel für authentifizierte Anfragen

```swift
func fetchCategories(token: String) async throws -> CategoriesResponse {
    let url = URL(string: "https://your-app.onrender.com/api/categories")!
    var request = URLRequest(url: url)
    request.httpMethod = "GET"
    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
    
    let (data, response) = try await URLSession.shared.data(for: request)
    
    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw URLError(.badServerResponse)
    }
    
    return try JSONDecoder().decode(CategoriesResponse.self, from: data)
}
```

### Token-Speicherung in iOS

```swift
import Security

class TokenManager {
    static let shared = TokenManager()
    
    private let service = "com.yourapp.arbeitszeiten"
    private let account = "userToken"
    
    func saveToken(_ token: String) {
        let data = token.data(using: .utf8)!
        
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecValueData as String: data
        ]
        
        SecItemDelete(query as CFDictionary)
        SecItemAdd(query as CFDictionary, nil)
    }
    
    func getToken() -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecReturnData as String: true
        ]
        
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        
        guard status == errSecSuccess,
              let data = result as? Data,
              let token = String(data: data, encoding: .utf8) else {
            return nil
        }
        
        return token
    }
    
    func deleteToken() {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account
        ]
        
        SecItemDelete(query as CFDictionary)
    }
}
```

---

## 🔧 Lokale Entwicklung

### Installation

1. Repository klonen
2. Virtuelle Umgebung erstellen:
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   # oder
   venv\Scripts\activate  # Windows
   ```
3. Dependencies installieren:
   ```bash
   pip install -r requirements.txt
   ```
4. `.env` Datei erstellen mit Datenbankverbindung:
   ```
   uname=your_username
   db=your_database
   password=your_password
   host=localhost
   port=5432
   scheme=your_database
   ```
5. API starten:
   ```bash
   python api_main.py
   ```

Die API läuft dann auf `http://localhost:5000`

---

## 📝 Fehlerbehandlung

Die API verwendet folgende HTTP-Statuscodes:

- `200 OK`: Erfolgreiche Anfrage
- `201 Created`: Ressource erfolgreich erstellt
- `400 Bad Request`: Ungültige Anfrage
- `401 Unauthorized`: Authentifizierung fehlgeschlagen oder Token fehlt
- `404 Not Found`: Ressource nicht gefunden
- `409 Conflict`: Konflikt (z.B. Benutzername existiert bereits)

Fehlerantworten haben folgendes Format:
```json
{
  "message": "Fehlerbeschreibung"
}
```

---

## 🔐 Sicherheit

- Passwörter werden mit SHA-512 gehasht
- Tokens haben eine Gültigkeitsdauer von 7 Tagen
- CORS ist aktiviert für Cross-Origin-Anfragen
- Alle Datenänderungen erfordern Authentifizierung

---

## 📄 Lizenz

Dieses Projekt ist für private Nutzung bestimmt.
