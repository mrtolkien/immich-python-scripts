from textual.widget import Widget
from textual.widgets import DataTable

from .. import api


def run_duplicates(table: DataTable):
    duplicates = api.queries.get_duplicates()

    table.add_columns("Filename", "Size", "Resolution", "Albums")

    for duplicate_assets in duplicates:
        table.clear()
        albums = set()

        for asset in duplicate_assets.assets:
            asset_album_ids = [a.id for a in api.queries.get_albums(asset.id)]
            albums.update(asset_album_ids)

            if asset.exifInfo is None:
                file_size = "N/A"
                resolution = "N/A"
            else:
                file_size = format_file_size(asset.exifInfo.fileSizeInByte)
                resolution = f"{int(asset.exifInfo.exifImageWidth or 0)}x{int(asset.exifInfo.exifImageHeight or 0 )}"

            table.add_row(
                asset.originalFileName,
                file_size,
                resolution,
                len(asset_album_ids),
                key=asset.id,
            )

        break


def format_file_size(size_in_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} PB"
