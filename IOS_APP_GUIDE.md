# iOS App Entwicklung - Komplette Anleitung

## 🎯 Übersicht

Diese Anleitung zeigt dir, wie du eine native iOS-App erstellst, die die gleiche Funktionalität wie die Web-App hat, aber die neue REST API verwendet.

## 📱 Schritt 1: Neues Xcode-Projekt erstellen

1. Öffne Xcode
2. Wähle "Create a new Xcode project"
3. Wähle "iOS" → "App"
4. Konfiguration:
   - **Product Name**: `Arbeitszeiten`
   - **Team**: Dein Team
   - **Organization Identifier**: `com.yourname.arbeitszeiten`
   - **Interface**: SwiftUI
   - **Language**: Swift
   - **Storage**: None (wir verwenden API)
5. Speichere das Projekt

## 🏗️ Schritt 2: Projekt-Struktur erstellen

Erstelle folgende Ordner-Struktur in Xcode:

```
Arbeitszeiten/
├── Models/
│   ├── User.swift
│   ├── Category.swift
│   ├── TimeEntry.swift
│   └── APIResponse.swift
├── ViewModels/
│   ├── AuthViewModel.swift
│   ├── CategoryViewModel.swift
│   └── TimeTrackingViewModel.swift
├── Views/
│   ├── Authentication/
│   │   ├── LoginView.swift
│   │   └── RegisterView.swift
│   ├── Main/
│   │   ├── HomeView.swift
│   │   ├── CategoryListView.swift
│   │   └── ProfileView.swift
│   └── Components/
│       ├── TimeEntryCard.swift
│       └── CategoryPicker.swift
├── Services/
│   ├── APIService.swift
│   ├── AuthService.swift
│   └── KeychainManager.swift
└── Utilities/
    ├── Constants.swift
    └── Extensions.swift
```

## 📝 Schritt 3: Code-Dateien erstellen

### 1. Constants.swift
```swift
//
//  Constants.swift
//  Arbeitszeiten
//

import Foundation

struct Constants {
    // WICHTIG: Ersetze dies mit deiner tatsächlichen Render.com URL!
    static let baseURL = "https://deine-app.onrender.com/api"
    
    struct Endpoints {
        // Auth
        static let register = "/auth/register"
        static let login = "/auth/login"
        static let logout = "/auth/logout"
        static let user = "/auth/user"
        static let changePassword = "/auth/change-password"
        static let changeUsername = "/auth/change-username"
        static let deleteAccount = "/auth/delete-account"
        
        // Categories
        static let categories = "/categories"
        static func category(id: Int) -> String { "/categories/\(id)" }
        
        // Data
        static let data = "/data"
        static func dataByDate(_ date: String) -> String { "/data/\(date)" }
        
        // Health
        static let health = "/health"
    }
}
```

### 2. KeychainManager.swift
```swift
//
//  KeychainManager.swift
//  Arbeitszeiten
//

import Foundation
import Security

class KeychainManager {
    static let shared = KeychainManager()
    
    private let service = "com.yourname.arbeitszeiten"
    private let tokenKey = "authToken"
    
    private init() {}
    
    func saveToken(_ token: String) -> Bool {
        guard let data = token.data(using: .utf8) else { return false }
        
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: tokenKey,
            kSecValueData as String: data
        ]
        
        // Lösche alten Token falls vorhanden
        SecItemDelete(query as CFDictionary)
        
        // Speichere neuen Token
        let status = SecItemAdd(query as CFDictionary, nil)
        return status == errSecSuccess
    }
    
    func getToken() -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: tokenKey,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
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
    
    func deleteToken() -> Bool {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: tokenKey
        ]
        
        let status = SecItemDelete(query as CFDictionary)
        return status == errSecSuccess
    }
}
```

### 3. Models/User.swift
```swift
//
//  User.swift
//  Arbeitszeiten
//

import Foundation

struct User: Codable, Identifiable {
    let id: Int
    let username: String
    
    enum CodingKeys: String, CodingKey {
        case id = "user_id"
        case username
    }
}

struct LoginRequest: Codable {
    let username: String
    let password: String
}

struct LoginResponse: Codable {
    let message: String
    let token: String
    let userId: Int
    let username: String
    
    enum CodingKeys: String, CodingKey {
        case message, token, username
        case userId = "user_id"
    }
}

struct RegisterRequest: Codable {
    let username: String
    let password: String
}

struct RegisterResponse: Codable {
    let message: String
    let userId: Int
    let username: String
    
    enum CodingKeys: String, CodingKey {
        case message, username
        case userId = "user_id"
    }
}
```

