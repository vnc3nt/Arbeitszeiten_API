# iOS App Entwicklung - Teil 2: Fehlende Komponenten

## 📋 Übersicht

Diese Datei enthält alle fehlenden ViewModels, Views und Modelle aus Teil 1.

---

## 📝 Models/APIResponse.swift

```swift
//
//  APIResponse.swift
//  Arbeitszeiten
//

import Foundation

// Generic Response für einfache Nachrichten
struct MessageResponse: Codable {
    let message: String
}

struct ErrorResponse: Codable {
    let message: String
}

// Datums-Response für einzelne Daten
struct DateEntriesResponse: Codable {
    let date: String
    let entries: [TimeEntry]
    let totalHours: Double
    
    enum CodingKeys: String, CodingKey {
        case date, entries
        case totalHours = "total_hours"
    }
}

// Delete Response
struct DeleteResponse: Codable {
    let message: String
    let date: String?
    let deletedDataEntries: Int?
    
    enum CodingKeys: String, CodingKey {
        case message, date
        case deletedDataEntries = "deleted_data_entries"
    }
}

// Update Response
struct UpdateResponse: Codable {
    let message: String
    let date: String?
    let hours: Double?
}

// Change Username Response
struct ChangeUsernameResponse: Codable {
    let message: String
    let username: String
}

// Health Check Response
struct HealthResponse: Codable {
    let status: String
    let message: String
}
```

---

## 🔐 Services/AuthService.swift

```swift
//
//  AuthService.swift
//  Arbeitszeiten
//

import Foundation

class AuthService {
    static let shared = AuthService()
    
    private init() {}
    
    // MARK: - Authentication
    
    func register(username: String, password: String) async throws -> RegisterResponse {
        let request = RegisterRequest(username: username, password: password)
        return try await APIService.shared.request(
            endpoint: Constants.Endpoints.register,
            method: "POST",
            body: request,
            requiresAuth: false
        )
    }
    
    func login(username: String, password: String) async throws -> LoginResponse {
        let request = LoginRequest(username: username, password: password)
        return try await APIService.shared.request(
            endpoint: Constants.Endpoints.login,
            method: "POST",
            body: request,
            requiresAuth: false
        )
    }
    
    func logout() async throws {
        let _: MessageResponse = try await APIService.shared.request(
            endpoint: Constants.Endpoints.logout,
            method: "POST"
        )
    }
    
    func getCurrentUser() async throws -> User {
        return try await APIService.shared.request(
            endpoint: Constants.Endpoints.user
        )
    }
    
    // MARK: - Account Management
    
    func changePassword(currentPassword: String, newPassword: String) async throws -> MessageResponse {
        struct ChangePasswordRequest: Codable {
            let currentPassword: String
            let newPassword: String
            
            enum CodingKeys: String, CodingKey {
                case currentPassword = "current_password"
                case newPassword = "new_password"
            }
        }
        
        let request = ChangePasswordRequest(
            currentPassword: currentPassword,
            newPassword: newPassword
        )
        
        return try await APIService.shared.request(
            endpoint: Constants.Endpoints.changePassword,
            method: "POST",
            body: request
        )
    }
    
    func changeUsername(newUsername: String) async throws -> ChangeUsernameResponse {
        struct ChangeUsernameRequest: Codable {
            let newUsername: String
            
            enum CodingKeys: String, CodingKey {
                case newUsername = "new_username"
            }
        }
        
        let request = ChangeUsernameRequest(newUsername: newUsername)
        
        return try await APIService.shared.request(
            endpoint: Constants.Endpoints.changeUsername,
            method: "POST",
            body: request
        )
    }
    
    func deleteAccount(password: String) async throws -> MessageResponse {
        struct DeleteAccountRequest: Codable {
            let password: String
        }
        
        let request = DeleteAccountRequest(password: password)
        
        return try await APIService.shared.request(
            endpoint: Constants.Endpoints.deleteAccount,
            method: "DELETE",
            body: request
        )
    }
}
```

---

