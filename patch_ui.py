from pathlib import Path
import sys

ROOT = Path(sys.argv[1])


def replace_file(path, pairs):
    p = ROOT / path
    text = p.read_text(encoding='utf-8')
    for old, new in pairs:
        text = text.replace(old, new)
    p.write_text(text, encoding='utf-8')

# Main navigation.
replace_file('StikDebug/App/AppFeature.swift', [
    ('return "Apps"', 'return "應用程式"'),
    ('return "Scripts"', 'return "腳本"'),
    ('return "Tools"', 'return "工具"'),
    ('return "Console"', 'return "主控台"'),
    ('return "Device Info"', 'return "裝置資訊"'),
    ('return "App Expiry"', 'return "App 到期日"'),
    ('return "Processes"', 'return "程序"'),
    ('return "Location"', 'return "定位"'),
    ('return "Settings"', 'return "設定"'),
    ('return "Manage installed apps"', 'return "管理已安裝的 App"'),
    ('return "Manage and run JS scripts"', 'return "管理與執行 JS 腳本"'),
    ('return "Access additional tools"', 'return "使用其他工具"'),
    ('return "Live device logs"', 'return "即時裝置日誌"'),
    ('return "View detailed device metadata"', 'return "查看詳細裝置資訊"'),
    ('return "Check app expiration dates"', 'return "查看 App 到期日"'),
    ('return "Inspect running apps"', 'return "查看執行中的 App"'),
    ('return "Simulate GPS location"', 'return "模擬 GPS 位置"'),
    ('return "Configure StikDebug"', 'return "設定 StikDebug"'),
    ('return "Location Simulation"', 'return "位置模擬"'),
])
replace_file('StikDebug/Views/ToolsView.swift', [
    ('.navigationTitle("Tools")', '.navigationTitle("工具")'),
])

# Settings.
replace_file('StikDebug/Views/SettingsView.swift', [
    ('Label("Star on GitHub", systemImage:', 'Label("在 GitHub 上加星", systemImage:'),
    ('Section("Pairing File")', 'Section("配對檔案")'),
    ('Label("Import Pairing File", systemImage:', 'Label("匯入配對檔案", systemImage:'),
    ('Text("Importing pairing file…")', 'Text("正在匯入配對檔案…")'),
    ('Text("Silent Audio")', 'Text("靜音音訊")'),
    ('Text("Plays inaudible audio so iOS keeps the app running.")', 'Text("播放無聲音訊，讓 iOS 保持 App 執行。")'),
    ('Text("Background Location")', 'Text("背景定位")'),
    ('Text("Uses low-accuracy location to stay alive when an activity needs it.")', 'Text("需要保持活動時，使用低精度定位讓 App 保持執行。")'),
    ('Text("Background Keep-Alive")', 'Text("背景保持執行")'),
    ('Section("Behavior")', 'Section("行為")'),
    ('Text("Confirm JIT Links")', 'Text("確認 JIT 連結")'),
    ('Text("Ask before external links enable JIT or run scripts.")', 'Text("外部連結啟用 JIT 或執行腳本前先詢問。")'),
    ('Text("Always Run Scripts")', 'Text("永遠執行腳本")'),
    ('Text("Treats device as TXM-capable to bypass hardware checks.")', 'Text("將裝置視為支援 TXM，以略過硬體檢查。")'),
    ('Section("Advanced")', 'Section("進階")'),
    ('Text("Target Device IP")', 'Text("目標裝置 IP")'),
    ('Label("App Folder", systemImage:', 'Label("App 資料夾", systemImage:'),
    ('Label("Redownload DDI", systemImage:', 'Label("重新下載 DDI", systemImage:'),
    ('Section("Help")', 'Section("說明")'),
    ('Label("Pairing File Guide", systemImage:', 'Label("配對檔案教學", systemImage:'),
    ('Label("Download LocalDevVPN", systemImage:', 'Label("下載 LocalDevVPN", systemImage:'),
    ('Label("Discord Support", systemImage:', 'Label("Discord 支援", systemImage:'),
    ('.navigationTitle("Settings")', '.navigationTitle("設定")'),
    ('("Imported successfully", false)', '("匯入成功", false)'),
    ('("Import failed: \\(error.localizedDescription)", true)', '("匯入失敗：\\(error.localizedDescription)", true)'),
    ('"Redownload DDI Files?"', '"重新下載 DDI 檔案？"'),
    ('Button("Redownload", role: .destructive)', 'Button("重新下載", role: .destructive)'),
    ('Text("Existing DDI files will be removed before downloading fresh copies.")', 'Text("重新下載前會先移除現有的 DDI 檔案。")'),
    ('Button("Cancel", role: .cancel)', 'Button("取消", role: .cancel)'),
    ('"Preparing download…"', '"準備下載…"'),
    ('("DDI files refreshed successfully.", false)', '("DDI 檔案重新整理完成。", false)'),
    ('("Failed to redownload DDI files: \\(error.localizedDescription)", true)', '("重新下載 DDI 失敗：\\(error.localizedDescription)", true)'),
])

