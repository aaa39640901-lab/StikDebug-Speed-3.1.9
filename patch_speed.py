#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(sys.argv[1])
MAP = ROOT / "StikDebug" / "Views" / "MapSelectionView.swift"
if not MAP.exists():
    raise SystemExit(f"Missing source file: {MAP}")

text = MAP.read_text(encoding="utf-8")

# Route playback does not need a network-wide OpenStreetMap/Overpass query to
# become playable. That query used the entire route bounding box and could be
# extremely slow on long routes (for example Tokyo -> Kasukabe). Build the
# playback samples immediately using the route's ETA-derived fallback speed.
# This makes route loading depend only on MapKit's route calculation.
text = text.replace(
    "    static let pathSamplingDistance: CLLocationDistance = 10\n",
    "    static let pathSamplingDistance: CLLocationDistance = 50\n",
    1,
)

needle = "    @State private var isPrefetchingRouteSpeeds = false\n"
insert = needle + "    @State private var customSpeedKmh: Double = 18\n"
if "customSpeedKmh" not in text:
    if needle not in text:
        raise SystemExit("Could not find speed state insertion point")
    text = text.replace(needle, insert, 1)

start = text.find("    private var routeControls: some View {")
end = text.find("    private func simulate() {", start)
if start < 0 or end < 0:
    raise SystemExit("Could not locate routeControls block")

route_controls = '''    private var routeControls: some View {
        VStack(spacing: 10) {
            Text(routeStatusText)
                .font(.footnote)
                .foregroundStyle(.secondary)

            if isLoadingRoute {
                ProgressView()
                    .controlSize(.small)
            } else if let routeSummaryText {
                Text(routeSummaryText)
                    .font(.footnote.monospaced())
                    .foregroundStyle(.secondary)
            }

            HStack(spacing: 10) {
                Text("Speed:")
                    .font(.subheadline.weight(.medium))

                TextField(
                    "Speed",
                    value: $customSpeedKmh,
                    format: .number.precision(.fractionLength(0))
                )
                .keyboardType(.numberPad)
                .textFieldStyle(.roundedBorder)
                .frame(width: 70)
                .multilineTextAlignment(.center)
                .onChange(of: customSpeedKmh) { _, newValue in
                    customSpeedKmh = min(max(newValue, 1), 120)
                }

                Text("km/h")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }

            Slider(value: $customSpeedKmh, in: 1...120, step: 1)
                .onChange(of: customSpeedKmh) { _, newValue in
                    customSpeedKmh = min(max(newValue, 1), 120)
                }
                .accessibilityLabel("Simulation speed")
                .accessibilityValue("\\(Int(customSpeedKmh)) km/h")

            routeAttributionLink

            HStack(spacing: 12) {
                Button("Stop", action: clear)
                    .buttonStyle(.bordered)
                    .tint(.red)
                    .disabled(!pairingExists || isBusy || !hasActiveSimulation)

                Button("Play Route", action: simulateRoute)
                    .buttonStyle(.borderedProminent)
                    .disabled(
                        !pairingExists ||
                        isBusy ||
                        isLoadingRoute ||
                        routePlan == nil ||
                        routePlaybackSamples.isEmpty
                    )

                Button("Reset", action: resetRouteSelection)
                    .buttonStyle(.bordered)
                    .disabled(isBusy || isRouteRunning)
            }
        }
    }

'''
text = text[:start] + route_controls + text[end:]

