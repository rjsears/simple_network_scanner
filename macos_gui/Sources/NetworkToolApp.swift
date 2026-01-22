import SwiftUI
import AppKit

@main
struct NetworkToolApp: App {
    @StateObject private var appState = AppState()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .frame(minWidth: 1100, idealWidth: 1200, minHeight: 760, idealHeight: 820)
                .environmentObject(appState)
        }
        .windowStyle(.titleBar)
        .commands {
            CommandGroup(replacing: .appInfo) {
                Button("About Simple Network Host Scanner") {
                    appState.showAbout = true
                }
            }
        }
    }
}

struct ContentView: View {
    @StateObject private var model = ScanViewModel()
    @EnvironmentObject private var appState: AppState

    var body: some View {
        ZStack {
            TechBackground()

            VStack(spacing: 18) {
                HeaderView(statusText: model.statusText, isScanning: model.isScanning)

                ControlsCard(
                    startIP: $model.startIP,
                    hostCount: $model.hostCount,
                    cidr: $model.cidr,
                    isScanning: model.isScanning,
                    errorText: model.errorText,
                    onStart: model.startScan,
                    onCancel: model.cancelScan
                )

                ProgressCard(
                    progressValue: model.progressValue,
                    totalCount: model.totalCount,
                    isScanning: model.isScanning
                )

                ResultsCard(results: model.results)

                SummaryCard(results: model.results, onSelect: model.showFilter)
            }
            .padding(24)
        }
        .sheet(isPresented: $model.isFilterSheetPresented) {
            FilteredListSheet(
                status: model.activeFilter,
                results: model.filteredResults,
                onClose: model.hideFilter
            )
        }
        .sheet(isPresented: $appState.showAbout) {
            AboutSheet(onClose: { appState.showAbout = false })
        }
    }
}

struct HeaderView: View {
    let statusText: String
    let isScanning: Bool

    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 6) {
                Text("Simple Network Host Scanner")
                    .font(.system(size: 28, weight: .semibold, design: .monospaced))
                    .foregroundColor(Palette.ink)
                Text("Richard J. Sears")
                    .font(.system(size: 14, weight: .medium, design: .monospaced))
                    .foregroundColor(Palette.tealStrong)
            }
            Spacer()
            HStack(spacing: 10) {
                Circle()
                    .fill(isScanning ? Palette.green : Palette.gray)
                    .frame(width: 10, height: 10)
                Text(statusText.uppercased())
                    .font(.system(size: 12, weight: .semibold, design: .monospaced))
                    .foregroundColor(Palette.ink)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(Palette.card)
            .clipShape(Capsule())
            .overlay(
                Capsule()
                    .stroke(Palette.tealSoft, lineWidth: 1)
            )
        }
    }
}

struct ControlsCard: View {
    @Binding var startIP: String
    @Binding var hostCount: String
    @Binding var cidr: String
    let isScanning: Bool
    let errorText: String?
    let onStart: () -> Void
    let onCancel: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("Scan Parameters")
                .font(.system(size: 16, weight: .semibold, design: .monospaced))
                .foregroundColor(Palette.ink)

            HStack(spacing: 16) {
                LabeledInput(title: "Start IP", text: $startIP, placeholder: "10.0.0.1")
                LabeledInput(title: "Hosts", text: $hostCount, placeholder: "64")
                    .frame(width: 120)
                LabeledInput(title: "CIDR", text: $cidr, placeholder: "24")
                    .frame(width: 120)
                Spacer()
                HStack(spacing: 12) {
                    Button(action: onStart) {
                        Text("Start Scan")
                            .font(.system(size: 13, weight: .semibold, design: .monospaced))
                            .padding(.horizontal, 18)
                            .padding(.vertical, 10)
                            .background(Palette.tealStrong)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                    .disabled(isScanning)

                    Button(action: onCancel) {
                        Text("Cancel")
                            .font(.system(size: 13, weight: .semibold, design: .monospaced))
                            .padding(.horizontal, 18)
                            .padding(.vertical, 10)
                            .background(Palette.graySoft)
                            .foregroundColor(Palette.ink)
                            .cornerRadius(8)
                    }
                    .disabled(!isScanning)
                }
            }

            if let errorText {
                Text(errorText)
                    .font(.system(size: 12, weight: .medium, design: .monospaced))
                    .foregroundColor(Palette.red)
            }
        }
        .padding(18)
        .background(CardBackground())
    }
}

