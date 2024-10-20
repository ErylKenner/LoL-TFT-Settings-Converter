import argparse
import pathlib
import configparser
import os

PERSISTED_SETTINGS_FILE = pathlib.Path("C:\\Riot Games\\League of Legends\\Config\\PersistedSettings.json").resolve()
INPUTS_CONFIG_FILE = pathlib.Path("C:\\Riot Games\\League of Legends\\Config\\Input.ini").resolve()
GAME_CFG_FILE = pathlib.Path("C:\\Riot Games\\League of Legends\\Config\\game.cfg").resolve()

FILES = [INPUTS_CONFIG_FILE, GAME_CFG_FILE]

LEAGUE_VALUE = "league"
TFT_VALUE = "tft"

FIELDS_TO_CHANGE = {
    INPUTS_CONFIG_FILE: {
        "GameEvents": {
            "evtPlayerAttackMoveClick": {
                LEAGUE_VALUE: "[Button 1]",
                TFT_VALUE: "[<Unbound>]",
            },
            "evtPlayerAttackMove": {
                LEAGUE_VALUE: "[Button 1],[<Unbound>]",
                TFT_VALUE: "[<Unbound>],[<Unbound>]",
            },
        },
    },
    GAME_CFG_FILE: {
        "General": {
            "WindowMode": {
                LEAGUE_VALUE: "0",
                TFT_VALUE: "1",
            }
        },
    },
}
COLUMN_HEADERS = ["Field", "Existing Value", "New Value"]
DOES_NOT_EXIST = "DOES NOT EXIST"


def get_table_columns(target, config_parser):
    """Returns a list of column sizes based on the given target."""
    column_sizes = [0, 0, 0]
    for section, fields in FIELDS_TO_CHANGE.items():
        for field, values in fields.items():
            field_name_length = len(f"{field}.{section}")
            if field_name_length > column_sizes[0]:
                column_sizes[0] = field_name_length

            if section in config_parser and field in config_parser[section]:
                field_value_length = len(config_parser[section][field])
                new_value_length = len(values[target])
            else:
                field_value_length = len(DOES_NOT_EXIST)
                new_value_length = len(DOES_NOT_EXIST)

            if field_value_length > column_sizes[1]:
                column_sizes[1] = field_value_length

            if new_value_length > column_sizes[2]:
                column_sizes[2] = new_value_length
    return column_sizes


def print_table_header(column_sizes):
    """Prints the header of the table based on the given column sizes."""
    inside_str = ""
    for header, size in zip(COLUMN_HEADERS, column_sizes):
        inside_str += f"| {header: ^{size}} "
    inside_str += "|"

    print_table_border(column_sizes)
    print(inside_str)
    print_table_border(column_sizes)


def print_table_border(column_sizes):
    """Prints the borders of the table based on the given column sizes."""
    border_str = ""
    for size in column_sizes:
        border_str += f"+={'=' * size}="
    border_str += "+"
    print(border_str)


def print_table_row(values, column_sizes):
    """Prints a row of the table with the given values and corresponding column sizes."""
    value_str = ""
    for value, size in zip(values, column_sizes):
        value_str += f"| {value: <{size}} "
    value_str += "|"
    print(value_str)


def update_file(args, file):
    # Open config file
    config_parser = configparser.ConfigParser()
    config_parser.optionxform = str
    config_parser.read(file)

    column_sizes = get_table_columns(args.target, config_parser)

    print_table_header(column_sizes)
    for section, fields in FIELDS_TO_CHANGE[file].items():
        for field, values in fields.items():
            # Get values
            field_name = f"{section}.{field}"
            existing_value = DOES_NOT_EXIST
            desired_value = DOES_NOT_EXIST
            if section in config_parser and field in config_parser[section]:
                existing_value = config_parser[section][field]
                desired_value = values[args.target]

            # Print the table row
            values = [field_name, existing_value, desired_value]
            print_table_row(values, column_sizes)

            # Assign new value if the field was present
            if section in config_parser and field in config_parser[section]:
                config_parser[section][field] = desired_value

    print_table_border(column_sizes)
    print("")

    # Write the new config file
    print(f"Overriding: {file}")
    with open(file, "w", encoding="utf-8") as settings_file:
        config_parser.write(settings_file, space_around_delimiters=False)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        prog="SettingsConverter",
        description="Used for converting: League Setting <--> TFT_VALUE Settings",
    )
    parser.add_argument("-t", "--target", type=str, choices=[LEAGUE_VALUE, TFT_VALUE], required=True)
    args = parser.parse_args()

    for file in FILES:
        update_file(args, file)

    try:
        print(f"Deleting settings file (so that changes take effect): {PERSISTED_SETTINGS_FILE}")
        os.remove(PERSISTED_SETTINGS_FILE)
    except OSError:
        pass

    print("")


if __name__ == "__main__":
    main()
