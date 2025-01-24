import questionary
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from textual_image.renderable import Image

from immich_python_scripts.duplicates.common import (
    format_file_size,
    get_duplicate_data,
    pick_asset,
)

from .. import api


def step_by_step_handler():
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
    # Create a table to display duplicate assets
    table = Table(title="Duplicate Assets")
    table.add_column("Filename")
    table.add_column("Type")
    table.add_column("File Size")
    table.add_column("Resolution")
    table.add_column("Albums Count")
    table.add_column("Thumbnail")

    assets, albums = get_duplicate_data(duplicate)

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

    pick_asset(assets, albums, picked_asset_index)
