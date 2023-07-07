import json
import re
import sys
import argparse


parser = argparse.ArgumentParser(
    prog="KaizoDelivery Release Utils (KDRU)",
    description="Manages .json release history files in a predictable way, 'free' of human error.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

parser.add_argument(
    "version",
    help="New version to include in the release history files."
)

release_type = parser.add_mutually_exclusive_group(
    required=True
)

release_type.add_argument(
    "-r",
    "--release",
    action="store_true",
    help="Marks this version as a full release."
)

release_type.add_argument(
    "-b",
    "--beta",
    action="store_true",
    help="Marks this version as a beta release."
)

release_type.add_argument(
    "-jb",
    "--join-beta",
    action="store_true",
    help="Makes the beta branch join the given release branch version. Used to mark the end of a beta branch lifecycle."
)

args = parser.parse_args()


if __name__ == "__main__":
    config: dict = vars(args)
    version: str = config["version"]

    if config["join_beta"]:
        raise ValueError("This functionality isn't implemented yet.")

    if config["beta"] and not re.match(r"^\d+\.\d{3}$", version):
        raise ValueError("Invalid beta version. A beta version should follow the following format: ?.!!! "
              "where ? is any number, and ! is a number from 0 to 9. Ex: b1.001")

    if config["release"] and not re.match(r"^\d+\.\d$", version):
        raise ValueError("Invalid release version. A beta version should follow the following format: ?.! "
              "where ? is any number, and ! is a number from 0 to 9. Ex: 1.0")

    rel_type: str = "release" if config["release"] else "beta"
    history_file: str = "data/tags_release.json" if config["release"] else "data/tags_beta.json"

    with open(history_file, "r+") as file:
        data: list[str, ...] = json.load(file)

        print("Reminder: Please keep version jumps consistent. Only newer versions can be released.")
        print("Versions must match the GitHub Releases tag.\n\n")

        if len(data) == 0:
            print(
                "{} will be the first version to ever release in the {} branch.".format(
                    version,
                    rel_type
                )
            )
        else:
            print(
                "Jumping from version {} to version {} in the {} branch".format(
                    data[-1],
                    version,
                    rel_type
                )
            )

        if input("Is this correct? [y/n] ").lower() not in ("y", "yes"):
            raise ValueError("User has cancelled the operation.")

        data.append(version)

        file.seek(0)
        file.write(json.dumps(data))
        file.truncate()

    with open("data/latest_release.json", "r+") as file:
        data: dict = json.load(file)

        data["latest_{}".format(rel_type)] = version

        file.seek(0)
        file.write(json.dumps(data))
        file.truncate()

    print(
        "\n\nVersion {} has been released in the {} branch. Push changes to make it effective, "
        "discard changes to undo.\n\n".format(
                version,
                rel_type
            )
    )