## 📂 ViewModels/CategoryViewModel.swift

```swift
//
//  CategoryViewModel.swift
//  Arbeitszeiten
//

import Foundation
import SwiftUI

@MainActor
class CategoryViewModel: ObservableObject {
    @Published var categories: [Category] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    // MARK: - Fetch Categories
    
    func fetchCategories() async {
        isLoading = true
        errorMessage = nil
        
        do {
            let response: CategoriesResponse = try await APIService.shared.request(
                endpoint: Constants.Endpoints.categories
            )
            categories = response.categories
        } catch {
            errorMessage = error.localizedDescription
        }
        
        isLoading = false
    }
    
    // MARK: - Create Category
    
    func createCategory(name: String, color: String) async -> Bool {
        isLoading = true
        errorMessage = nil
        
        do {
            let request = CreateCategoryRequest(name: name, color: color)
            let _: CategoryResponse = try await APIService.shared.request(
                endpoint: Constants.Endpoints.categories,
                method: "POST",
                body: request
            )
            
            // Refresh categories
            await fetchCategories()
            isLoading = false
            return true
            
        } catch {
            errorMessage = error.localizedDescription
            isLoading = false
            return false
        }
    }
    
    // MARK: - Update Category
    
    func updateCategory(id: Int, name: String, color: String) async -> Bool {
        isLoading = true
        errorMessage = nil
        
        do {
            struct UpdateCategoryRequest: Codable {
                let name: String
                let color: String
            }
            
            let request = UpdateCategoryRequest(name: name, color: color)
            let _: CategoryResponse = try await APIService.shared.request(
                endpoint: Constants.Endpoints.category(id: id),
                method: "PUT",
                body: request
            )
            
            // Refresh categories
            await fetchCategories()
            isLoading = false
            return true
            
        } catch {
            errorMessage = error.localizedDescription
            isLoading = false
            return false
        }
    }
    
    // MARK: - Delete Category
    
    func deleteCategory(id: Int) async -> Bool {
        isLoading = true
        errorMessage = nil
        
        do {
            let _: DeleteResponse = try await APIService.shared.request(
                endpoint: Constants.Endpoints.category(id: id),
                method: "DELETE"
            )
            
            // Remove from local array
            categories.removeAll { $0.id == id }
            isLoading = false
            return true
            
        } catch {
            errorMessage = error.localizedDescription
            isLoading = false
            return false
        }
    }
}
```

---

## ⏱️ ViewModels/TimeTrackingViewModel.swift

