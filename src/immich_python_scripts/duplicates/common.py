from rich.table import Table
from textual_image.renderable import Image

from immich_python_scripts import api


def pick_asset(assets, albums, picked_asset_index):
    asset_id = assets[picked_asset_index].id

    for album_id in set(a_ for albs in albums for a_ in albs):
        if album_id in albums[picked_asset_index]:
            continue

        print(f"Adding asset {asset_id} to album {album_id}")
        api.queries.add_asset_to_album(asset_id, album_id)

    trash_ids = [a.id for a in assets if a.id != asset_id]

    print(f"Trashing assets {trash_ids}")

    api.queries.trash_assets(trash_ids)


def format_file_size(size_in_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} PB"


def get_duplicate_data(
    duplicate: api.model.DuplicateResponseDto,
) -> tuple[list[api.model.AssetResponseDto], list[list[str]]]:
    assets = []
    albums: list[list[str]] = []

    for asset_ in duplicate.assets:
        # TODO Remove, due to api bug
        asset = api.queries.get_asset(asset_.id)

        assets.append(asset)

        asset_album_ids = [a.id for a in api.queries.get_albums(asset.id)]
        albums.append(asset_album_ids)

    return assets, albums


def show_table(console, assets, albums):
    table = Table(title="Duplicate Assets")
    table.add_column("Filename")
    table.add_column("Type")
    table.add_column("File Size")
    table.add_column("Resolution")
    table.add_column("Albums Count")
    table.add_column("Thumbnail")

    largest_size = -1
    largest_asset_index = -1

    for asset, asset_album_ids in zip(assets, albums):
        file_size = format_file_size(
            asset.exifInfo.fileSizeInByte if asset.exifInfo else 0
        )

        resolution = (
            f"{asset.exifInfo.exifImageWidth}x{asset.exifInfo.exifImageHeight}"
            if asset.exifInfo
            else "Unknown"
        )

        if asset.exifInfo and (asset.exifInfo.fileSizeInByte or -1) > largest_size:
            largest_size = asset.exifInfo.fileSizeInByte or -1
            largest_asset_index = len(table.rows)

        table.add_row(
            asset.originalFileName + "\n" + asset.id,
            asset.originalMimeType,
            file_size,
            resolution,
            str(len(asset_album_ids)),
            Image(api.queries.get_thumbnail(asset.id)),
        )

    # Display the table
    console.print(table)
    return largest_asset_index
