import argparse
import itertools
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
        self._width = 0
        self._column_widths = {}

    def add_header(self, args):
        self._headers.append(args)

    def add_row(self, args):
        self._rows.append(args)

    def write(self):
        self._calculate_column_widths()

        self._print_table_border()
        for header in self._headers:
            self._print_table_row(header, is_centered=True)
        self._print_table_border()

        for row in self._rows:
            self._print_table_row(row, is_centered=False)
        self._print_table_border()
        print("")

    def _calculate_column_widths(self):
        for row in itertools.chain(self._headers, self._rows):
            num_columns = len(row)
            column_widths = [len(column) + 2 for column in row]
            if num_columns in self._column_widths:
                for i, existing_column in enumerate(self._column_widths[num_columns]):
                    if existing_column > column_widths[i]:
                        column_widths[i] = existing_column
            self._column_widths[num_columns] = column_widths
        self._width = max(
            [sum(column_widths) + len(column_widths) - 1 for column_widths in self._column_widths.values()])

    def _print_table_row(self, values, is_centered):
        """Prints a row of the table with the given values."""
        # Pad column widths (if necessary) so each row is the same width as the global width
        num_columns = len(values)
        column_widths = self._column_widths[num_columns]
        column = 0
        while sum(column_widths) + num_columns - 1 < self._width:
            column_widths[column] += 1
            column = (column + 1) % num_columns

        # Create the string
        value_str = "|"
        for value, column_width in zip(values, column_widths):
            centering = "^" if is_centered else "<"
            value_str += f" {value: {centering}{column_width - 2}} |"
        print(value_str)

    def _print_table_border(self):
        """Prints the borders of the table."""
        border_str = f"+{'=' * self._width}+"
        print(border_str)


def update_file(args, file):
    # Open config file
    config_parser = configparser.ConfigParser()
    config_parser.optionxform = str
    config_parser.read(file)

    table_writer = TableWriter()
    table_writer.add_header([str(file)])
    table_writer.add_header([""])
    table_writer.add_header(COLUMN_HEADERS)

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