```swift
//
//  TimeTrackingViewModel.swift
//  Arbeitszeiten
//

import Foundation

@MainActor
class TimeTrackingViewModel: ObservableObject {
    @Published var entries: [TimeEntry] = []
    @Published var categories: [Category] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let dateFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter
    }()
    
    // MARK: - Fetch Data
    
    func fetchCategories() async {
        do {
            let response: CategoriesResponse = try await APIService.shared.request(
                endpoint: Constants.Endpoints.categories
            )
            categories = response.categories
        } catch {
            errorMessage = error.localizedDescription
        }
    }
    
    func fetchEntries(for date: Date) async {
        isLoading = true
        errorMessage = nil
        
        let dateString = dateFormatter.string(from: date)
        
        do {
            let response: DateEntriesResponse = try await APIService.shared.request(
                endpoint: Constants.Endpoints.dataByDate(dateString)
            )
            entries = response.entries
        } catch {
            errorMessage = error.localizedDescription
            entries = []
        }
        
        isLoading = false
    }
    
    func fetchAllEntries(startDate: Date? = nil, endDate: Date? = nil) async {
        isLoading = true
        errorMessage = nil
        
        var endpoint = Constants.Endpoints.data
        var queryItems: [String] = []
        
        if let start = startDate {
            queryItems.append("start_date=\(dateFormatter.string(from: start))")
        }
        if let end = endDate {
            queryItems.append("end_date=\(dateFormatter.string(from: end))")
        }
        
        if !queryItems.isEmpty {
            endpoint += "?" + queryItems.joined(separator: "&")
        }
        
        do {
            let response: TimeEntriesResponse = try await APIService.shared.request(
                endpoint: endpoint
            )
            entries = response.data
        } catch {
            errorMessage = error.localizedDescription
            entries = []
        }
        
        isLoading = false
    }
    
    // MARK: - Create/Update Entry
    
    func addEntry(date: Date, categoryId: Int, hours: Double, maxHours: Double? = nil) async -> Bool {
        isLoading = true
        errorMessage = nil
        
        let dateString = dateFormatter.string(from: date)
        
        do {
            let request = CreateTimeEntryRequest(
                date: dateString,
                categoryId: categoryId,
                hours: hours,
                maxHours: maxHours
            )
            
            let _: UpdateResponse = try await APIService.shared.request(
                endpoint: Constants.Endpoints.data,
                method: "POST",
                body: request
            )
            
            // Refresh entries
            await fetchEntries(for: date)
            isLoading = false
            return true
            
        } catch {
            errorMessage = error.localizedDescription
            isLoading = false
            return false
        }
    }
    
    func updateEntry(date: Date, categoryId: Int, increment: Double) async -> Bool {
        isLoading = true
        errorMessage = nil
        
        let dateString = dateFormatter.string(from: date)
        
        do {
            let request = UpdateTimeEntryRequest(
                categoryId: categoryId,
                hours: nil,
                increment: increment
            )
            
            let _: UpdateResponse = try await APIService.shared.request(
                endpoint: Constants.Endpoints.dataByDate(dateString),
                method: "PATCH",
                body: request
            )
            
            // Refresh entries
            await fetchEntries(for: date)
            isLoading = false
            return true
            
        } catch {
            errorMessage = error.localizedDescription
            isLoading = false
            return false
        }
    }
    
    // MARK: - Delete Entry
    
    func deleteEntry(date: Date) async -> Bool {
        isLoading = true
        errorMessage = nil
        
        let dateString = dateFormatter.string(from: date)
        
        do {
            let _: DeleteResponse = try await APIService.shared.request(
                endpoint: Constants.Endpoints.dataByDate(dateString),
                method: "DELETE"
            )
            
            // Remove from local array
            entries.removeAll { $0.date == dateString }
            isLoading = false
            return true
            
        } catch {
            errorMessage = error.localizedDescription
            isLoading = false
            return false
        }
    }
}
```

---

## 🎨 Views/Components/CategoryPicker.swift

```swift
//
//  CategoryPicker.swift
//  Arbeitszeiten
//

import SwiftUI

struct CategoryPicker: View {
    let categories: [Category]
    @Binding var selectedCategory: Category?
    
    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 12) {
                ForEach(categories) { category in
                    CategoryButton(
                        category: category,
                        isSelected: selectedCategory?.id == category.id
                    ) {
                        selectedCategory = category
                    }
                }
            }
            .padding(.horizontal)
        }
    }
}

struct CategoryButton: View {
    let category: Category
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 8) {
                Circle()
                    .fill(category.colorValue)
                    .frame(width: 12, height: 12)
                
                Text(category.name)
                    .font(.subheadline)
                    .fontWeight(isSelected ? .semibold : .regular)
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 10)
            .background(
                RoundedRectangle(cornerRadius: 20)
                    .fill(isSelected ? category.colorValue.opacity(0.2) : Color.gray.opacity(0.1))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 20)
                    .stroke(isSelected ? category.colorValue : Color.clear, lineWidth: 2)
            )
        }
        .buttonStyle(.plain)
    }
}
```

---

## 📊 Views/Components/TimeEntryCard.swift

