import logging
from uuid import uuid4
from functools import wraps
from time import perf_counter
from argparse import ArgumentParser, Namespace
from pytradfri import Gateway, PytradfriError
from pytradfri.util import load_json, save_json
from pytradfri.api.libcoap_api import APIFactory


logging.basicConfig(level=logging.INFO)


# timer decorator
def timer(func):
    """Prints the runtime of the decorated function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        res = func(*args, **kwargs)
        end = perf_counter()
        logging.info('Elapsed time of %s: %.3f [s]', func.__name__, (end - start))
        return res
    return wrapper


def get_args() -> Namespace:
    """Get arguments from command line.
    
    :return: An object containing the command-line arguments.
    """
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
    """Verifies the validity of the arguments
    
    :param args: An object containing the command-line arguments.
    :param conf_file: The path to the JSON configuration file.
    :raises PytradfriError: If the security code is not provided.
    """
    if args.host not in load_json(conf_file) and args.key is None:
        print(
            "Please provide the 'Security Code' on the back of your Tradfri gateway:",
            end=" ",
        )
        key = input().strip()
        if len(key) != 16:
            raise PytradfriError("Invalid 'Security Code' provided.")
        args.key = key


def get_api_request(args: Namespace, config_file: str) -> APIFactory.request:
    """Returns an API request object for the specified host.
        
    :param args: An object containing the command-line arguments.
    :param config_file: The path to the JSON configuration file.
    :return: An API request object for the specified host.
    :raises PytradfriError: If the security code is not provided.
    """
    conf = load_json(config_file)

    try:
        identity = conf[args.host].get("identity")
        psk = conf[args.host].get("key")
        api_factory = APIFactory(host=args.host, psk_id=identity, psk=psk)
    except KeyError:
        identity = uuid4().hex
        api_factory = APIFactory(host=args.host, psk_id=identity)
        try:
            psk = api_factory.generate_psk(args.key)
            print("Generated PSK: ", psk)

            conf[args.host] = {"identity": identity, "key": psk}
            save_json(config_file, conf)
        except AttributeError as err:
            raise PytradfriError(
                "Please provide the 'Security Code' on the back of your Tradfri gateway "
                "using the -K flag."
            ) from err
    return api_factory.request


@timer
def get_devices(api: APIFactory.request, gateway: Gateway) -> list:
    """Returns a list of devices.
    
    :param api: An API request object for the specified host.
    :return: A list of devices.
    """
    return api(api(gateway.get_devices()))


def get_lights(api: APIFactory.request, gateway: Gateway) -> list:
    """Returns a list of lights.
    
    :param api: An API request object for the specified host.
    :return: A list of lights.
    """
    return [dev for dev in get_devices(api, gateway) if dev.has_light_control]