struct ProgressCard: View {
    let progressValue: Double
    let totalCount: Int
    let isScanning: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Progress")
                    .font(.system(size: 14, weight: .semibold, design: .monospaced))
                    .foregroundColor(Palette.ink)
                Spacer()
                Text("\(Int(progressValue * Double(max(1, totalCount)))) / \(totalCount)")
                    .font(.system(size: 12, weight: .medium, design: .monospaced))
                    .foregroundColor(Palette.tealStrong)
            }
            ProgressView(value: progressValue)
                .progressViewStyle(.linear)
                .tint(Palette.tealStrong)
                .scaleEffect(x: 1, y: 2, anchor: .center)
                .animation(.easeOut(duration: 0.2), value: progressValue)
            Text(isScanning ? "Active scan" : "Idle")
                .font(.system(size: 11, weight: .medium, design: .monospaced))
                .foregroundColor(Palette.gray)
        }
        .padding(18)
        .background(CardBackground())
    }
}

struct ResultsCard: View {
    let results: [HostResult]

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Results")
                .font(.system(size: 16, weight: .semibold, design: .monospaced))
                .foregroundColor(Palette.ink)

            Table(results) {
                TableColumn("IP") { result in
                    Text(result.ip)
                        .font(.system(size: 12, weight: .medium, design: .monospaced))
                }
                .width(120)
                TableColumn("Status") { result in
                    Text(result.status.rawValue)
                        .font(.system(size: 12, weight: .semibold, design: .monospaced))
                        .foregroundColor(result.status.color)
                }
                .width(80)
                TableColumn("Hostname") { result in
                    Text(result.hostname)
                        .font(.system(size: 12, weight: .medium, design: .monospaced))
                }
                .width(min: 200, ideal: 360, max: 600)
            }
            .frame(minHeight: 260)
            .tableStyle(.inset(alternatesRowBackgrounds: true))
        }
        .padding(18)
        .background(CardBackground())
    }
}

struct SummaryCard: View {
    let results: [HostResult]
    let onSelect: (HostStatus) -> Void

    var body: some View {
        let up = results.filter { $0.status == .up }.count
        let down = results.filter { $0.status == .down }.count
        let network = results.filter { $0.status == .network }.count
        let broadcast = results.filter { $0.status == .broadcast }.count

        return HStack(spacing: 18) {
            SummaryPill(label: "UP", value: up, color: Palette.green) {
                onSelect(.up)
            }
            SummaryPill(label: "DOWN", value: down, color: Palette.red) {
                onSelect(.down)
            }
            SummaryPill(label: "NET", value: network, color: Palette.cyan) {
                onSelect(.network)
            }
            SummaryPill(label: "BCAST", value: broadcast, color: Palette.purple) {
                onSelect(.broadcast)
            }
            Spacer()
        }
        .padding(18)
        .background(CardBackground())
    }
}

struct SummaryPill: View {
    let label: String
    let value: Int
    let color: Color
    let onTap: () -> Void

    var body: some View {
        Button(action: onTap) {
            HStack(spacing: 8) {
                Circle()
                    .fill(color)
                    .frame(width: 8, height: 8)
                Text(label)
                    .font(.system(size: 12, weight: .semibold, design: .monospaced))
                    .foregroundColor(Palette.ink)
                Text("\(value)")
                    .font(.system(size: 12, weight: .bold, design: .monospaced))
                    .foregroundColor(color)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(Palette.card)
            .clipShape(Capsule())
            .overlay(
                Capsule()
                    .stroke(color.opacity(0.6), lineWidth: 1)
            )
        }
        .buttonStyle(.plain)
    }
}

struct LabeledInput: View {
    let title: String
    @Binding var text: String
    let placeholder: String

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title)
                .font(.system(size: 12, weight: .semibold, design: .monospaced))
                .foregroundColor(Palette.gray)
            TextField(placeholder, text: $text)
                .textFieldStyle(.plain)
                .padding(8)
                .background(Palette.input)
                .foregroundColor(Palette.ink)
                .overlay(
                    RoundedRectangle(cornerRadius: 6)
                        .stroke(Palette.tealSoft, lineWidth: 1)
                )
        }
    }
}

struct CardBackground: View {
    var body: some View {
        RoundedRectangle(cornerRadius: 16)
            .fill(Palette.card)
            .overlay(
                RoundedRectangle(cornerRadius: 16)
                    .stroke(Palette.tealSoft.opacity(0.7), lineWidth: 1)
            )
            .shadow(color: Palette.shadow, radius: 10, x: 0, y: 6)
    }
}