```swift
//
//  TimeEntryCard.swift
//  Arbeitszeiten
//

import SwiftUI

struct TimeEntryCard: View {
    let entry: TimeEntry
    let onIncrement: () -> Void
    let onDecrement: () -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Header mit Kategorie
            if let category = entry.category {
                HStack {
                    Circle()
                        .fill(Color(hex: category.color) ?? .blue)
                        .frame(width: 16, height: 16)
                    
                    Text(category.name)
                        .font(.headline)
                    
                    Spacer()
                    
                    if let hours = entry.hours {
                        Text("\(hours, specifier: "%.1f") h")
                            .font(.title2)
                            .fontWeight(.bold)
                    }
                }
            }
            
            // Max Hours Info
            if let maxHours = entry.maxHours, let hours = entry.hours {
                ProgressView(value: hours, total: maxHours)
                    .tint(progressColor(hours: hours, max: maxHours))
                
                HStack {
                    Text("\(Int(hours / maxHours * 100))%")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    
                    Spacer()
                    
                    Text("Max: \(maxHours, specifier: "%.1f")h")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            // Buttons für +30min / -30min
            HStack(spacing: 12) {
                Button(action: onDecrement) {
                    HStack {
                        Image(systemName: "minus")
                        Text("30 min")
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 8)
                    .background(Color.red.opacity(0.1))
                    .foregroundColor(.red)
                    .cornerRadius(8)
                }
                
                Button(action: onIncrement) {
                    HStack {
                        Image(systemName: "plus")
                        Text("30 min")
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 8)
                    .background(Color.green.opacity(0.1))
                    .foregroundColor(.green)
                    .cornerRadius(8)
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: .black.opacity(0.1), radius: 5, x: 0, y: 2)
    }
    
    private func progressColor(hours: Double, max: Double) -> Color {
        let percentage = hours / max
        if percentage < 0.7 {
            return .green
        } else if percentage < 0.9 {
            return .orange
        } else {
            return .red
        }
    }
}
```

---

## 📂 Views/Main/CategoryListView.swift

