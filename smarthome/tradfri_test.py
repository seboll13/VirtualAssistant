#!/usr/bin/env python3
# Example MAC: A0:CC:2B:FD:49:ED
"""Example of how the pytradfri-library can be used.

To run the script, do the following:
$ pip3 install pytradfri
$ Download this file (example_sync.py)
$ python3 example_sync.py <IP>

Where <IP> is the address to your IKEA gateway. The first time
running you will be asked to input the 'Security Code' found on
the back of your IKEA gateway.
"""

import argparse
import os
import sys
import threading
import time
import uuid

# Hack to allow relative import above top level package

folder = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(f"{folder}/.."))

# pylint: disable=import-error, wrong-import-position, useless-suppression, not-an-iterable, unsubscriptable-object # noqa: E501

from pytradfri import Gateway
from pytradfri.api.libcoap_api import APIFactory, APIRequestProtocol
from pytradfri.device import Device
from pytradfri.error import PytradfriError
from pytradfri.resource import ApiResource
from pytradfri.util import load_json, save_json

CONFIG_FILE = "../files/tradfri_standalone_psk.conf"


parser = argparse.ArgumentParser()
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
args = parser.parse_args()


if args.host not in load_json(CONFIG_FILE) and args.key is None:
    print(
        "Please provide the 'Security Code' on the back of your Tradfri gateway:",
        end=" ",
    )
    key = input().strip()
    if len(key) != 16:
        raise PytradfriError("Invalid 'Security Code' provided.")

    args.key = key


def observe(api: APIRequestProtocol, device: Device) -> None:
    """Observe."""

    def callback(updated_device: ApiResource) -> None:
        assert isinstance(updated_device, Device)
        assert updated_device.light_control is not None
        light = updated_device.light_control.lights[0]
        print(f"Received message for: {light}")

    def err_callback(err: Exception) -> None:
        print(err)

    def worker() -> None:
        api(device.observe(callback, err_callback, duration=120))

    threading.Thread(target=worker, daemon=True).start()
    print("Sleeping to start observation task")
    time.sleep(1)


def run() -> None:
    """Run."""
    # Assign configuration variables.
    # The configuration check takes care they are present.
    conf = load_json(CONFIG_FILE)

    try:
        identity = conf[args.host].get("identity")
        psk = conf[args.host].get("key")
        api_factory = APIFactory(host=args.host, psk_id=identity, psk=psk)
    except KeyError:
        identity = uuid.uuid4().hex
        api_factory = APIFactory(host=args.host, psk_id=identity)

        try:
            psk = api_factory.generate_psk(args.key)
            print("Generated PSK: ", psk)

            conf[args.host] = {"identity": identity, "key": psk}
            save_json(CONFIG_FILE, conf)
        except AttributeError as err:
            raise PytradfriError(
                "Please provide the 'Security Code' on the "
                "back of your Tradfri gateway using the "
                "-K flag."
            ) from err

    api = api_factory.request

    gateway = Gateway()

    devices_command = gateway.get_devices()
    devices_commands = api(devices_command)
    devices = api(devices_commands)

    lights = [dev for dev in devices if dev.has_light_control]

    # Print all lights
    print(lights)

    # Lights can be accessed by its index, so lights[1] is the second light
    if lights:
        light = lights[0]
    else:
        print("No lights found!")
        light = None

    if light:
        observe(api, light)

        assert light.light_control is not None
        # Example 1: checks state of the light (true=on)
        print(f"State: {light.light_control.lights[0].state}")

        # Example 2: get dimmer level of the light
        print(f"Dimmer: {light.light_control.lights[0].dimmer}")

        # Example 3: What is the name of the light
        print(f"Name: {light.name}")

        # Example 4: Set the light level of the light
        dim_command = light.light_control.set_dimmer(254)
        api(dim_command)

        # Example 5: Change color of the light
        # f5faf6 = cold | f1e0b5 = normal | efd275 = warm
        color_command = light.light_control.set_color_temp(250)
        api(color_command)

    # Get all blinds
    blinds = [dev for dev in devices if dev.has_blind_control]

    # Print all blinds
    print(blinds)

    if blinds:
        blind = blinds[0]
    else:
        print("No blinds found!")
        blind = None

    if blind:
        assert blind.blind_control is not None
        blind_command = blind.blind_control.set_state(50)
        api(blind_command)

    tasks_command = gateway.get_smart_tasks()
    tasks_commands = api(tasks_command)
    if tasks := api(tasks_commands):
        # Example 6: Return the transition time (in minutes) for task#1
        task = tasks[0]
    else:
        print("No tasks found!")
        task = None

    if task:
        if task_control_tasks := task.task_control.tasks:
            task_control_task = task_control_tasks[0]
            print(task_control_task.transition_time)

            # Example 7: Set the dimmer stop value to 30 for light#1 in task#1
            dim_command_2 = task_control_task.item_controller.set_dimmer(30)
            api(dim_command_2)

    if light:
        print("Sleeping for 2 min to listen for more observation events")
        print(
            f"Try altering the light ({light.name}) in the app, and watch the events!"
        )
        time.sleep(120)


if __name__ == '__main__':
    run()