### 4. Models/Category.swift
```swift
//
//  Category.swift
//  Arbeitszeiten
//

import Foundation
import SwiftUI

struct Category: Codable, Identifiable {
    let id: Int
    let name: String
    let color: String
    
    var colorValue: Color {
        Color(hex: color) ?? .blue
    }
}

struct CategoriesResponse: Codable {
    let categories: [Category]
    let total: Int
}

struct CreateCategoryRequest: Codable {
    let name: String
    let color: String
}

struct CategoryResponse: Codable {
    let message: String
    let id: Int?
    let name: String?
    let color: String?
}
```

### 5. Models/TimeEntry.swift
```swift
//
//  TimeEntry.swift
//  Arbeitszeiten
//

import Foundation

struct TimeEntry: Codable, Identifiable {
    var id: String { date }
    let date: String
    let hours: Double?
    let maxHours: Double?
    let category: CategoryInfo?
    
    enum CodingKeys: String, CodingKey {
        case date, hours, category
        case maxHours = "max_hours"
    }
    
    struct CategoryInfo: Codable {
        let id: Int
        let name: String
        let color: String
    }
}

struct TimeEntriesResponse: Codable {
    let data: [TimeEntry]
    let totalEntries: Int
    
    enum CodingKeys: String, CodingKey {
        case data
        case totalEntries = "total_entries"
    }
}

struct CreateTimeEntryRequest: Codable {
    let date: String
    let categoryId: Int
    let hours: Double
    let maxHours: Double?
    
    enum CodingKeys: String, CodingKey {
        case date, hours
        case categoryId = "category_id"
        case maxHours = "max_hours"
    }
}

struct UpdateTimeEntryRequest: Codable {
    let categoryId: Int
    let hours: Double?
    let increment: Double?
    
    enum CodingKeys: String, CodingKey {
        case hours, increment
        case categoryId = "category_id"
    }
}
```

### 6. Services/APIService.swift
```swift
//
//  APIService.swift
//  Arbeitszeiten
//

import Foundation

enum APIError: Error, LocalizedError {
    case invalidURL
    case invalidResponse
    case unauthorized
    case serverError(String)
    case decodingError
    case networkError(Error)
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Ungültige URL"
        case .invalidResponse:
            return "Ungültige Antwort vom Server"
        case .unauthorized:
            return "Nicht autorisiert"
        case .serverError(let message):
            return message
        case .decodingError:
            return "Fehler beim Verarbeiten der Daten"
        case .networkError(let error):
            return "Netzwerkfehler: \(error.localizedDescription)"
        }
    }
}

class APIService {
    static let shared = APIService()
    
    private init() {}
    
    func request<T: Decodable>(
        endpoint: String,
        method: String = "GET",
        body: Encodable? = nil,
        requiresAuth: Bool = true
    ) async throws -> T {
        guard let url = URL(string: Constants.baseURL + endpoint) else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        // Add auth token if required
        if requiresAuth {
            guard let token = KeychainManager.shared.getToken() else {
                throw APIError.unauthorized
            }
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        // Add body if present
        if let body = body {
            request.httpBody = try JSONEncoder().encode(body)
        }
        
        do {
            let (data, response) = try await URLSession.shared.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIError.invalidResponse
            }
            
            switch httpResponse.statusCode {
            case 200...299:
                return try JSONDecoder().decode(T.self, from: data)
            case 401:
                throw APIError.unauthorized
            default:
                if let errorResponse = try? JSONDecoder().decode(ErrorResponse.self, from: data) {
                    throw APIError.serverError(errorResponse.message)
                }
                throw APIError.serverError("Server-Fehler: \(httpResponse.statusCode)")
            }
        } catch let error as APIError {
            throw error
        } catch {
            throw APIError.networkError(error)
        }
    }
}

struct ErrorResponse: Codable {
    let message: String
}

struct MessageResponse: Codable {
    let message: String
}
```