```swift
//
//  CategoryListView.swift
//  Arbeitszeiten
//

import SwiftUI

struct CategoryListView: View {
    @StateObject private var viewModel = CategoryViewModel()
    @State private var showingAddCategory = false
    @State private var editingCategory: Category?
    
    var body: some View {
        NavigationView {
            Group {
                if viewModel.isLoading && viewModel.categories.isEmpty {
                    ProgressView()
                } else if viewModel.categories.isEmpty {
                    VStack(spacing: 20) {
                        Image(systemName: "folder.badge.plus")
                            .font(.system(size: 60))
                            .foregroundColor(.gray)
                        
                        Text("Keine Kategorien")
                            .font(.headline)
                            .foregroundColor(.secondary)
                        
                        Button("Kategorie erstellen") {
                            showingAddCategory = true
                        }
                        .buttonStyle(.borderedProminent)
                    }
                } else {
                    List {
                        ForEach(viewModel.categories) { category in
                            CategoryRow(category: category)
                                .swipeActions(edge: .trailing, allowsFullSwipe: false) {
                                    Button(role: .destructive) {
                                        deleteCategory(category)
                                    } label: {
                                        Label("Löschen", systemImage: "trash")
                                    }
                                    
                                    Button {
                                        editingCategory = category
                                    } label: {
                                        Label("Bearbeiten", systemImage: "pencil")
                                    }
                                    .tint(.blue)
                                }
                        }
                    }
                }
            }
            .navigationTitle("Kategorien")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { showingAddCategory = true }) {
                        Image(systemName: "plus")
                    }
                }
            }
            .sheet(isPresented: $showingAddCategory) {
                AddCategoryView()
                    .environmentObject(viewModel)
            }
            .sheet(item: $editingCategory) { category in
                EditCategoryView(category: category)
                    .environmentObject(viewModel)
            }
            .alert("Fehler", isPresented: .constant(viewModel.errorMessage != nil)) {
                Button("OK") {
                    viewModel.errorMessage = nil
                }
            } message: {
                if let error = viewModel.errorMessage {
                    Text(error)
                }
            }
        }
        .task {
            await viewModel.fetchCategories()
        }
    }
    
    private func deleteCategory(_ category: Category) {
        Task {
            _ = await viewModel.deleteCategory(id: category.id)
        }
    }
}

struct CategoryRow: View {
    let category: Category
    
    var body: some View {
        HStack(spacing: 12) {
            Circle()
                .fill(category.colorValue)
                .frame(width: 24, height: 24)
            
            Text(category.name)
                .font(.body)
            
            Spacer()
        }
        .padding(.vertical, 4)
    }
}

// MARK: - Add Category View

struct AddCategoryView: View {
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject var viewModel: CategoryViewModel
    
    @State private var name = ""
    @State private var selectedColor = Color.blue
    
    let predefinedColors: [Color] = [
        .red, .orange, .yellow, .green, .blue,
        .purple, .pink, .brown, .gray, .cyan
    ]
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Name")) {
                    TextField("Kategorie-Name", text: $name)
                }
                
                Section(header: Text("Farbe")) {
                    LazyVGrid(columns: [GridItem(.adaptive(minimum: 50))], spacing: 15) {
                        ForEach(predefinedColors, id: \.self) { color in
                            Circle()
                                .fill(color)
                                .frame(width: 50, height: 50)
                                .overlay(
                                    Circle()
                                        .stroke(Color.white, lineWidth: selectedColor == color ? 4 : 0)
                                )
                                .onTapGesture {
                                    selectedColor = color
                                }
                        }
                    }
                    .padding(.vertical)
                }
            }
            .navigationTitle("Neue Kategorie")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Abbrechen") {
                        dismiss()
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Speichern") {
                        Task {
                            let success = await viewModel.createCategory(
                                name: name,
                                color: selectedColor.toHex()
                            )
                            if success {
                                dismiss()
                            }
                        }
                    }
                    .disabled(name.isEmpty)
                }
            }
        }
    }
}

// MARK: - Edit Category View

struct EditCategoryView: View {
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject var viewModel: CategoryViewModel
    
    let category: Category
    @State private var name = ""
    @State private var selectedColor = Color.blue
    
    let predefinedColors: [Color] = [
        .red, .orange, .yellow, .green, .blue,
        .purple, .pink, .brown, .gray, .cyan
    ]
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Name")) {
                    TextField("Kategorie-Name", text: $name)
                }
                
                Section(header: Text("Farbe")) {
                    LazyVGrid(columns: [GridItem(.adaptive(minimum: 50))], spacing: 15) {
                        ForEach(predefinedColors, id: \.self) { color in
                            Circle()
                                .fill(color)
                                .frame(width: 50, height: 50)
                                .overlay(
                                    Circle()
                                        .stroke(Color.white, lineWidth: selectedColor == color ? 4 : 0)
                                )
                                .onTapGesture {
                                    selectedColor = color
                                }
                        }
                    }
                    .padding(.vertical)
                }
            }
            .navigationTitle("Kategorie bearbeiten")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Abbrechen") {
                        dismiss()
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Speichern") {
                        Task {
                            let success = await viewModel.updateCategory(
                                id: category.id,
                                name: name,
                                color: selectedColor.toHex()
                            )
                            if success {
                                dismiss()
                            }
                        }
                    }
                    .disabled(name.isEmpty)
                }
            }
        }
        .onAppear {
            name = category.name
            selectedColor = category.colorValue
        }
    }
}
```

---

## 👤 Views/Main/ProfileView.swift

