import os

import questionary
from rich.console import Console
from rich.markdown import Markdown

from immich_python_scripts import duplicates


def show_presentation():
    Console().print(
        Markdown("""
# Immich Python Scripts

Simply manage your Immich duplicates. 

## Features

### Duplicate Photos Management

- Merges album memberships
- Move low-quality duplicates to trash

Two options:
- **Step by Step Review**: Review and merge duplicates one by one
- **Automatic Merge**: Automatically merge duplicates based on heuristics
  - Asks if unsure

### Duplicate Videos Management
                 
- Shows files with the same name with their exif data
- Prompts to delete the duplicates

---
""")
    )


def main():
    os.system("clear")
    show_presentation()

    response = questionary.select(
        "What do you want to do?",
        choices=[
            "Review duplicates one by one",
            "Automatically merge duplicates",
            "Review videos with the same name",
            "Exit",
        ],
    ).ask()

    match response:
        case "Review duplicates one by one":
            duplicates.step_by_step_handler()

        case "Automatically merge duplicates":
            duplicates.automated_handler()

        case "Review videos with the same name":
            duplicates.dedup_videos()

        case "Exit":
            print("Exiting")
            return

    main()
