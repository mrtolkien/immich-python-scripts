import questionary

from immich_python_scripts import duplicates


def main():
    response = questionary.select(
        "What do you want to do?",
        choices=[
            "Review duplicates one by one with album merging",
            "Automatically merge duplicates with album merging",
            "Exit",
        ],
    ).ask()

    match response:
        case "Review duplicates one by one with album merging":
            duplicates.step_by_step_handler()

        case "Automatically merge duplicates with album merging":
            print("Automatically merging duplicates with album merging")

        case "Exit":
            print("Exiting")
            return

    main()
