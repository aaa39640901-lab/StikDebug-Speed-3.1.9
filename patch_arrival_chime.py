from pathlib import Path
import sys

ROOT = Path(sys.argv[1])
p = ROOT / 'StikDebug/Views/MapSelectionView.swift'
text = p.read_text(encoding='utf-8')

# AVAudioPlayer is used to synthesize a tiny two-note aircraft-style chime in memory;
# no external audio asset is required.
if 'import AVFoundation' not in text:
    text = text.replace('import SwiftUI\n', 'import SwiftUI\nimport AVFoundation\n', 1)

marker = 'private struct CoordinateSnapshot: Equatable {'
helper = r'''private final class RouteArrivalChime {
    private static var player: AVAudioPlayer?

    static func play() {
        do {
            let session = AVAudioSession.sharedInstance()
            try session.setCategory(.playback, mode: .default, options: [.mixWithOthers])
            try session.setActive(true)

            let sampleRate = 44_100.0
            let firstDuration = 0.16
            let gapDuration = 0.08
            let secondDuration = 0.22
            let totalSamples = Int((firstDuration + gapDuration + secondDuration) * sampleRate)
            var pcm = [Int16](repeating: 0, count: totalSamples)

            func fillTone(start: Int, duration: Double, frequency: Double) {
                let count = Int(duration * sampleRate)
                for i in 0..<count {
                    let t = Double(i) / sampleRate
                    let fadeIn = min(1.0, t / 0.012)
                    let fadeOut = min(1.0, Double(count - i) / (sampleRate * 0.035))
                    let envelope = min(fadeIn, fadeOut)
                    let sample = sin(2.0 * Double.pi * frequency * t) * 0.34 * envelope
                    pcm[start + i] = Int16(max(-1.0, min(1.0, sample)) * Double(Int16.max))
                }
            }

            let firstStart = 0
            let secondStart = Int((firstDuration + gapDuration) * sampleRate)
            fillTone(start: firstStart, duration: firstDuration, frequency: 880.0)
            fillTone(start: secondStart, duration: secondDuration, frequency: 660.0)

            var data = Data()
            data.append(contentsOf: Array("RIFF".utf8))
            var fileSize = UInt32(36 + pcm.count * 2).littleEndian
            data.append(Data(bytes: &fileSize, count: 4))
            data.append(contentsOf: Array("WAVEfmt ".utf8))
            var fmtSize = UInt32(16).littleEndian
            data.append(Data(bytes: &fmtSize, count: 4))
            var audioFormat = UInt16(1).littleEndian
            data.append(Data(bytes: &audioFormat, count: 2))
            var channels = UInt16(1).littleEndian
            data.append(Data(bytes: &channels, count: 2))
            var rate = UInt32(sampleRate).littleEndian
            data.append(Data(bytes: &rate, count: 4))
            var byteRate = UInt32(sampleRate * 2).littleEndian
            data.append(Data(bytes: &byteRate, count: 4))
            var blockAlign = UInt16(2).littleEndian
            data.append(Data(bytes: &blockAlign, count: 2))
            var bits = UInt16(16).littleEndian
            data.append(Data(bytes: &bits, count: 2))
            data.append(contentsOf: Array("data".utf8))
            var dataSize = UInt32(pcm.count * 2).littleEndian
            data.append(Data(bytes: &dataSize, count: 4))
            pcm.withUnsafeBytes { data.append(contentsOf: $0) }

            let player = try AVAudioPlayer(data: data)
            player.prepareToPlay()
            self.player = player
            player.play()
        } catch {
            // Arrival sound is optional; route completion must still succeed if audio is unavailable.
        }
    }
}

'''
if 'private final class RouteArrivalChime' not in text:
    if marker not in text:
        raise SystemExit('Could not find insertion marker')
    text = text.replace(marker, helper + marker, 1)

# Play only after the final route sample has successfully been sent.
needle = '''            await MainActor.run {
                routePlaybackTask = nil
                if let lastSuccessfulCoordinate {
                    routePlaybackCoordinate = lastSuccessfulCoordinate
                    startResendLoop(with: lastSuccessfulCoordinate)
                }
            }
'''
replacement = '''            await MainActor.run {
                routePlaybackTask = nil
                if let lastSuccessfulCoordinate {
                    routePlaybackCoordinate = lastSuccessfulCoordinate
                    startResendLoop(with: lastSuccessfulCoordinate)
                    RouteArrivalChime.play()
                }
            }
'''
if needle not in text:
    raise SystemExit('Could not find route completion block')
if 'RouteArrivalChime.play()' not in text:
    text = text.replace(needle, replacement, 1)

p.write_text(text, encoding='utf-8')
print('Arrival chime patch applied.')
