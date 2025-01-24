from textual.widgets import DataTable

from .. import api


class DuplicatesHandler:
    def __init__(self):
        self.duplicates = api.queries.get_duplicates()

        self.current_index = 0

        self.current_assets_albums = {}

    def load_next(self, table: DataTable):
        if self.current_index >= len(self.duplicates):
            table.clear()
            return None

        duplicate_assets = self.duplicates[self.current_index]
        table.clear()

        largest_asset_id = 0
        largest_size = -1

        for idx, asset in enumerate(duplicate_assets.assets):
            asset_album_ids = [a.id for a in api.queries.get_albums(asset.id)]
            self.current_assets_albums[asset.id] = asset_album_ids

            if asset.exifInfo is None:
                file_size = "N/A"
                resolution = "N/A"
                size_in_bytes = -1
            else:
                size_in_bytes = asset.exifInfo.fileSizeInByte
                file_size = format_file_size(size_in_bytes)
                resolution = f"{int(asset.exifInfo.exifImageWidth or 0)}x{int(asset.exifInfo.exifImageHeight or 0 )}"

            if size_in_bytes > largest_size:  # type: ignore
                largest_size = size_in_bytes
                largest_asset_id = idx

            if not table.columns:
                table.add_columns("Filename", "Size", "Resolution", "Albums")

            table.add_row(
                asset.originalFileName,
                file_size,
                resolution,
                len(asset_album_ids),
                key=asset.id,
            )

        table.move_cursor(row=largest_asset_id)

    def handle_selection(self, asset_row):
        asset_id = asset_row.value

        for a in self.current_assets_albums:
            if a == asset_id:
                continue

            for album_id in self.current_assets_albums[a]:
                api.queries.add_asset_to_album(asset_id, album_id)

        api.queries.trash_assets(
            [a for a in self.current_assets_albums if a != asset_id]
        )

        self.current_assets_albums = {}
        self.current_index += 1


def format_file_size(size_in_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} PB"