# Location simulation: all visible labels + numeric keyboard dismissal.
p = ROOT / 'StikDebug/Views/MapSelectionView.swift'
text = p.read_text(encoding='utf-8')

marker = 'struct LocationSimulationView: View {\n'
if '@Environment(\\.dismiss) private var dismissKeyboard' not in text and marker in text:
    text = text.replace(marker, marker + '    @Environment(\\.dismiss) private var dismissKeyboard\n', 1)

pairs = [
    ('Text("Speed:")', 'Text("速度：")'),
    ('"Speed",', '"速度",'),
    ('Text("km/h")', 'Text("公里/小時")'),
    ('"Start"', '"起點"'),
    ('"End"', '"終點"'),
    ('"Current"', '"目前位置"'),
    ('"Pin"', '"標記"'),
    ('"Import Coordinates"', '"匯入座標"'),
    ('"Search location..."', '"搜尋位置…"'),
    ('"OK"', '"確定"'),
    ('"Save Bookmark"', '"儲存地點"'),
    ('"Name"', '"名稱"'),
    ('Button("Save")', 'Button("儲存")'),
    ('"Enter a name for this location."', '"請輸入此位置的名稱。"'),
    ('"Imported"', '"已匯入"'),
    ('"Import Failed"', '"匯入失敗"'),
    ('"Tap map to drop pin"', '"點擊地圖以放置標記"'),
    ('Button("Stop", action: clear)', 'Button("停止", action: clear)'),
    ('Button("Simulate Location", action: simulate)', 'Button("模擬位置", action: simulate)'),
    ('Button("Play Route", action: simulateRoute)', 'Button("播放路線", action: simulateRoute)'),
    ('Button("Reset", action: resetRouteSelection)', 'Button("重設", action: resetRouteSelection)'),
    ('"Simulation Failed"', '"模擬失敗"'),
    ('"Route Simulation Failed"', '"路線模擬失敗"'),
    ('"Clear Failed"', '"清除失敗"'),
    ('"Calculating route…"', '"正在計算路線…"'),
    ('"Prefetching road speeds…"', '"正在取得道路速度…"'),
    ('"Route ready."', '"路線已準備完成。"'),
    ('"Pick both route endpoints to build the drive."', '"請選擇起點與終點以建立路線。"'),
    ('"Plan a route from the toolbar."', '"請從工具列規劃路線。"'),
    ('"Speed limit data © OpenStreetMap contributors (ODbL)"', '"限速資料 © OpenStreetMap 貢獻者（ODbL）"'),
    ('"No drivable route was returned."', '"找不到可行駛的路線。"'),
    ('"Route Failed"', '"路線失敗"'),
    ('"Resolving location…"', '"正在解析位置…"'),
    ('"Search for a start and destination to build the route."', '"搜尋起點與目的地以建立路線。"'),
    ('"Simulate Route"', '"模擬路線"'),
    ('Button("Use Route")', 'Button("使用此路線")'),
    ('"Could not resolve that location."', '"無法解析該位置。"'),
    ('"No Bookmarks"', '"沒有儲存的地點"'),
    ('"Drop a pin on the map and tap the bookmark icon to save a location."', '"在地圖上放置標記，再點擊書籤圖示即可儲存位置。"'),
    ('.navigationTitle("Bookmarks")', '.navigationTitle("已儲存地點")'),
    ('"Could not simulate location (error \\(code)). Make sure the device is connected and the DDI is mounted."', '"無法模擬位置（錯誤 \\(code)）。請確認裝置已連線且 DDI 已掛載。"'),
    ('"Could not start route simulation (error \\(code)). Make sure the device is connected and the DDI is mounted."', '"無法開始路線模擬（錯誤 \\(code)）。請確認裝置已連線且 DDI 已掛載。"'),
    ('"Could not clear simulated location (error \\(code))."', '"無法清除模擬位置（錯誤 \\(code)）。"'),
    ('"Could not continue route simulation (error \\(code))."', '"無法繼續路線模擬（錯誤 \\(code)）。"'),
]
for old, new in pairs:
    text = text.replace(old, new)

