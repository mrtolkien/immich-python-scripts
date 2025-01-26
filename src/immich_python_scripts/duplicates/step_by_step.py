import questionary
from rich.console import Console
from rich.markdown import Markdown

from immich_python_scripts.duplicates.common import (
    format_file_size,
    get_duplicate_data,
    pick_asset,
    show_table,
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

    print(f"Found {len(duplicates)} duplicate groups")

    for duplicate in duplicates:
        handle_duplicate_group(duplicate)


def handle_duplicate_group(duplicate):
    assets, albums = get_duplicate_data(duplicate)

    # Create a table to display duplicate assets
    largest_asset_index = show_table(assets, albums)

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
