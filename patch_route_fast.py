from pathlib import Path
import sys

ROOT = Path(sys.argv[1])
MAP = ROOT / "StikDebug" / "Views" / "MapSelectionView.swift"
text = MAP.read_text(encoding="utf-8")

# 1) Route search accepts exact latitude,longitude input without MapKit fuzzy search.
needle = '''    private func update(query: String, for field: RouteSearchField) {
        switch field {
'''
replacement = '''    private func update(query: String, for field: RouteSearchField) {
        if let coordinate = CoordinateImportParser.parseInline(query).first,
           query.trimmingCharacters(in: .whitespacesAndNewlines).contains(",") {
            let title = String(format: "%.6f, %.6f", coordinate.latitude, coordinate.longitude)
            let selection = RouteSearchSelection(title: title, coordinate: coordinate)
            switch field {
            case .start:
                startSelection = selection
                startCompleter.results = []
            case .end:
                endSelection = selection
                endCompleter.results = []
            }
            return
        }

        switch field {
'''
if needle not in text:
    raise SystemExit("RouteSearchSheet update() marker not found")
text = text.replace(needle, replacement, 1)

# 2) Do not block route playback on the slow OpenStreetMap/Overpass speed-limit prefetch.
# Build immediately using Apple Maps ETA as the fallback speed, then refine in the background.
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
                let immediatePlaybackSamples = buildPlaybackSamples(
                    from: displayCoordinates,
                    speedWays: [],
                    fallbackSpeedMetersPerSecond: fallbackSpeed
                )

                await MainActor.run {
                    guard routeRequestID == requestID else { return }
                    self.setRoutePlan(routePlan)
                    routePlaybackSamples = immediatePlaybackSamples
                    isLoadingRoute = false
                    isPrefetchingRouteSpeeds = false
                    if let routePolyline {
                        position = .rect(routePolyline.boundingMapRect)
                    }
                }

                routeSpeedPrefetchTask = Task.detached(priority: .utility) {
                    let refinedPlaybackSamples = await prefetchRoutePlaybackSamples(
                        displayCoordinates: displayCoordinates,
                        fallbackSpeedMetersPerSecond: fallbackSpeed
                    )
                    guard !Task.isCancelled else { return }
                    await MainActor.run {
                        guard routeRequestID == requestID,
                              routePlaybackTask == nil else { return }
                        routePlaybackSamples = refinedPlaybackSamples
                    }
                }
'''
if old not in text:
    raise SystemExit("refreshRoute prefetch block not found")
text = text.replace(old, new, 1)

# 3) Imported multi-point routes also start immediately instead of waiting for Overpass.
old_import = '''        let requestID = UUID()
        routeRequestID = requestID
        isPrefetchingRouteSpeeds = true
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
'''
new_import = '''        let requestID = UUID()
        routeRequestID = requestID
        routePlaybackSamples = buildPlaybackSamples(
            from: displayCoordinates,
            speedWays: [],
            fallbackSpeedMetersPerSecond: fallbackSpeed
        )
        isPrefetchingRouteSpeeds = false
        routeSpeedPrefetchTask = Task.detached(priority: .utility) {
            let refinedPlaybackSamples = await prefetchRoutePlaybackSamples(
                displayCoordinates: displayCoordinates,
                fallbackSpeedMetersPerSecond: fallbackSpeed
            )
            guard !Task.isCancelled else { return }
            await MainActor.run {
                guard routeRequestID == requestID,
                      routePlaybackTask == nil else { return }
                routePlaybackSamples = refinedPlaybackSamples
            }
        }
'''
if old_import not in text:
    raise SystemExit("imported route prefetch block not found")
text = text.replace(old_import, new_import, 1)

# 4) Play Route must not be disabled while background refinement is running.
text = text.replace('''                        isLoadingRoute ||
                        isPrefetchingRouteSpeeds ||
                        routePlan == nil ||''', '''                        isLoadingRoute ||
                        routePlan == nil ||''', 1)

MAP.write_text(text, encoding="utf-8")
print("Fast route loading and exact coordinate route input patch applied.")
