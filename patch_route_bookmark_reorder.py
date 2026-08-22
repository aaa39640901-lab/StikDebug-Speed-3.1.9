from pathlib import Path
import sys

ROOT = Path(sys.argv[1])
MAP = ROOT / "StikDebug" / "Views" / "MapSelectionView.swift"
if not MAP.exists():
    raise SystemExit(f"Missing source file: {MAP}")

text = MAP.read_text(encoding="utf-8")

# Make the A→B route bookmark list reorderable from the Edit button.
old_signature = '''private struct SavedRoutesView: View {
    let routes: [SavedRouteBookmark]
    let onSelect: (SavedRouteBookmark) -> Void
    let onDelete: (IndexSet) -> Void
'''
new_signature = '''private struct SavedRoutesView: View {
    let routes: [SavedRouteBookmark]
    let onSelect: (SavedRouteBookmark) -> Void
    let onDelete: (IndexSet) -> Void
    let onMove: (IndexSet, Int) -> Void
'''
if old_signature not in text:
    raise SystemExit("SavedRoutesView signature not found")
text = text.replace(old_signature, new_signature, 1)

old_call = '''                onDelete: { offsets in
                    savedRouteBookmarks.remove(atOffsets: offsets)
                    SavedRouteBookmarkStore.save(savedRouteBookmarks)
                }
'''
new_call = '''                onDelete: { offsets in
                    savedRouteBookmarks.remove(atOffsets: offsets)
                    SavedRouteBookmarkStore.save(savedRouteBookmarks)
                },
                onMove: { source, destination in
                    savedRouteBookmarks.move(fromOffsets: source, toOffset: destination)
                    SavedRouteBookmarkStore.save(savedRouteBookmarks)
                }
'''
if old_call not in text:
    raise SystemExit("Saved route sheet call not found")
text = text.replace(old_call, new_call, 1)

old_list = '''                        .onDelete(perform: onDelete)
                    }
                }
'''
new_list = '''                        .onDelete(perform: onDelete)
                        .onMove(perform: onMove)
                    }
                }
'''
start = text.index("private struct SavedRoutesView: View {")
head = text[:start]
tail = text[start:]
if old_list not in tail:
    raise SystemExit("Saved route list onDelete not found")
tail = tail.replace(old_list, new_list, 1)
text = head + tail

old_toolbar = '''            .navigationTitle("收藏路線")
            .navigationBarTitleDisplayMode(.inline)
        }
'''
new_toolbar = '''            .navigationTitle("收藏路線")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                if !routes.isEmpty {
                    EditButton()
                }
            }
        }
'''
if old_toolbar not in text:
    raise SystemExit("Saved route navigation block not found")
text = text.replace(old_toolbar, new_toolbar, 1)

MAP.write_text(text, encoding="utf-8")
print("A-to-B route bookmarks are now reorderable and persisted.")