struct TechBackground: View {
    var body: some View {
        ZStack {
            if let image = loadBackgroundImage() {
                Image(nsImage: image)
                    .resizable()
                    .scaledToFill()
                    .ignoresSafeArea()
                    .overlay(Color.white.opacity(0.28))
            } else {
                LinearGradient(
                    colors: [Palette.surfaceLight, Palette.surfaceMid],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                .ignoresSafeArea()
            }

            RadialGradient(
                colors: [Palette.tealSoft.opacity(0.5), Color.clear],
                center: .topTrailing,
                startRadius: 50,
                endRadius: 400
            )
            .ignoresSafeArea()

            GridOverlay()
                .opacity(0.45)
                .ignoresSafeArea()
        }
    }

    private func loadBackgroundImage() -> NSImage? {
        guard let path = Bundle.main.path(forResource: "map_background", ofType: "png") else {
            return nil
        }
        return NSImage(contentsOfFile: path)
    }
}

struct GridOverlay: View {
    var body: some View {
        GeometryReader { proxy in
            let size = proxy.size
            Path { path in
                let step: CGFloat = 40
                var x: CGFloat = 0
                while x <= size.width {
                    path.move(to: CGPoint(x: x, y: 0))
                    path.addLine(to: CGPoint(x: x, y: size.height))
                    x += step
                }
                var y: CGFloat = 0
                while y <= size.height {
                    path.move(to: CGPoint(x: 0, y: y))
                    path.addLine(to: CGPoint(x: size.width, y: y))
                    y += step
                }
            }
            .stroke(Palette.tealSoft.opacity(0.25), lineWidth: 1)
        }
    }
}

extension Array {
    func chunked(into size: Int) -> [[Element]] {
        guard size > 0 else { return [self] }
        var chunks: [[Element]] = []
        var index = 0
        while index < count {
            let end = Swift.min(index + size, count)
            chunks.append(Array(self[index..<end]))
            index = end
        }
        return chunks
    }
}

struct FilteredListSheet: View {
    let status: HostStatus?
    let results: [HostResult]
    let onClose: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Text(title)
                    .font(.system(size: 18, weight: .semibold, design: .monospaced))
                    .foregroundColor(Palette.ink)
                Spacer()
                Button("Close", action: onClose)
                    .buttonStyle(.bordered)
            }

            List(results) { result in
                Text(result.ip)
                    .font(.system(size: 12, weight: .medium, design: .monospaced))
            }
        }
        .padding(20)
        .frame(minWidth: 360, minHeight: 400)
        .background(Palette.surfaceLight)
    }

    private var title: String {
        guard let status else { return "All Hosts" }
        return "\(status.rawValue) Hosts"
    }
}

struct AboutSheet: View {
    let onClose: () -> Void

    var body: some View {
        VStack(spacing: 18) {
            HStack {
                HStack(spacing: 10) {
                    ZStack {
                        Circle()
                            .fill(Palette.tealSoft.opacity(0.35))
                            .frame(width: 34, height: 34)
                        Image(systemName: "info.circle.fill")
                            .foregroundColor(Palette.tealStrong)
                    }
                    Text("About")
                        .font(.system(size: 16, weight: .semibold, design: .monospaced))
                        .foregroundColor(Palette.ink)
                }
                Spacer()
                Button(action: onClose) {
                    Image(systemName: "xmark")
                        .foregroundColor(Palette.gray)
                        .padding(6)
                        .background(Palette.graySoft)
                        .clipShape(Circle())
                }
                .buttonStyle(.plain)
            }

            Divider()

            VStack(spacing: 6) {
                Text("Simple Network Host Scanner")
                    .font(.system(size: 20, weight: .semibold, design: .monospaced))
                    .foregroundColor(Palette.ink)
                Text("macOS Desktop Utility")
                    .font(.system(size: 12, weight: .medium, design: .monospaced))
                    .foregroundColor(Palette.gray)
                HStack(spacing: 10) {
                    Text(AppInfo.versionString)
                        .font(.system(size: 11, weight: .semibold, design: .monospaced))
                        .padding(.horizontal, 10)
                        .padding(.vertical, 4)
                        .background(Palette.tealSoft.opacity(0.35))
                        .clipShape(Capsule())
                        .foregroundColor(Palette.tealStrong)
                    Text(AppInfo.releaseDate)
                        .font(.system(size: 11, weight: .medium, design: .monospaced))
                        .foregroundColor(Palette.gray)
                }
            }

            Divider()

            Text("A simple, fast network host scanner for spotting live hosts and basic hostname discovery on local subnets.")
                .font(.system(size: 12, weight: .regular, design: .monospaced))
                .foregroundColor(Palette.gray)
                .multilineTextAlignment(.center)

            Divider()

            VStack(spacing: 6) {
                Text("Developed by")
                    .font(.system(size: 11, weight: .medium, design: .monospaced))
                    .foregroundColor(Palette.gray)
                Text("Richard J. Sears")
                    .font(.system(size: 13, weight: .semibold, design: .monospaced))
                    .foregroundColor(Palette.ink)
                Link("richardjsears@protonmail.com", destination: URL(string: "mailto:richardjsears@protonmail.com")!)
                    .font(.system(size: 12, weight: .medium, design: .monospaced))
                    .foregroundColor(Palette.tealStrong)
            }

            Divider()

            Link(destination: URL(string: "https://github.com/rjsears/simple_network_scanner")!) {
                HStack(spacing: 8) {
                    Image(systemName: "link")
                    Text("View on GitHub")
                    Image(systemName: "arrow.up.right.square")
                }
                .font(.system(size: 12, weight: .semibold, design: .monospaced))
                .padding(.horizontal, 16)
                .padding(.vertical, 10)
                .background(Palette.graySoft)
                .clipShape(RoundedRectangle(cornerRadius: 10))
                .foregroundColor(Palette.ink)
            }
            .buttonStyle(.plain)

            Button("Close", action: onClose)
                .buttonStyle(.borderedProminent)
                .tint(Palette.tealStrong)
        }
        .padding(24)
        .frame(minWidth: 520, minHeight: 380)
        .background(Palette.surfaceLight)
    }
}

