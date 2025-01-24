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

### Duplicate Management
- **Step by Step Review**: Review and merge duplicates one by one
  - Compare metadata and thumbnails
  - Pick which file to keep
  - Merge album memberships
  - Move others to trash
- **Automatic Merge**: Automatically merge duplicates
  - Keeps the highest quality version
  - Merges album memberships
  - Moves others to trash

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
            "Exit",
        ],
    ).ask()

    match response:
        case "Review duplicates one by one":
            duplicates.step_by_step_handler()

        case "Automatically merge duplicates":
            print("Automatically merging duplicates with album merging")

        case "Exit":
            print("Exiting")
            return

    main()