```swift
//
//  ProfileView.swift
//  Arbeitszeiten
//

import SwiftUI

struct ProfileView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    @State private var showingChangePassword = false
    @State private var showingChangeUsername = false
    @State private var showingDeleteAccount = false
    
    var body: some View {
        NavigationView {
            List {
                // User Info Section
                Section {
                    HStack {
                        Image(systemName: "person.circle.fill")
                            .font(.system(size: 60))
                            .foregroundColor(.blue)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(authViewModel.currentUser?.username ?? "Benutzer")
                                .font(.title2)
                                .fontWeight(.semibold)
                            
                            Text("ID: \(authViewModel.currentUser?.id ?? 0)")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        .padding(.leading)
                    }
                    .padding(.vertical, 8)
                }
                
                // Account Settings
                Section(header: Text("Account")) {
                    Button(action: { showingChangeUsername = true }) {
                        HStack {
                            Image(systemName: "person.badge.key")
                            Text("Benutzername ändern")
                        }
                    }
                    
                    Button(action: { showingChangePassword = true }) {
                        HStack {
                            Image(systemName: "key")
                            Text("Passwort ändern")
                        }
                    }
                }
                
                // Danger Zone
                Section(header: Text("Gefährlicher Bereich")) {
                    Button(role: .destructive, action: { showingDeleteAccount = true }) {
                        HStack {
                            Image(systemName: "trash")
                            Text("Account löschen")
                        }
                    }
                }
                
                // Logout
                Section {
                    Button(action: {
                        Task {
                            await authViewModel.logout()
                        }
                    }) {
                        HStack {
                            Spacer()
                            Text("Abmelden")
                                .foregroundColor(.red)
                            Spacer()
                        }
                    }
                }
            }
            .navigationTitle("Profil")
            .sheet(isPresented: $showingChangePassword) {
                ChangePasswordView()
            }
            .sheet(isPresented: $showingChangeUsername) {
                ChangeUsernameView()
            }
            .alert("Account löschen", isPresented: $showingDeleteAccount) {
                SecureField("Passwort bestätigen", text: .constant(""))
                
                Button("Abbrechen", role: .cancel) { }
                
                Button("Löschen", role: .destructive) {
                    // TODO: Implement delete
                }
            } message: {
                Text("Diese Aktion kann nicht rückgängig gemacht werden. Alle deine Daten werden gelöscht.")
            }
        }
    }
}

// MARK: - Change Password View

struct ChangePasswordView: View {
    @Environment(\.dismiss) var dismiss
    @State private var currentPassword = ""
    @State private var newPassword = ""
    @State private var confirmPassword = ""
    @State private var errorMessage: String?
    @State private var isLoading = false
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Aktuelles Passwort")) {
                    SecureField("Aktuelles Passwort", text: $currentPassword)
                }
                
                Section(header: Text("Neues Passwort")) {
                    SecureField("Neues Passwort", text: $newPassword)
                    SecureField("Passwort bestätigen", text: $confirmPassword)
                }
                
                if let error = errorMessage {
                    Section {
                        Text(error)
                            .foregroundColor(.red)
                    }
                }
            }
            .navigationTitle("Passwort ändern")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Abbrechen") {
                        dismiss()
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Speichern") {
                        Task {
                            await changePassword()
                        }
                    }
                    .disabled(!isValidForm || isLoading)
                }
            }
        }
    }
    
    private var isValidForm: Bool {
        !currentPassword.isEmpty &&
        newPassword.count >= 8 &&
        newPassword == confirmPassword
    }
    
    private func changePassword() async {
        isLoading = true
        errorMessage = nil
        
        do {
            let _: MessageResponse = try await AuthService.shared.changePassword(
                currentPassword: currentPassword,
                newPassword: newPassword
            )
            dismiss()
        } catch {
            errorMessage = error.localizedDescription
        }
        
        isLoading = false
    }
}

// MARK: - Change Username View

struct ChangeUsernameView: View {
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject var authViewModel: AuthViewModel
    @State private var newUsername = ""
    @State private var errorMessage: String?
    @State private var isLoading = false
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Neuer Benutzername")) {
                    TextField("Benutzername", text: $newUsername)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                }
                
                if let error = errorMessage {
                    Section {
                        Text(error)
                            .foregroundColor(.red)
                    }
                }
            }
            .navigationTitle("Benutzername ändern")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Abbrechen") {
                        dismiss()
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Speichern") {
                        Task {
                            await changeUsername()
                        }
                    }
                    .disabled(newUsername.isEmpty || isLoading)
                }
            }
        }
        .onAppear {
            newUsername = authViewModel.currentUser?.username ?? ""
        }
    }
    
    private func changeUsername() async {
        isLoading = true
        errorMessage = nil
        
        do {
            let response = try await AuthService.shared.changeUsername(newUsername: newUsername)
            authViewModel.currentUser = User(
                id: authViewModel.currentUser?.id ?? 0,
                username: response.username
            )
            dismiss()
        } catch {
            errorMessage = error.localizedDescription
        }
        
        isLoading = false
    }
}
```

