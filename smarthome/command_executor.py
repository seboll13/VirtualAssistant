from logging import warning

from pytradfri import Gateway
from pytradfri.device import Device
from pytradfri.api.libcoap_api import APIFactory

from smarthome.helpers import get_lights


COMMAND_TYPES = ['control', 'query']
LIGHT_COMMANDS = ['lights_on', 'lights_off', 'turn_on', 'turn_off', 'dim', 'brighten', 'intensity']


def map_intensity(value: int) -> int:
    """Maps a percentage to a valid intensity value"""
    if value < 0 or value > 100:
        raise ValueError('Value must be between 0 and 100')
    return int(value * 254 / 100)


class CommandExecutor:
    """This class executes a home assistant related command"""
    def __init__(self, command: str, api: APIFactory.request, gateway: Gateway):
        self.keywords = [w.lower() for w in command.split(' ')]
        if self.keywords[0] not in LIGHT_COMMANDS:
            raise NotImplementedError('Command not supported')
        self.keywords[:0] = ['control']
        self.api = api
        self.gateway = gateway


    def change_light_state(self, light: Device, state: bool) -> None:
        """Changes the state of a light"""
        if not light.has_light_control:
            raise ValueError('Device must be a light')
        if light.light_control.lights[0].state == state:
            warning('Light is already in this state')
            return
        self.api(light.light_control.set_state(state))


    def change_light_intensity(self, light: Device, intensity: int) -> None:
        """Changes the intensity of a light"""
        if not light.has_light_control:
            raise ValueError('Device must be a light')
        self.api(light.light_control.set_dimmer(intensity))


    def change_all_lights_states(self, state: bool) -> None:
        """Changes the state of all lights at once"""
        for light in get_lights(self.api, self.gateway):
            self.change_light_state(light, state)


    def execute(self) -> None:
        """Executes the given command"""
        if self.keywords[0] == 'control':
            if self.keywords[1].startswith('lights_'):
                self.change_all_lights_states(self.keywords[1] == 'lights_on')
            elif self.keywords[1].startswith('turn_'):
                light = get_lights(self.api, self.gateway)[0]
                self.change_light_state(light, self.keywords[1] == 'turn_on')
            elif self.keywords[1] in ['dim', 'brighten', 'intensity']:
                intensity = map_intensity(int(self.keywords[2]))
                light = get_lights(self.api, self.gateway)[0]
                self.change_light_intensity(light, intensity)
            else:
                print('Congratulations, you found a bug!')
        else:
            raise NotImplementedError('Querying is not supported yet')
        print('done')