### 7. ViewModels/AuthViewModel.swift
```swift
//
//  AuthViewModel.swift
//  Arbeitszeiten
//

import Foundation

@MainActor
class AuthViewModel: ObservableObject {
    @Published var isAuthenticated = false
    @Published var currentUser: User?
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    init() {
        checkAuthentication()
    }
    
    func checkAuthentication() {
        isAuthenticated = KeychainManager.shared.getToken() != nil
        if isAuthenticated {
            Task {
                await fetchCurrentUser()
            }
        }
    }
    
    func login(username: String, password: String) async {
        isLoading = true
        errorMessage = nil
        
        do {
            let request = LoginRequest(username: username, password: password)
            let response: LoginResponse = try await APIService.shared.request(
                endpoint: Constants.Endpoints.login,
                method: "POST",
                body: request,
                requiresAuth: false
            )
            
            // Save token
            _ = KeychainManager.shared.saveToken(response.token)
            
            // Update state
            currentUser = User(id: response.userId, username: response.username)
            isAuthenticated = true
            
        } catch {
            errorMessage = error.localizedDescription
        }
        
        isLoading = false
    }
    
    func register(username: String, password: String) async {
        isLoading = true
        errorMessage = nil
        
        do {
            let request = RegisterRequest(username: username, password: password)
            let _: RegisterResponse = try await APIService.shared.request(
                endpoint: Constants.Endpoints.register,
                method: "POST",
                body: request,
                requiresAuth: false
            )
            
            // Auto-login after registration
            await login(username: username, password: password)
            
        } catch {
            errorMessage = error.localizedDescription
        }
        
        isLoading = false
    }
    
    func logout() async {
        do {
            let _: MessageResponse = try await APIService.shared.request(
                endpoint: Constants.Endpoints.logout,
                method: "POST"
            )
        } catch {
            print("Logout error: \(error)")
        }
        
        // Clear local state
        _ = KeychainManager.shared.deleteToken()
        currentUser = nil
        isAuthenticated = false
    }
    
    private func fetchCurrentUser() async {
        do {
            let user: User = try await APIService.shared.request(
                endpoint: Constants.Endpoints.user
            )
            currentUser = user
        } catch {
            // If fetching user fails, logout
            await logout()
        }
    }
}
```

### 8. Views/Authentication/LoginView.swift
```swift
//
//  LoginView.swift
//  Arbeitszeiten
//

import SwiftUI

struct LoginView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    @State private var username = ""
    @State private var password = ""
    @State private var showingRegister = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                // Logo oder Titel
                Text("⏱️")
                    .font(.system(size: 80))
                
                Text("Arbeitszeiten")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                
                Spacer()
                
                // Login Form
                VStack(spacing: 15) {
                    TextField("Benutzername", text: $username)
                        .textFieldStyle(.roundedBorder)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                    
                    SecureField("Passwort", text: $password)
                        .textFieldStyle(.roundedBorder)
                    
                    if let error = authViewModel.errorMessage {
                        Text(error)
                            .foregroundColor(.red)
                            .font(.caption)
                    }
                    
                    Button(action: {
                        Task {
                            await authViewModel.login(username: username, password: password)
                        }
                    }) {
                        if authViewModel.isLoading {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                        } else {
                            Text("Anmelden")
                                .fontWeight(.semibold)
                        }
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(10)
                    .disabled(authViewModel.isLoading || username.isEmpty || password.isEmpty)
                }
                .padding()
                
                Spacer()
                
                // Register Button
                Button(action: {
                    showingRegister = true
                }) {
                    Text("Noch kein Account? Registrieren")
                        .font(.footnote)
                }
                .sheet(isPresented: $showingRegister) {
                    RegisterView()
                }
            }
            .padding()
            .navigationBarHidden(true)
        }
    }
}
```

### 9. Views/Authentication/RegisterView.swift
```swift
//
//  RegisterView.swift
//  Arbeitszeiten
//

import SwiftUI

struct RegisterView: View {
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject var authViewModel: AuthViewModel
    
    @State private var username = ""
    @State private var password = ""
    @State private var confirmPassword = ""
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Registrierung")) {
                    TextField("Benutzername", text: $username)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                    
                    SecureField("Passwort", text: $password)
                    
                    SecureField("Passwort bestätigen", text: $confirmPassword)
                }
                
                if let error = authViewModel.errorMessage {
                    Section {
                        Text(error)
                            .foregroundColor(.red)
                    }
                }
                
                Section {
                    Button(action: {
                        Task {
                            await authViewModel.register(username: username, password: password)
                            if authViewModel.isAuthenticated {
                                dismiss()
                            }
                        }
                    }) {
                        if authViewModel.isLoading {
                            HStack {
                                Spacer()
                                ProgressView()
                                Spacer()
                            }
                        } else {
                            Text("Registrieren")
                                .frame(maxWidth: .infinity)
                        }
                    }
                    .disabled(!isValidForm || authViewModel.isLoading)
                }
            }
            .navigationTitle("Registrieren")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Abbrechen") {
                        dismiss()
                    }
                }
            }
        }
    }
    
    private var isValidForm: Bool {
        !username.isEmpty &&
        password.count >= 8 &&
        password == confirmPassword
    }
}
```

