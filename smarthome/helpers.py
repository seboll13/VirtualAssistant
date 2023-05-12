from argparse import ArgumentParser, Namespace
from pytradfri import PytradfriError
from pytradfri.util import load_json


def get_args() -> Namespace:
    """Get arguments."""
    parser = ArgumentParser()
    parser.add_argument(
        "host", metavar="IP", type=str, help="IP Address of your Tradfri gateway"
    )
    parser.add_argument(
        "-K",
        "--key",
        dest="key",
        required=False,
        help="Security code found on your Tradfri gateway",
    )
    return parser.parse_args()


def verify_args(args: Namespace, conf_file: str) -> None:
    """Verify the validity of the arguments"""
    if args.host not in load_json(conf_file) and args.key is None:
        print(
            "Please provide the 'Security Code' on the back of your Tradfri gateway:",
            end=" ",
        )
        key = input().strip()
        if len(key) != 16:
            raise PytradfriError("Invalid 'Security Code' provided.")

        args.key = key