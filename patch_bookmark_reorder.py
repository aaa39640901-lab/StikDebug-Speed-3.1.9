from pathlib import Path
import sys

ROOT = Path(sys.argv[1])
MAP = ROOT / "StikDebug" / "Views" / "MapSelectionView.swift"
if not MAP.exists():
    raise SystemExit(f"Missing source file: {MAP}")

text = MAP.read_text(encoding="utf-8")

# Add persistent drag-to-reorder support to the existing location bookmarks.
old_parent = '''            BookmarksView(bookmarks: $bookmarks) { bookmark in
                applySelection(bookmark.coordinate)
                showBookmarks = false
            } onDelete: { offsets in
                bookmarks.remove(atOffsets: offsets)
                saveBookmarks()
            }
'''
new_parent = '''            BookmarksView(bookmarks: $bookmarks) { bookmark in
                applySelection(bookmark.coordinate)
                showBookmarks = false
            } onDelete: { offsets in
                bookmarks.remove(atOffsets: offsets)
                saveBookmarks()
            } onMove: { source, destination in
                bookmarks.move(fromOffsets: source, toOffset: destination)
                saveBookmarks()
            }
'''
if old_parent not in text:
    raise SystemExit("Location BookmarksView call did not match expected source")
text = text.replace(old_parent, new_parent, 1)

old_struct = '''struct BookmarksView: View {
    @Binding var bookmarks: [LocationBookmark]
    let onSelect: (LocationBookmark) -> Void
    let onDelete: (IndexSet) -> Void
'''
new_struct = '''struct BookmarksView: View {
    @Binding var bookmarks: [LocationBookmark]
    let onSelect: (LocationBookmark) -> Void
    let onDelete: (IndexSet) -> Void
    let onMove: (IndexSet, Int) -> Void
'''
if old_struct not in text:
    raise SystemExit("BookmarksView declaration did not match expected source")
text = text.replace(old_struct, new_struct, 1)

old_init_call = '''                        .onDelete(perform: onDelete)
                    }
'''
new_init_call = '''                        .onDelete(perform: onDelete)
                        .onMove(perform: onMove)
                    }
'''
# There are other List views with .onDelete; target the first occurrence after BookmarksView.
bookmark_pos = text.index("struct BookmarksView: View {")
tail = text[bookmark_pos:]
if old_init_call not in tail:
    raise SystemExit("BookmarksView onDelete block not found")
tail = tail.replace(old_init_call, new_init_call, 1)
text = text[:bookmark_pos] + tail

MAP.write_text(text, encoding="utf-8")
print("Persistent drag-to-reorder support applied to saved location bookmarks.")