# The actual speed editor is in LocationSimulationView; add a Done button to the numeric keyboard.
needle = '.multilineTextAlignment(.center)\n                .onChange(of: customSpeedKmh)'
if needle in text and 'Button("完成") { dismissKeyboard() }' not in text:
    text = text.replace(needle, '.multilineTextAlignment(.center)\n                .toolbar {\n                    ToolbarItemGroup(placement: .keyboard) {\n                        Spacer()\n                        Button("完成") { dismissKeyboard() }\n                    }\n                }\n                .onChange(of: customSpeedKmh)', 1)

text = text.replace('Slider(value: $customSpeedKmh, in: 1...120, step: 1)', 'Slider(value: $customSpeedKmh, in: 1...120, step: 1)\n                .onTapGesture { dismissKeyboard() }', 1)
p.write_text(text, encoding='utf-8')

# Broad pass for remaining screens. Exact replacements only; no identifiers/function names are changed.
all_pairs = [
    ('Process Inspector', '程序檢視器'), ('Refresh', '重新整理'), ('Try Again', '再試一次'),
    ('Overview', '總覽'), ('Total Processes', '程序總數'), ('No matching processes.', '沒有符合的程序。'),
    ('Resume', '繼續'), ('Pause', '暫停'), ('Kill', '終止'), ('Confirm', '確認'),
    ('Resuming Process', '正在繼續程序'), ('Pausing Process', '正在暫停程序'), ('Terminating Process', '正在終止程序'),
    ('Resume Timed Out', '繼續程序逾時'), ('Pause Timed Out', '暫停程序逾時'), ('Kill Timed Out', '終止程序逾時'),
    ('Resume Failed', '繼續程序失敗'), ('Pause Failed', '暫停程序失敗'), ('Kill Failed', '終止程序失敗'),
    ('Process Resumed', '程序已繼續'), ('Process Paused', '程序已暫停'), ('Process Terminated', '程序已終止'),
    ('Console Logs', '主控台日誌'), ('Device Information', '裝置資訊'), ('App Expiration', 'App 到期日'),
    ('Installed Apps', '已安裝 App'), ('Search', '搜尋'), ('Close', '關閉'), ('Done', '完成'),
    ('Cancel', '取消'), ('Save', '儲存'), ('Delete', '刪除'), ('Edit', '編輯'), ('Back', '返回'),
    ('Next', '下一步'), ('Clear', '清除'), ('Import', '匯入'), ('Export', '匯出'),
    ('Loading…', '載入中…'), ('Running', '執行中'), ('Stopped', '已停止'),
    ('Connected', '已連線'), ('Disconnected', '未連線'),
]
for p in (ROOT / 'StikDebug').rglob('*.swift'):
    text = p.read_text(encoding='utf-8')
    original = text
    for old, new in all_pairs:
        text = text.replace(old, new)
    if text != original:
        p.write_text(text, encoding='utf-8')

print('Traditional Chinese UI patch applied.')
