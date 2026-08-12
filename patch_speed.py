#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(sys.argv[1])
MAP = ROOT / "StikDebug" / "Views" / "MapSelectionView.swift"
if not MAP.exists():
    raise SystemExit(f"Missing source file: {MAP}")

text = MAP.read_text(encoding="utf-8")

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

            if isLoadingRoute || isPrefetchingRouteSpeeds {
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
                        isPrefetchingRouteSpeeds ||
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

lproj = ROOT / "StikDebug" / "zh-Hant.lproj"
lproj.mkdir(parents=True, exist_ok=True)
strings = r'''"Apps" = "應用程式";
"Scripts" = "腳本";
"Tools" = "工具";
"Console" = "主控台";
"Device Info" = "裝置資訊";
"App Expiry" = "App 到期日";
"Processes" = "程序";
"Location" = "定位";
"Settings" = "設定";
"Manage installed apps" = "管理已安裝的 App";
"Manage and run JS scripts" = "管理與執行 JS 腳本";
"Access additional tools" = "使用其他工具";
"Live device logs" = "即時裝置日誌";
"View detailed device metadata" = "查看詳細裝置資訊";
"Check app expiration dates" = "查看 App 到期日";
"Inspect running apps" = "查看執行中的 App";
"Simulate GPS location" = "模擬 GPS 位置";
"Configure StikDebug" = "設定 StikDebug";
"Location Simulation" = "位置模擬";
"Installed App" = "已安裝 App";
"Running Process" = "執行中的程序";
"Enable JIT" = "啟用 JIT";
"Kill Process" = "結束程序";
"App" = "App";
"Process" = "程序";
"Process ID" = "程序 ID";
"Unknown error" = "未知錯誤";
"An Error has Occurred" = "發生錯誤";
"INFO" = "資訊";
"ERROR" = "錯誤";
"DEBUG" = "除錯";
"WARNING" = "警告";
"Copy Value" = "複製值";
"Copy Key & Value" = "複製鍵和值";
"Copy All (Text)" = "全部複製（文字）";
"Copy All (CSV)" = "全部複製（CSV）";
"Share…" = "分享…";
"Import Pairing File" = "匯入配對檔案";
"Export" = "匯出";
"Export Failed" = "匯出失敗";
"Export Complete" = "匯出完成";
"Reload" = "重新載入";
"Copied" = "已複製";
"OK" = "確定";
"Cancel" = "取消";
"Save" = "儲存";
"Name" = "名稱";
"Stop" = "停止";
"Reset" = "重設";
"Play Route" = "播放路線";
"Simulate Location" = "模擬位置";
"Tap map to drop pin" = "點擊地圖放置標記";
"Search location..." = "搜尋位置…";
"Import Coordinates" = "匯入座標";
"Start" = "起點";
"End" = "終點";
"Current" = "目前位置";
"Pin" = "標記";
"Speed:" = "速度：";
"Speed" = "速度";
"km/h" = "公里/小時";
"Simulation speed" = "模擬速度";
"Route ready." = "路線準備完成。";
"Calculating route…" = "正在計算路線…";
"Prefetching road speeds…" = "正在取得道路速限…";
"Plan a route from the toolbar." = "請從工具列規劃路線。";
"Pick both route endpoints to build the drive." = "請選擇路線起點與終點。";
"Save Bookmark" = "儲存書籤";
"Enter a name for this location." = "請輸入此位置的名稱。";
"Import Failed" = "匯入失敗";
"Route Failed" = "路線失敗";
"Route Simulation Failed" = "路線模擬失敗";
"Clear Failed" = "清除失敗";
"Simulation Failed" = "模擬失敗";
"Resolving location…" = "正在解析位置…";
"Importing coordinates…" = "正在匯入座標…";
"Speed limit data © OpenStreetMap contributors (ODbL)" = "速限資料 © OpenStreetMap 貢獻者（ODbL）";
'''
(lproj / "Localizable.strings").write_text(strings, encoding="utf-8")

print("Patch applied successfully.")
