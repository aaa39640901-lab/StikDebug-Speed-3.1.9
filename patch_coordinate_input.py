from pathlib import Path
import sys

ROOT = Path(sys.argv[1])
MAP = ROOT / "StikDebug" / "Views" / "MapSelectionView.swift"
if not MAP.exists():
    raise SystemExit(f"Missing source file: {MAP}")

text = MAP.read_text(encoding="utf-8")

# RouteSearchSheet already contains CoordinateImportParser, which can parse
# plain text latitude,longitude pairs. Use that parser directly so numeric
# coordinates bypass MapKit fuzzy search.
old = '''    private func update(query: String, for field: RouteSearchField) {
        switch field {
        case .start:
            if query != startSelection?.title {
                startSelection = nil
            }
            startCompleter.update(query: query)
        case .end:
            if query != endSelection?.title {
                endSelection = nil
            }
            endCompleter.update(query: query)
        }
    }
'''

new = '''    private func update(query: String, for field: RouteSearchField) {
        let trimmed = query.trimmingCharacters(in: .whitespacesAndNewlines)

        if let coordinate = CoordinateImportParser.parseInline(trimmed).first,
           trimmed.contains(",") {
            let title = String(format: "%.6f,%.6f", coordinate.latitude, coordinate.longitude)
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
        case .start:
            if query != startSelection?.title {
                startSelection = nil
            }
            startCompleter.update(query: query)
        case .end:
            if query != endSelection?.title {
                endSelection = nil
            }
            endCompleter.update(query: query)
        }
    }
'''

if old not in text:
    raise SystemExit("RouteSearchSheet.update() source did not match expected 3.1.9 code")

text = text.replace(old, new, 1)
MAP.write_text(text, encoding="utf-8")
print("Exact route coordinate input patch applied.")