# Replace refreshRoute's post-MapKit speed-prefetch phase with immediate local
# sample generation. The route is therefore usable as soon as MapKit returns.
old = '''                await MainActor.run {
                    guard routeRequestID == requestID else { return }
                    self.setRoutePlan(routePlan)
                    isLoadingRoute = false
                    isPrefetchingRouteSpeeds = true
                    if let routePolyline {
                        position = .rect(routePolyline.boundingMapRect)
                    }
                }

                let fallbackSpeed = route.expectedTravelTime > 0
                    ? route.distance / route.expectedTravelTime
                    : 13.4

                await MainActor.run {
                    guard routeRequestID == requestID else { return }
                    routeSpeedPrefetchTask?.cancel()
                    routeSpeedPrefetchTask = Task.detached(priority: .utility) {
                        let playbackSamples = await prefetchRoutePlaybackSamples(
                            displayCoordinates: displayCoordinates,
                            fallbackSpeedMetersPerSecond: fallbackSpeed
                        )
                        guard !Task.isCancelled else { return }
                        await MainActor.run {
                            guard routeRequestID == requestID else { return }
                            routePlaybackSamples = playbackSamples
                            isPrefetchingRouteSpeeds = false
                        }
                    }
                }
'''

new = '''                let fallbackSpeed = route.expectedTravelTime > 0
                    ? route.distance / route.expectedTravelTime
                    : 13.4
                let playbackSamples = buildPlaybackSamples(
                    from: displayCoordinates,
                    speedWays: [],
                    fallbackSpeedMetersPerSecond: fallbackSpeed
                )

                await MainActor.run {
                    guard routeRequestID == requestID else { return }
                    self.setRoutePlan(routePlan)
                    routePlaybackSamples = playbackSamples
                    isLoadingRoute = false
                    isPrefetchingRouteSpeeds = false
                    if let routePolyline {
                        position = .rect(routePolyline.boundingMapRect)
                    }
                }
'''

if old not in text:
    raise SystemExit("Could not locate route speed prefetch block")
text = text.replace(old, new, 1)

start = text.find("    private func startRoutePlayback() {")
end = text.find("    private func sendLocationUpdate", start)
if start < 0 or end < 0:
    raise SystemExit("Could not locate startRoutePlayback block")

playback = '''    private func startRoutePlayback() {
        routePlaybackTask = Task {
            var lastSuccessfulCoordinate = routePlaybackSamples.first?.coordinate

            for sample in routePlaybackSamples.dropFirst() {
                let previousCoordinate = lastSuccessfulCoordinate ?? sample.coordinate
                let distance = CLLocation(
                    latitude: previousCoordinate.latitude,
                    longitude: previousCoordinate.longitude
                ).distance(
                    from: CLLocation(
                        latitude: sample.coordinate.latitude,
                        longitude: sample.coordinate.longitude
                    )
                )

                let speedMetersPerSecond = max(customSpeedKmh, 1) / 3.6
                let manualDelay = distance / speedMetersPerSecond
                let delay = manualDelay.isFinite && manualDelay > 0
                    ? manualDelay
                    : sample.delayFromPrevious

                try? await Task.sleep(for: .seconds(delay))
                guard !Task.isCancelled else { return }

                let code = await sendLocationUpdate(for: sample.coordinate)
                guard code == 0 else {
                    await MainActor.run {
                        routePlaybackTask = nil
                        routePlaybackCoordinate = lastSuccessfulCoordinate
                        if let lastSuccessfulCoordinate {
                            startResendLoop(with: lastSuccessfulCoordinate)
                        }
                        alertTitle = "Route Simulation Failed"
                        alertMessage = "Could not continue route simulation (error \\(code))."
                        showAlert = true
                    }
                    return
                }

                lastSuccessfulCoordinate = sample.coordinate
                await MainActor.run {
                    routePlaybackCoordinate = sample.coordinate
                }
            }

            await MainActor.run {
                routePlaybackTask = nil
                if let lastSuccessfulCoordinate {
                    routePlaybackCoordinate = lastSuccessfulCoordinate
                    startResendLoop(with: lastSuccessfulCoordinate)
                }
            }
        }
    }

'''
text = text[:start] + playback + text[end:]
MAP.write_text(text, encoding="utf-8")
print("Fast route loading patch applied: no blocking Overpass prefetch, 50m route sampling.")
