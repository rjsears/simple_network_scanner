import Foundation
import Darwin
import SwiftUI

struct ScanRequest {
    let startIP: String
    let hostCount: Int
    let cidr: Int
    let ipList: [IPInfo]

    static func fromInput(startIP: String, hostCount: String, cidr: String) -> ScanRequest? {
        guard let hostCountValue = Int(hostCount), hostCountValue > 0 else { return nil }
        guard let cidrValue = Int(cidr), (8...32).contains(cidrValue) else { return nil }
        guard IPUtils.isValidIP(startIP) else { return nil }

        let ipList = IPUtils.generateIPList(startIP: startIP, numHosts: hostCountValue, cidr: cidrValue)
        return ScanRequest(startIP: startIP, hostCount: hostCountValue, cidr: cidrValue, ipList: ipList)
    }
}

struct IPInfo {
    let ip: String
    let type: IPType
    let ipInt: UInt32
}

enum IPType {
    case host
    case network
    case broadcast
}

struct HostResult: Identifiable {
    let id = UUID()
    let ip: String
    let status: HostStatus
    let hostname: String
    let ipInt: UInt32
}

enum HostStatus: String {
    case up = "UP"
    case down = "DOWN"
    case network = "NTWRK"
    case broadcast = "BCAST"

    var color: Color {
        switch self {
        case .up: return .green
        case .down: return .red
        case .network: return .cyan
        case .broadcast: return .purple
        }
    }
}

final class NetworkScanner {
    func scanHost(ipInfo: IPInfo) -> HostResult {
        switch ipInfo.type {
        case .network:
            return HostResult(ip: ipInfo.ip, status: .network, hostname: "-", ipInt: ipInfo.ipInt)
        case .broadcast:
            return HostResult(ip: ipInfo.ip, status: .broadcast, hostname: "-", ipInt: ipInfo.ipInt)
        case .host:
            break
        }

        let isUp = pingHost(ipInfo.ip)
        let hostname = isUp ? reverseDNS(ipInfo.ip) : "-"
        return HostResult(ip: ipInfo.ip, status: isUp ? .up : .down, hostname: hostname, ipInt: ipInfo.ipInt)
    }

    private func pingHost(_ ip: String) -> Bool {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/sbin/ping")
        process.arguments = ["-c", "1", "-W", "1000", ip]

        process.standardOutput = FileHandle.nullDevice
        process.standardError = FileHandle.nullDevice

        do {
            try process.run()
            process.waitUntilExit()
            return process.terminationStatus == 0
        } catch {
            return false
        }
    }

    private func reverseDNS(_ ip: String) -> String {
        var addr = sockaddr_in()
        addr.sin_len = UInt8(MemoryLayout<sockaddr_in>.size)
        addr.sin_family = sa_family_t(AF_INET)
        _ = ip.withCString { cstr in
            inet_pton(AF_INET, cstr, &addr.sin_addr)
        }

        var host = [CChar](repeating: 0, count: Int(NI_MAXHOST))
        let result = withUnsafePointer(to: &addr) {
            $0.withMemoryRebound(to: sockaddr.self, capacity: 1) { ptr in
                getnameinfo(ptr, socklen_t(MemoryLayout<sockaddr_in>.size), &host, socklen_t(host.count), nil, 0, NI_NAMEREQD)
            }
        }

        if result == 0 {
            return String(cString: host)
        }
        return "-"
    }
}

enum IPUtils {
    static func isValidIP(_ ip: String) -> Bool {
        let parts = ip.split(separator: ".")
        if parts.count != 4 { return false }
        for part in parts {
            guard let value = Int(String(part)), (0...255).contains(value) else { return false }
        }
        return true
    }

    static func ipToInt(_ ip: String) -> UInt32? {
        let parts = ip.split(separator: ".")
        if parts.count != 4 { return nil }
        guard
            let p0 = UInt32(String(parts[0])),
            let p1 = UInt32(String(parts[1])),
            let p2 = UInt32(String(parts[2])),
            let p3 = UInt32(String(parts[3]))
        else {
            return nil
        }
        return (p0 << 24) + (p1 << 16) + (p2 << 8) + p3
    }

    static func intToIP(_ value: UInt32) -> String {
        let p0 = (value >> 24) & 255
        let p1 = (value >> 16) & 255
        let p2 = (value >> 8) & 255
        let p3 = value & 255
        return "\(p0).\(p1).\(p2).\(p3)"
    }

    static func getIPType(ipInt: UInt32, cidr: Int) -> IPType {
        if cidr >= 31 { return .host }
        let blockSize = UInt32(1) << UInt32(32 - cidr)
        let network = (ipInt / blockSize) * blockSize
        let broadcast = network + blockSize - 1
        if ipInt == network { return .network }
        if ipInt == broadcast { return .broadcast }
        return .host
    }

    static func generateIPList(startIP: String, numHosts: Int, cidr: Int) -> [IPInfo] {
        guard let start = ipToInt(startIP) else { return [] }
        var list: [IPInfo] = []
        var current = start
        var hostsFound = 0

        while hostsFound < numHosts {
            let type = getIPType(ipInt: current, cidr: cidr)
            let ipStr = intToIP(current)
            list.append(IPInfo(ip: ipStr, type: type, ipInt: current))
            if type == .host {
                hostsFound += 1
            }
            if current == UInt32.max { break }
            current += 1
        }

        return list
    }
}