enum Palette {
    static let surfaceLight = Color(red: 0.95, green: 0.97, blue: 0.99)
    static let surfaceMid = Color(red: 0.88, green: 0.92, blue: 0.96)
    static let card = Color.white.opacity(0.9)
    static let input = Color.white
    static let ink = Color(red: 0.08, green: 0.12, blue: 0.18)
    static let gray = Color(red: 0.35, green: 0.42, blue: 0.5)
    static let graySoft = Color(red: 0.9, green: 0.92, blue: 0.95)
    static let tealStrong = Color(red: 0.0, green: 0.55, blue: 0.62)
    static let tealSoft = Color(red: 0.3, green: 0.75, blue: 0.8)
    static let green = Color(red: 0.1, green: 0.6, blue: 0.3)
    static let red = Color(red: 0.82, green: 0.24, blue: 0.2)
    static let cyan = Color(red: 0.1, green: 0.6, blue: 0.7)
    static let purple = Color(red: 0.45, green: 0.35, blue: 0.7)
    static let shadow = Color.black.opacity(0.08)
}

final class AppState: ObservableObject {
    @Published var showAbout = false
}

enum AppInfo {
    static var versionString: String {
        let version = Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "1.0.0"
        return "v\(version)"
    }
    static let releaseDate = "2025-01-17"
}

@MainActor
final class ScanViewModel: ObservableObject {
    @Published var startIP = "10.0.0.1"
    @Published var hostCount = "64"
    @Published var cidr = "24"
    @Published var results: [HostResult] = []
    @Published var statusText = "Idle"
    @Published var progressValue: Double = 0
    @Published var totalCount: Int = 0
    @Published var isScanning = false
    @Published var errorText: String?
    @Published var activeFilter: HostStatus?
    @Published var isFilterSheetPresented = false

    private var scanTask: Task<Void, Never>?

    func startScan() {
        errorText = nil
        guard !isScanning else { return }
        guard let request = ScanRequest.fromInput(startIP: startIP, hostCount: hostCount, cidr: cidr) else {
            errorText = "Invalid input. Check IP, host count, and CIDR."
            return
        }

        results = []
        totalCount = request.ipList.count
        progressValue = 0
        isScanning = true
        statusText = "Scanning"

        let requestCopy = request
        scanTask = Task(priority: .userInitiated) {
            await runScan(request: requestCopy)
        }
    }

    func cancelScan() {
        scanTask?.cancel()
        scanTask = nil
        isScanning = false
        statusText = "Cancelled"
    }

    var filteredResults: [HostResult] {
        guard let filter = activeFilter else { return results }
        return results.filter { $0.status == filter }
    }

    func showFilter(_ status: HostStatus) {
        activeFilter = status
        isFilterSheetPresented = true
    }

    func hideFilter() {
        isFilterSheetPresented = false
    }

    private func runScan(request: ScanRequest) async {
        let scanner = NetworkScanner()
        let batchSize = 20
        var completed = 0
        var collected: [HostResult] = []

        for batch in request.ipList.chunked(into: batchSize) {
            if Task.isCancelled { break }

            await withTaskGroup(of: HostResult.self) { group in
                for ipInfo in batch {
                    group.addTask {
                        return scanner.scanHost(ipInfo: ipInfo)
                    }
                }

                for await result in group {
                    if Task.isCancelled { break }
                    collected.append(result)
                    completed += 1
                    let progress = Double(completed) / Double(request.ipList.count)
                    results = collected.sorted(by: { $0.ipInt < $1.ipInt })
                    progressValue = progress
                }
            }
        }

        results = collected.sorted(by: { $0.ipInt < $1.ipInt })
        progressValue = min(1.0, Double(completed) / Double(max(1, request.ipList.count)))
        isScanning = false
        statusText = Task.isCancelled ? "Cancelled" : "Complete"
    }
}