### 10. Views/Main/HomeView.swift
```swift
//
//  HomeView.swift
//  Arbeitszeiten
//

import SwiftUI

struct HomeView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    @StateObject private var viewModel = TimeTrackingViewModel()
    
    var body: some View {
        TabView {
            // Zeit erfassen
            TimeTrackingView()
                .environmentObject(viewModel)
                .tabItem {
                    Label("Zeiten", systemImage: "clock.fill")
                }
            
            // Kategorien
            CategoryListView()
                .tabItem {
                    Label("Kategorien", systemImage: "folder.fill")
                }
            
            // Profil
            ProfileView()
                .tabItem {
                    Label("Profil", systemImage: "person.fill")
                }
        }
    }
}

struct TimeTrackingView: View {
    @EnvironmentObject var viewModel: TimeTrackingViewModel
    @State private var selectedDate = Date()
    @State private var showingAddEntry = false
    
    var body: some View {
        NavigationView {
            VStack {
                // Date Picker
                DatePicker("Datum", selection: $selectedDate, displayedComponents: .date)
                    .datePickerStyle(.graphical)
                    .padding()
                    .onChange(of: selectedDate) { newDate in
                        Task {
                            await viewModel.fetchEntries(for: newDate)
                        }
                    }
                
                // Entries List
                if viewModel.isLoading {
                    ProgressView()
                } else if viewModel.entries.isEmpty {
                    Text("Keine Einträge für dieses Datum")
                        .foregroundColor(.secondary)
                } else {
                    List(viewModel.entries) { entry in
                        TimeEntryRow(entry: entry)
                    }
                }
                
                Spacer()
            }
            .navigationTitle("Zeiterfassung")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { showingAddEntry = true }) {
                        Image(systemName: "plus")
                    }
                }
            }
            .sheet(isPresented: $showingAddEntry) {
                AddTimeEntryView(date: selectedDate)
                    .environmentObject(viewModel)
            }
        }
        .task {
            await viewModel.fetchCategories()
            await viewModel.fetchEntries(for: selectedDate)
        }
    }
}

struct TimeEntryRow: View {
    let entry: TimeEntry
    
    var body: some View {
        HStack {
            if let category = entry.category {
                Circle()
                    .fill(Color(hex: category.color) ?? .blue)
                    .frame(width: 12, height: 12)
                
                Text(category.name)
                    .fontWeight(.medium)
            }
            
            Spacer()
            
            if let hours = entry.hours {
                Text("\(hours, specifier: "%.1f")h")
                    .fontWeight(.semibold)
            }
        }
        .padding(.vertical, 4)
    }
}
```

## ⚙️ Schritt 4: Extensions hinzufügen

### Utilities/Extensions.swift
```swift
//
//  Extensions.swift
//  Arbeitszeiten
//

import SwiftUI

extension Color {
    init?(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            return nil
        }
        
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue:  Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}

extension Date {
    func toString(format: String = "yyyy-MM-dd") -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = format
        return formatter.string(from: self)
    }
}
```

## 🎨 Schritt 5: App-Einstiegspunkt

### ArbeitszeitenApp.swift (Haupt-App-Datei)
```swift
//
//  ArbeitszeitenApp.swift
//  Arbeitszeiten
//

import SwiftUI

@main
struct ArbeitszeitenApp: App {
    @StateObject private var authViewModel = AuthViewModel()
    
    var body: some Scene {
        WindowGroup {
            if authViewModel.isAuthenticated {
                HomeView()
                    .environmentObject(authViewModel)
            } else {
                LoginView()
                    .environmentObject(authViewModel)
            }
        }
    }
}
```

## ✅ Schritt 6: WICHTIG - API-URL anpassen

In `Constants.swift` **UNBEDINGT** deine tatsächliche Render.com URL eintragen:

```swift
static let baseURL = "https://DEINE-APP-NAME.onrender.com/api"
```

## 🧪 Schritt 7: App testen

1. Baue das Projekt (⌘ + B)
2. Wähle einen Simulator oder dein iPhone
3. Starte die App (⌘ + R)
4. Teste:
   - Registrierung
   - Login
   - Kategorien erstellen
   - Zeiten erfassen
   - Daten ansehen

## 📋 Checkliste

- [ ] Alle Dateien erstellt
- [ ] API-URL in Constants.swift angepasst
- [ ] App kompiliert ohne Fehler
- [ ] Login funktioniert
- [ ] Kategorien werden angezeigt
- [ ] Zeiterfassung funktioniert

## 🐛 Häufige Probleme

### "Unable to connect to API"
- Prüfe die URL in `Constants.swift`
- Stelle sicher, dass der Render.com Service läuft
- Teste die API mit Postman

### "Unauthorized"
- Token wird möglicherweise nicht korrekt gespeichert
- Prüfe KeychainManager
- Lösche die App und installiere sie neu

### Build-Fehler
- Stelle sicher, dass alle Dateien im richtigen Ordner sind
- Clean Build Folder (⌘ + Shift + K)
- Neustart von Xcode

## 📞 Support

Bei Fragen zur API siehe `README.md` im Backend-Repository.
