from pathlib import Path
import sys

ROOT = Path(sys.argv[1])
MAP = ROOT / "StikDebug" / "Views" / "MapSelectionView.swift"
if not MAP.exists():
    raise SystemExit(f"Missing source file: {MAP}")

text = MAP.read_text(encoding="utf-8")

# Add a direct coordinate parser for forms such as:
#   49.255725,2.134948
#   49.255725, 2.134948
#   (49.255725, 2.134948)
# Latitude is first, longitude second, matching CLLocationCoordinate2D.
marker = "    private func simulate() {\n"
helper = '''    private func parseDirectCoordinate(_ raw: String) -> CLLocationCoordinate2D? {
        let cleaned = raw
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .replacingOccurrences(of: "(", with: "")
            .replacingOccurrences(of: ")", with: "")
            .replacingOccurrences(of: "，", with: ",")

        let parts = cleaned.split(separator: ",", maxSplits: 1, omittingEmptySubsequences: true)
        guard parts.count == 2,
              let latitude = Double(parts[0].trimmingCharacters(in: .whitespaces)),
              let longitude = Double(parts[1].trimmingCharacters(in: .whitespaces)),
              (-90...90).contains(latitude),
              (-180...180).contains(longitude) else {
            return nil
        }

        return CLLocationCoordinate2D(latitude: latitude, longitude: longitude)
    }

'''
if "private func parseDirectCoordinate" not in text:
    if marker not in text:
        raise SystemExit("Could not find simulate() insertion point")
    text = text.replace(marker, helper + marker, 1)

# Make the route geocoder accept exact numeric coordinates before network geocoding.
# We intentionally preserve all normal place-name search behavior as a fallback.
replacements = [
    (
        '        let geocoder = CLGeocoder()\n',
        '''        if let direct = parseDirectCoordinate(query) {
            return direct
        }

        let geocoder = CLGeocoder()
'''
    ),
    (
        '        routeStartText = coordinateString(startCoordinate)\n',
        '        routeStartText = coordinateString(startCoordinate)\n'
    ),
]
for old, new in replacements:
    if old in text and old != new:
        text = text.replace(old, new, 1)

# Also accept direct coordinates when importing coordinates for route endpoints.
# This adds a helper branch around any CLLocation geocoding entry points that feed route endpoints.
needle = '        let query = text.trimmingCharacters(in: .whitespacesAndNewlines)\n'
if needle in text and 'if let direct = parseDirectCoordinate(query)' not in text:
    text = text.replace(
        needle,
        '        let query = text.trimmingCharacters(in: .whitespacesAndNewlines)\n        if let direct = parseDirectCoordinate(query) {\n            return direct\n        }\n',
        1,
    )

MAP.write_text(text, encoding="utf-8")

print("Direct latitude,longitude input support added.")
