import argparse
import pathlib
import configparser


INPUTS_CONFIG_FILE = pathlib.Path("C:\Riot Games\League of Legends\Config\Input.ini").resolve()

LEAGUE_VALUE = "league"
TFT_VALUE =  "tft"

FIELDS_TO_CHANGE = {
    "GameEvents": {
        "evtPlayerAttackMoveClick": {
            LEAGUE_VALUE: "[Button 1]",
            TFT_VALUE: "[<Unbound>]",
        },
        "evtPlayerAttackMove": {
            LEAGUE_VALUE: "[Button 1],[<Unbound>]",
            TFT_VALUE: "[<Unbound>],[<Unbound>]",
        },
    }
}


def main():
    parser = argparse.ArgumentParser(prog="SettingsConverter", description="Used for converting: League Setting <--> TFT_VALUE Settings")
    parser.add_argument("-t", "--target", type=str, choices=["league", "tft"], required=True)
    args = parser.parse_args()

    # Open config file
    config_parser = configparser.ConfigParser()
    config_parser.optionxform = str
    config_parser.read(INPUTS_CONFIG_FILE)

    field_width = 1 + max(len(field_name) + len(section_name) for section_name, section in FIELDS_TO_CHANGE.items() for field_name in section.keys())

    for section, fields in FIELDS_TO_CHANGE.items():
        if section not in config_parser:
            print(f"ERROR: No section '{section}' found")
            continue

        for field, values in fields.items():
            desired_value = values[TFT_VALUE] if args.target == "tft" else values[LEAGUE_VALUE]

            if field not in config_parser[section]:
                print(f"ERROR: Field '{field}' in section '{section}' not found")
            else:
                field_string = "{0: <{1}}".format(f"{section}.{field}", field_width)
                print(f"{field_string}: {desired_value}")
                config_parser[section][field] = desired_value

    # Write the new config file
    with open(INPUTS_CONFIG_FILE, "w") as settings_file:
        config_parser.write(settings_file, space_around_delimiters=False)


if __name__ == "__main__":
    main()