from pathlib import Path
import sys

ROOT = Path(sys.argv[1])


def replace_file(path, pairs):
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    for old, new in pairs:
        text = text.replace(old, new)
    p.write_text(text, encoding="utf-8")

# Only translate the three screens requested. Keep this patch deliberately
# small so it cannot interfere with the working route/coordinate changes.
replace_file("StikDebug/App/AppFeature.swift", [
    ('return "Apps"', 'return "應用程式"'),
    ('return "Tools"', 'return "工具"'),
    ('return "Settings"', 'return "設定"'),
])

replace_file("StikDebug/Views/MapSelectionView.swift", [
    ('"Search location..."', '"搜尋位置…"'),
    ('"Simulate Route"', '"模擬路線"'),
    ('"Simulate Location"', '"模擬位置"'),
    ('"Play Route"', '"播放路線"'),
    ('"Use Route"', '"使用路線"'),
    ('"Cancel"', '"取消"'),
    ('"Start"', '"起點"'),
    ('"End"', '"終點"'),
    ('"Search for a start and destination to build the route."', '"搜尋起點與目的地以建立路線。"'),
    ('"Calculating route…"', '"正在計算路線…"'),
    ('"Prefetching road speeds…"', '"正在取得道路速度…"'),
    ('"Route ready."', '"路線已準備完成。"'),
    ('"Pick both route endpoints to build the drive."', '"請選擇起點與終點以建立路線。"'),
    ('"No drivable route was returned."', '"找不到可行駛的路線。"'),
    ('"Route Failed"', '"路線失敗"'),
    ('"Simulation Failed"', '"模擬失敗"'),
    ('"Route Simulation Failed"', '"路線模擬失敗"'),
    ('"Clear Failed"', '"清除失敗"'),
    ('"Reset"', '"重設"'),
    ('"Stop"', '"停止"'),
    ('"Speed:"', '"速度："'),
    ('"Speed"', '"速度"'),
    ('"km/h"', '"公里/小時"'),
    ('"Save Bookmark"', '"儲存地點"'),
    ('"Bookmarks"', '"已儲存地點"'),
])

print("Minimal Traditional Chinese UI patch applied for the three requested screens.")
