import AppKit

let outputPath = CommandLine.arguments.dropFirst().first ?? "AppIcon.png"
let size: CGFloat = 1024
let image = NSImage(size: NSSize(width: size, height: size))

image.lockFocus()

let rect = NSRect(x: 0, y: 0, width: size, height: size)
let background = NSGradient(colors: [
    NSColor(calibratedRed: 0.95, green: 0.97, blue: 0.99, alpha: 1.0),
    NSColor(calibratedRed: 0.82, green: 0.89, blue: 0.96, alpha: 1.0)
])
background?.draw(in: rect, angle: -45)

let borderPath = NSBezierPath(roundedRect: rect.insetBy(dx: 24, dy: 24), xRadius: 80, yRadius: 80)
NSColor(calibratedRed: 0.2, green: 0.6, blue: 0.7, alpha: 0.25).setStroke()
borderPath.lineWidth = 12
borderPath.stroke()

let gridPath = NSBezierPath()
let step: CGFloat = 96
var x: CGFloat = 0
while x <= size {
    gridPath.move(to: CGPoint(x: x, y: 0))
    gridPath.line(to: CGPoint(x: x, y: size))
    x += step
}
var y: CGFloat = 0
while y <= size {
    gridPath.move(to: CGPoint(x: 0, y: y))
    gridPath.line(to: CGPoint(x: size, y: y))
    y += step
}
NSColor(calibratedRed: 0.15, green: 0.55, blue: 0.65, alpha: 0.15).setStroke()
gridPath.lineWidth = 4
gridPath.stroke()

let center = CGPoint(x: size * 0.55, y: size * 0.55)
let radarRadius: CGFloat = 300
let radarPath = NSBezierPath(ovalIn: CGRect(x: center.x - radarRadius, y: center.y - radarRadius, width: radarRadius * 2, height: radarRadius * 2))
NSColor(calibratedRed: 0.0, green: 0.55, blue: 0.62, alpha: 0.25).setFill()
radarPath.fill()
NSColor(calibratedRed: 0.0, green: 0.55, blue: 0.62, alpha: 0.8).setStroke()
radarPath.lineWidth = 10
radarPath.stroke()

let ringCount = 3
for index in 1...ringCount {
    let ringRadius = radarRadius * CGFloat(index) / CGFloat(ringCount + 1)
    let ring = NSBezierPath(ovalIn: CGRect(x: center.x - ringRadius, y: center.y - ringRadius, width: ringRadius * 2, height: ringRadius * 2))
    NSColor(calibratedRed: 0.0, green: 0.55, blue: 0.62, alpha: 0.35).setStroke()
    ring.lineWidth = 6
    ring.stroke()
}

let needlePath = NSBezierPath()
needlePath.move(to: center)
needlePath.line(to: CGPoint(x: center.x + 240, y: center.y + 120))
NSColor(calibratedRed: 0.9, green: 0.3, blue: 0.2, alpha: 0.8).setStroke()
needlePath.lineWidth = 12
needlePath.stroke()

func drawNode(_ point: CGPoint, color: NSColor) {
    let node = NSBezierPath(ovalIn: CGRect(x: point.x - 18, y: point.y - 18, width: 36, height: 36))
    color.setFill()
    node.fill()
    NSColor.white.setStroke()
    node.lineWidth = 4
    node.stroke()
}

drawNode(CGPoint(x: center.x - 140, y: center.y + 80), color: NSColor(calibratedRed: 0.1, green: 0.6, blue: 0.3, alpha: 1.0))
drawNode(CGPoint(x: center.x + 60, y: center.y - 120), color: NSColor(calibratedRed: 0.82, green: 0.24, blue: 0.2, alpha: 1.0))
drawNode(CGPoint(x: center.x + 160, y: center.y + 170), color: NSColor(calibratedRed: 0.45, green: 0.35, blue: 0.7, alpha: 1.0))

let label = "NET"
let attrs: [NSAttributedString.Key: Any] = [
    .font: NSFont.monospacedSystemFont(ofSize: 120, weight: .bold),
    .foregroundColor: NSColor(calibratedRed: 0.08, green: 0.12, blue: 0.18, alpha: 1.0)
]
let textSize = label.size(withAttributes: attrs)
let textPoint = CGPoint(x: size * 0.18, y: size * 0.18)
label.draw(at: textPoint, withAttributes: attrs)

image.unlockFocus()

guard let tiffData = image.tiffRepresentation,
      let rep = NSBitmapImageRep(data: tiffData),
      let pngData = rep.representation(using: .png, properties: [:]) else {
    fatalError("Failed to create PNG")
}

try pngData.write(to: URL(fileURLWithPath: outputPath))
print("Wrote \(outputPath)")
