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
                TFT_VALUE: "2",
            }
        },
    },
}
COLUMN_HEADERS = ["Field", "Existing Value", "New Value"]
DOES_NOT_EXIST = "DOES NOT EXIST"


class TableWriter():

    def __init__(self):
        self._headers = []
        self._rows = []
        self._column_sizes = None

    def add_header(self, args):
        self._headers.append(args)

        # Update column sizes
        if self._column_sizes is None:
            self._column_sizes = [len(column) for column in args]
        else:
            for i, column in enumerate(args):
                if len(column) > self._column_sizes[i]:
                    self._column_sizes[i] = len(column)

    def add_row(self, args):
        self._rows.append(args)

        # Update column sizes
        if self._column_sizes is None:
            self._column_sizes = [len(column) for column in args]
        else:
            for i, column in enumerate(args):
                if len(column) > self._column_sizes[i]:
                    self._column_sizes[i] = len(column)

    def write(self):
        for header in self._headers:
            self._print_table_border()
            self._print_table_header(header)
        self._print_table_border()

        for row in self._rows:
            self._print_table_row(row)
        self._print_table_border()
        print("")

    def _print_table_header(self, header):
        """Prints the header of the table."""
        header_row = ""
        for header, size in zip(header, self._column_sizes):
            header_row += f"| {header: ^{size}} "
        header_row += "|"

        print(header_row)

    def _print_table_row(self, values):
        """Prints a row of the table with the given values."""
        value_str = ""
        for value, size in zip(values, self._column_sizes):
            value_str += f"| {value: <{size}} "
        value_str += "|"
        print(value_str)

    def _print_table_border(self):
        """Prints the borders of the table."""
        border_str = ""
        for size in self._column_sizes:
            border_str += f"+={'=' * size}="
        border_str += "+"
        print(border_str)


def update_file(args, file):
    # Open config file
    config_parser = configparser.ConfigParser()
    config_parser.optionxform = str
    config_parser.read(file)

    table_writer = TableWriter()
    table_writer.add_header(COLUMN_HEADERS)

    # print_table_header(column_sizes)
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
            table_writer.add_row(values)

            # Assign new value if the field was present
            if section in config_parser and field in config_parser[section]:
                config_parser[section][field] = desired_value

    table_writer.write()
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
