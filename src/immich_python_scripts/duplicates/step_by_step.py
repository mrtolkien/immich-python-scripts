import os

import questionary
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from textual_image.renderable import Image

from .. import api


def step_by_step_handler():
    os.system("clear")

    console = Console()
    console.print(
        Markdown("""
# Step by Step Duplicate Handling

- For each duplicate group, you get shown the exif data
- The asset picked will be kept, all others will be trashed
- The asset will be added to all albums the other assets were in

---

Getting duplicates from server...

---
""")
    )

    duplicates = api.queries.get_duplicates()

    for duplicate in duplicates:
        handle_duplicate_group(console, duplicate)


def handle_duplicate_group(console, duplicate):
    os.system("clear")

    largest_size = -1
    largest_asset_index = -1
    albums: list[list[str]] = []
    assets = []

    # Create a table to display duplicate assets
    table = Table(title="Duplicate Assets")
    table.add_column("Filename")
    table.add_column("Type")
    table.add_column("File Size")
    table.add_column("Resolution")
    table.add_column("Albums Count")
    table.add_column("Thumbnail")

    for idx, asset_ in enumerate(duplicate.assets):
        # TODO Remove, due to api bug
        asset = api.queries.get_asset(asset_.id)

        assets.append(asset)

        asset_album_ids = [a.id for a in api.queries.get_albums(asset.id)]
        albums.append(asset_album_ids)

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
            largest_asset_index = idx

        # Add row to table
        table.add_row(
            asset.originalFileName,
            asset.originalMimeType,
            file_size,
            resolution,
            str(len(asset_album_ids)),
            Image(api.queries.get_thumbnail(asset.id)),
        )

    # Display the table
    console.print(table)

    # Select asset to keep
    choices = [
        {
            "name": f"{assets[i].originalFileName} ({format_file_size(d.exifInfo.fileSizeInByte if d.exifInfo else 0)})",
            "value": i,
        }
        for i, d in enumerate(assets)
    ]

    picked_asset_index = questionary.select(
        "Which asset do you want to keep?",
        choices=choices,
        default=choices[largest_asset_index],
    ).ask()

    asset_id = assets[picked_asset_index].id

    for album_id in set(a_ for albs in albums for a_ in albs):
        if album_id in albums[picked_asset_index]:
            continue

        api.queries.add_asset_to_album(asset_id, album_id)

    api.queries.trash_assets([a.id for a in assets if a.id != asset_id])


def format_file_size(size_in_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} PB"
