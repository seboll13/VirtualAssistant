# imports
from pathlib import Path

from helpers import get_args, verify_args

# constants
ROOT_PATH = Path(__file__).parent.parent.resolve()
CONFIG_FILE = ROOT_PATH / "files/tradfri_standalone_psk.conf"


def main() -> None:
    """Main."""
    args = get_args()
    verify_args(args, str(CONFIG_FILE))
    pass


if __name__ == "__main__":
    main()