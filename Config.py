# region imports
import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
import importlib.util
# endregion


#region userdata
class UserData:
    def __init__(self):
        self.root:Path = Path(__file__).parent.resolve()
        self.json_path = self.root / 'save_data' / 'user_data.json'
        self.theme_icons_file = self.root /'Icons' / 'theme_icons'
        self.log_path = self.root / 'save_data' / 'log.json'

user_data = UserData()
# region Setup Classes
"""
Signal Class that mirrors Godots Signal class.
"""


class Signal:
    def __init__(self):
        self.connections = []
        self.active = True

    def connect(self, connection):
        if not self.active:
            return
        self.connections.append(connection)

    def disconnect(self, connection):
        if not self.active:
            return
        self.connections.remove(connection)

    def emit(self, *args):
        if not self.connections or not self.active:
            return
        for connection in self.connections:
            try:
                connection(*args)
            except Exception as e:
                print(e)

    @staticmethod
    def mass_connect(connections: dict):
        for key, value in connections.items():
            if not isinstance(key, Signal):
                print('trying to connect signal {}'.format(key))
            if not isinstance(value, list):
                key.connect(value)
            else:
                for func in value:
                    key.connect(func)

    def preconnect(self, function):
        self.connect(function)
        return function


"""
every commands abstract base class, every command is appended to a list of all avalable commands,
when writing the command class make sure to add the @active_command decorator to each command to have it be active within the,
command bar and usable.
then can be used by the user in the command line, in the command line the user can call a command with:
/ + the commands call sign + a space + the string that is passed to the commands execute() function.
"""


class Command(ABC):
    all_commands = []
    all_callsigns = []

    def __init__(self, call_sign, *args, **kwargs):
        self.call_sign = call_sign

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass

    @abstractmethod
    def description(self) -> str:
        pass


# region Ui Theme Class
class Theme:
    theme_changed = Signal()
    all_themes = []
    themes_dir = user_data.theme_icons_file / 'user_themes' / 'user_themes.json'

    def __init__(self, name: str, color_1: str = 'black', color_2: str = 'black', color_3: str = 'black',
                 color_4: str = 'black', color_5: str = 'black', font_color: str = 'white', font_name: str = '',
                 _logo_img: str = r"DarkDefaultIcon.png"):
        self.name = name
        self.color_1 = color_1
        self.color_2 = color_2
        self.color_3 = color_3
        self.color_4 = color_4
        self.color_5 = color_5
        self.font_color = font_color
        self.font_name = font_name
        self._logo_img = _logo_img
        Theme.all_themes.append(self)

    @property
    def logo_img(self):
        if self._logo_img.startswith('c:'):
            return self._logo_img
        else:
            return user_data.theme_icons_file / self._logo_img

    @logo_img.setter
    def logo_img(self, value):
        self._logo_img = value

    @staticmethod
    def UnpackThemes():
        load = json.load(open(Theme.themes_dir, 'r'))
        for theme in load['Themes']:
            instance  = Theme(**theme)


# endregion

# endregion


# region Global Signals and variables
root = user_data.root

json_save_path = user_data.json_path

"""
close app signal will cause the application to close itself.
"""
close_app = Signal()
"""
call_ui_hide will make the ui withdraw loosing is visibility
"""
call_ui_hide = Signal()
"""
call_ui_text_change is called each time the text in the command line is changed and is emmitted
with whatever is in the command entry each time the text changes.
"""
call_ui_text_change = Signal()
"""
call_ui_screen_frame signal calls a scrollable frame in the ui that can be used to display text
you can call the ui with 3 positional arguments, the first is "label" to display text, the second is a
 what text you want to display and  the third is a string controlling the height of the frame
(this is optional and defaults to 70). 
"""
call_ui_screen_frame = Signal()
"""
Ready signal is emitted once when the UI opens for the first time and is emitted with the app itself,
as a variable if you want to connect to it with a function not using this, connect with a lamba function.
it can be connected to with set up functions if they are needed.
"""
ready = Signal()

"""a signal that when called resets the geometry of the console to only show the bar"""
call_reset_geometry = Signal()

# endregion

"""Handles Plugin functionality"""
def load_plugins():
    plugins_dir = root / 'plugins'
    if not plugins_dir.exists():
        os.mkdir(plugins_dir)
        return
    for file in plugins_dir.glob('*.py'):
        spec = importlib.util.spec_from_file_location(file.stem, file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

# region Instanciating Default Theme
"""FOR INSTRUCTIONS ABOUT ADDING CUSTOM THEMES SEE -> CustomThemeReadMe.txt"""
dark_default = Theme('Dark', color_1='#000000', color_2='#262626', color_3='#4d4d4d',
                      color_4='#737373', color_5='#999999', font_color='#ffffff', font_name='Cascadia Mono',
                      _logo_img= "DarkDefaultIcon.png")

#Region Global Function

'''Decorator for command classes to have them be active in the command bar, removing decorator will disable them'''
def active_command(cls):
    instance = cls()
    if not isinstance(instance, Command):
        raise TypeError(f"The class '{cls.__name__}' is not a Command")
    Command.all_commands.append(instance)
    Command.all_callsigns.append(instance.call_sign)
    return instance

"""Function to Display text called by commands"""
def display_text(text, frame_size = '100'):
    call_ui_screen_frame.emit('label', text, frame_size)
#endregion