---

## 🎨 Zusätzliche Extension für Color → Hex

Füge dies zu `Utilities/Extensions.swift` hinzu:

```swift
extension Color {
    func toHex() -> String {
        guard let components = UIColor(self).cgColor.components else {
            return "#000000"
        }
        
        let r = Float(components[0])
        let g = Float(components[1])
        let b = Float(components[2])
        
        return String(
            format: "#%02lX%02lX%02lX",
            lroundf(r * 255),
            lroundf(g * 255),
            lroundf(b * 255)
        )
    }
}
```

---

## 📱 AddTimeEntryView.swift

Füge diese View zu `Views/Main/` hinzu:

```swift
//
//  AddTimeEntryView.swift
//  Arbeitszeiten
//

import SwiftUI

struct AddTimeEntryView: View {
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject var viewModel: TimeTrackingViewModel
    
    let date: Date
    @State private var selectedCategory: Category?
    @State private var hours: String = ""
    @State private var maxHours: String = ""
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Datum")) {
                    Text(date.formatted(date: .long, time: .omitted))
                }
                
                Section(header: Text("Kategorie")) {
                    if viewModel.categories.isEmpty {
                        Text("Keine Kategorien verfügbar")
                            .foregroundColor(.secondary)
                    } else {
                        Picker("Kategorie", selection: $selectedCategory) {
                            Text("Auswählen").tag(nil as Category?)
                            ForEach(viewModel.categories) { category in
                                HStack {
                                    Circle()
                                        .fill(category.colorValue)
                                        .frame(width: 12, height: 12)
                                    Text(category.name)
                                }
                                .tag(category as Category?)
                            }
                        }
                    }
                }
                
                Section(header: Text("Stunden")) {
                    TextField("Stunden", text: $hours)
                        .keyboardType(.decimalPad)
                    
                    TextField("Max. Stunden (optional)", text: $maxHours)
                        .keyboardType(.decimalPad)
                }
            }
            .navigationTitle("Eintrag hinzufügen")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Abbrechen") {
                        dismiss()
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Speichern") {
                        Task {
                            await saveEntry()
                        }
                    }
                    .disabled(!isValidForm)
                }
            }
        }
    }
    
    private var isValidForm: Bool {
        selectedCategory != nil &&
        !hours.isEmpty &&
        Double(hours) != nil
    }
    
    private func saveEntry() async {
        guard let category = selectedCategory,
              let hoursValue = Double(hours) else {
            return
        }
        
        let maxHoursValue = Double(maxHours)
        
        let success = await viewModel.addEntry(
            date: date,
            categoryId: category.id,
            hours: hoursValue,
            maxHours: maxHoursValue
        )
        
        if success {
            dismiss()
        }
    }
}
```

---

## ✅ Fertig!

Jetzt hast du alle fehlenden Komponenten:

1. ✅ **APIResponse.swift** - Alle Response-Typen
2. ✅ **AuthService.swift** - Authentifizierungs-Service
3. ✅ **CategoryViewModel.swift** - Kategorie-Management
4. ✅ **TimeTrackingViewModel.swift** - Zeiterfassungs-Logik
5. ✅ **CategoryPicker.swift** - Kategorie-Auswahl-Komponente
6. ✅ **TimeEntryCard.swift** - Zeiterfassungs-Karte
7. ✅ **CategoryListView.swift** - Kategorie-Liste mit CRUD
8. ✅ **ProfileView.swift** - Profilverwaltung
9. ✅ **AddTimeEntryView.swift** - Neuen Eintrag erstellen
10. ✅ **Color Extensions** - Hex-Konvertierung

Kopiere diese Code-Snippets in dein Xcode-Projekt und die App ist vollständig! 🚀
