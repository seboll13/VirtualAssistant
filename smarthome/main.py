"""Home Assistant module."""
# imports
from pathlib import Path

from pytradfri import Gateway
from smarthome.command_executor import CommandExecutor

from smarthome.helpers import get_api_request, get_args, verify_args

# constants
ROOT_PATH = Path(__file__).parent.parent.resolve()
CONFIG_FILE = ROOT_PATH / "files/tradfri_standalone_psk.conf"


def main() -> None:
    """Main."""
    args = get_args()
    verify_args(args, str(CONFIG_FILE))

    api = get_api_request(args, str(CONFIG_FILE))
    gateway = Gateway()

    cmd = input('Enter a command: ')
    executor = CommandExecutor(cmd, api, gateway)
    executor.execute()


if __name__ == "__main__":
    main()