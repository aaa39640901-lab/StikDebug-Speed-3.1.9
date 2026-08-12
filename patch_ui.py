from pathlib import Path
import sys

ROOT = Path(sys.argv[1])


def edit(path, replacements):
    p = ROOT / path
    text = p.read_text(encoding='utf-8')
    for old, new in replacements:
        if old not in text:
            print(f'warning: not found in {path}: {old[:60]!r}')
            continue
        text = text.replace(old, new)
    p.write_text(text, encoding='utf-8')

# Main navigation / Tools screen labels.
edit('StikDebug/App/AppFeature.swift', [
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

edit('StikDebug/Views/ToolsView.swift', [
    ('.navigationTitle("Tools")', '.navigationTitle("工具")'),
])

# Settings screen: translate all user-facing labels visible in the supplied screenshot.
edit('StikDebug/Views/SettingsView.swift', [
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

# Location simulation: add a real keyboard dismissal button for the number-pad field.
p = ROOT / 'StikDebug/Views/MapSelectionView.swift'
text = p.read_text(encoding='utf-8')

if 'import SwiftUI' in text and '@Environment(\\.dismiss)' not in text:
    # Insert environment dismiss near the first State declarations.
    marker = 'struct MapSelectionView: View {\n'
    if marker in text:
        text = text.replace(marker, marker + '    @Environment(\\.dismiss) private var dismissKeyboard\n', 1)

text = text.replace('Text("Speed:")', 'Text("速度：")')
text = text.replace('"Speed",\n                    value:', '"速度",\n                    value:')
text = text.replace('Text("km/h")', 'Text("公里/小時")')
text = text.replace('.multilineTextAlignment(.center)\n                .onChange(of: customSpeedKmh)', '.multilineTextAlignment(.center)\n                .toolbar {\n                    ToolbarItemGroup(placement: .keyboard) {\n                        Spacer()\n                        Button("完成") { dismissKeyboard() }\n                    }\n                }\n                .onChange(of: customSpeedKmh)', 1)

# If the user taps the slider or map, dismiss the numeric keyboard as well.
text = text.replace('Slider(value: $customSpeedKmh, in: 1...120, step: 1)', 'Slider(value: $customSpeedKmh, in: 1...120, step: 1)\n                .onTapGesture { dismissKeyboard() }', 1)

text = text.replace('Button("Stop", action: clear)', 'Button("停止", action: clear)')
text = text.replace('Button("Play Route", action: simulateRoute)', 'Button("播放路線", action: simulateRoute)')
text = text.replace('Button("Reset", action: resetRouteSelection)', 'Button("重設", action: resetRouteSelection)')
p.write_text(text, encoding='utf-8')

print('UI patch applied.')
