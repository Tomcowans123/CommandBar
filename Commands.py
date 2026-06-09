#region Imports
from Config import *
import re
import random as r
import os
import json
import webbrowser
from BatchClass import Batch
#endregion

# region command-class_scripts

#region ReadMe
"""To Add commands just create a class that inherits from the Command Abstract class with an execute function
that accepts a string argument, using the @active_command decorator will cause the command to be automatically
instantiated and added to the list of commands that the Command Line can use
also be sure to add the description so the help command can remind you how it works."""
#endregion

@active_command
class Operation(Command):
    def __init__(self, call_sign='ops', *args, **kwargs):
        super().__init__(call_sign, *args, **kwargs)

        self.operations = {
            'close': self._close_app,
        }

    @staticmethod
    def _close_app():
        close_app.emit()

    def execute(self, text):
        for k, v in self.operations.items():
            if text.lower() == k.lower():
                v()

    @property
    def description(self):
        return f"""
/{self.call_sign}: Allows for Control Pannal Operations,
close: Closes the Command Line"""

@active_command
class Dice(Command):
    def __init__(self, call_sign='roll', *args, **kwargs):
        super().__init__(call_sign, *args, **kwargs)

    @property
    def description(self):
        return f"""
        /{self.call_sign}: Rolls a dice.
        Using a standard Dice Pattern such as 2d6 or 1d8+2
        """

    def execute(self, string: str):
        dice_pattern = re.compile(r"(?P<ammount>\d+)d(?P<max_val>\d+)(\+(?P<modifier>\d+))?")
        result = dice_pattern.search(string)
        if result:
            ammount = int(result.group('ammount'))
            max_val = int(result.group('max_val'))
            mod = 0
            if result.group('modifier'):
                mod = int(result.group('modifier'))
            d_results = []
            for i in range(ammount):
                d_results.append(r.randint(1, max_val))
            display_text(f"Result: {sum(d_results) + mod}")
        else:
            print(string)

@active_command
class Note(Command):
    def __init__(self, call_sign='note', *args, **kwargs):
        super().__init__(call_sign, *args, **kwargs)

    @property
    def note_path(self):
        return json.load(open(json_save_path))['paths']['obsidian']

    @property
    def description(self):
        return f"""
        /{self.call_sign}: Creates a quick note. in obsidian.
        use the following text format (title)::(note text)
        """

    def execute(self, string: str):
        temp = re.compile(r"(?P<title>.*)::(?P<note>.*)")
        result = temp.search(string)
        if self.note_path:
            if result:
                with open(f"{self.note_path}/{result.group('title')}.md", "w") as f:
                    f.write(result.group('note'))
                call_ui_hide.emit()
            else:
                call_ui_screen_frame.emit('Invalid note format, please try {title}::{note}', '100', 1000)
        else:
            display_text("Obsidian Path Not Specified, Please Type /add_path obsidian::{obsidian's file path} to save the path")

@active_command
class AddPath(Command):
    def __init__(self, call_sign='add_path', *args, **kwargs):
        super().__init__(call_sign, *args, **kwargs)

    def execute(self, string: str):
        temp = re.compile("(?P<name>.*)::(?P<path>.*)")
        result = temp.search(string)
        path = result.group('path')
        name = result.group('name')
        if Path(path).exists():
            json_path = json.load(open(user_data.json_path, "r"))
            json_path["paths"].update({name: path})
            json.dump(json_path, open(user_data.json_path, "w"), indent="\t")
            call_ui_hide.emit()
        else:
            display_text("The Path Does Not Exist")

    @property
    def description(self):
        return f"""/{self.call_sign}: saves paths to programs that can be used in other commands,
        I.E. /note requires a valid path to an obsidian vault to use correctly."""

@active_command
class EvalCommand(Command):
    def __init__(self, call_sign='calc', *args, **kwargs):
        super().__init__(call_sign, *args, **kwargs)

    # TODO add allowed Global Functions
    def execute(self, string: str):
        try:
            string = string.replace('x', '*').replace('X', '*')
            result = eval(string)
            if result:
                display_text(f"Result: {result}")
            else:
                call_ui_hide.emit()
        except Exception as e:
            call_ui_screen_frame.emit("label", f"Error: {e}")

    @property
    def description(self):
        return f"""
        /{self.call_sign}: Evaluates a python expression.
        can be used as a calculator.
        """

@active_command
class RunEXECommand(Command):
    def __init__(self, call_sign='run', *args, **kwargs):
        super().__init__(call_sign, *args, **kwargs)
        self.user_data_path = json_save_path
        self._check_exe_json()

    def execute(self, string: str):
        if not string.startswith('save:: '):
            self._execute_open(string)
        else:
            self._execute_save(string)
        call_ui_hide.emit()

    def _execute_save(self, string):
        pattern = re.compile(r"save:: (?P<path>.*)\[(?P<sudo>\w*)]")
        result = pattern.search(string)
        if not result:
            return
        self._add_save_path(result.group('path'), result.group('sudo'))

    def _execute_open(self, string):
        executable_path = string
        if not executable_path.lower().startswith('c:'):
            executable_path = self._search_json_match(string)
        self._open_exe(executable_path)

    def _search_json_match(self, string: str):
        save_dict = json.load(open(self.user_data_path))
        try:
            for k, v in save_dict["executables"].items():
                if string.lower() == k.lower():
                    return v
        except KeyError:
            save_dict["executables"] = {}
            json.dump(save_dict, open(self.user_data_path))
        return None

    def _add_save_path(self, path: str, sudo: str):
        save_dict = json.load(open(self.user_data_path, 'r'))
        save_dict["executables"].update({sudo: path})
        json.dump(obj=save_dict, fp=open(self.user_data_path, "w"), indent="\t")

    @staticmethod
    def _open_exe(string: str):
        if not string:
            return
        if not os.path.exists(string):
            return
        os.startfile(string)

    @property
    def description(self):
        user_data = json.load(open(self.user_data_path))
        desc = f"""
        /{self.call_sign}: Runs an EXE from the command line.

        can also be used to save a file path to favorites under a sudonym.

        to run type /{self.call_sign} c/file_path.exe (or saved sudonym),

        to save, type /{self.call_sign} save:: c:/file_path.exe[sudonym], (sudonym must not end with .exe)

        """
        if user_data['executables']:
            desc += f"Your current saved executables are:\n\n"
            for k, v in user_data['executables'].items():
                desc += f"\n{k}: {v}\n"
        else:
            desc += f"You have no current saved executables."
        return desc

    def _check_exe_json(self):
        if not json.load(open(self.user_data_path)).get('executables'):
            save_data = json.load(open(self.user_data_path, 'r'))
            save_data['executables'] = {}
            json.dump(obj=save_data, fp=open(self.user_data_path, 'w'))

@active_command
class GoogleSearch(Command):
    def __init__(self, call_sign='google', *args, **kwargs):
        super().__init__(call_sign, *args, **kwargs)

    @property
    def description(self):
        return f"""/{self.call_sign}: Search Google."""

    def execute(self, string: str):
        self._open_url(string)

    @staticmethod
    def _open_url(string: str):
        search_url = f'https://www.google.com/search?q={string.replace(" ", "+")}'
        webbrowser.open(search_url, 0)
        call_ui_hide.emit()

@active_command
class HelpCommand(Command):
    def __init__(self, call_sign='help', *args, **kwargs):
        super().__init__(call_sign, *args, **kwargs)

    @property
    def description(self):
        return f"""
        /{self.call_sign}: Shows help about commands.

        /{self.call_sign} followed by a callsign shows the individual commands description.

        /{self.call_sign} on its own Shows help about all commands
        """

    def execute(self, string: str):
        if string != 'all':
            for command in self.all_commands:
                if string in command.call_sign:
                    desc = command.description
                    desc_len = len(desc.split('\n')) * 12
                    if desc_len < 100:
                        desc_len = 100
                    display_text(desc, str(desc_len))
        else:
            command_lib_help = [command.description for command in self.all_commands]
            help_text = f""
            for txt in command_lib_help:
                help_text += f"\n{txt}"

            display_text(help_text, '400')

@active_command
class WebCommand(Command):
    def __init__(self, call_sign='web', *args, **kwargs):
        super().__init__(call_sign, *args, **kwargs)
        self.user_data = json_save_path
        self._check_web_json()

    @property
    def description(self) -> str:
        x = f"""
        /{self.call_sign}: can go to web pages directly.
        /{self.call_sign} save:: url[sudonym],
        /{self.call_sign} delete:: sudonym, will remove the saved website
        allows you to save a webpage under a sudonym and just type the sudonym instead of the
        full address.
        """
        save_dict = json.load(open(self.user_data))
        if save_dict['web-pages'] != {}:
            x += '\n you have the following web pages saved:\n'
            for k, v in save_dict['web-pages'].items():
                x += f"\n{k}: {v}\n"
        return x

    def execute(self, string: str):
        temp = re.compile(r'(?P<sub_command>\w*):: (?P<prompt>.*)')
        if temp.match(string):
            m = temp.search(string)
            match m.group('sub_command'):
                case 'save':
                    self._save_url(m.group('prompt'))
                case 'delete':
                    self._delete_sudonym(m.group('prompt'))
        else:
            try:
                url = string
                searched_url = self._search_sudonym(string)
                if searched_url:
                    url = searched_url
                self._open_url(url)

            except Exception as e:
                call_ui_screen_frame.emit(str(e))
        call_ui_hide.emit()

    def _delete_sudonym(self, name: str):
        save_dict = json.load(open(self.user_data))
        web_pages = save_dict['web-pages']
        if name in dict(web_pages).keys():
            web_pages.pop(name)
        json.dump(obj=save_dict, fp=open(self.user_data, "w"))

    def _search_sudonym(self, string: str):
        saved = json.load(open(self.user_data))
        web_pages = {}
        try:
            web_pages = saved["web-pages"]
        except KeyError:
            saved["web-pages"] = {}
            json.dump(saved, open(self.user_data))
        if string in web_pages.keys():
            return web_pages[string]
        else:
            return None

    def _save_url(self, string: str):
        pattern = re.compile(r"(?P<path>.*)\[(?P<sudo>.*)]")
        result = pattern.search(string)
        if not result:
            print(string)
            return
        self._add_save_path(result.group('path'), result.group('sudo'))

    def _add_save_path(self, path: str, sudo: str):
        save_dict = json.load(open(self.user_data, 'r'))
        save_dict["web-pages"].update({sudo: path})
        json.dump(obj=save_dict, fp=open(self.user_data, "w"), indent="\t")

    @staticmethod
    def _open_url(string: str):
        webbrowser.open(string)
        call_ui_hide.emit()

    def _check_web_json(self):
        if not json.load(open(self.user_data, 'r')).get('web-pages'):
            save_data = json.load(open(self.user_data))
            save_data['web-pages'] = {}
            json.dump(obj=save_data, fp=open(self.user_data, 'w'))

@active_command
class YoutubeSearch(Command):
    def __init__(self, call_sign='youtube', *args, **kwargs):
        super().__init__(call_sign, *args, **kwargs)

    @property
    def description(self) -> str:
        return f"{self.call_sign}: Search YouTube videos."

    def execute(self, string: str):
        self._open_url(string)

    def _open_url(self, string: str):
        search_url = f"https://www.youtube.com/results?search_query={string.replace(' ', '+')}"
        webbrowser.open(search_url, 0)
        call_ui_hide.emit()

@active_command
class BatchCall(Command):
    def __init__(self, call_sign='batch', *args, **kwargs):
        super().__init__(call_sign, *args, **kwargs)
        self._check_batch_json()
        Batch.instantiate_saved_batches()

    @property
    def description(self) -> str:
        readme = ''
        with open(root / "Readmes/BatchCommandReadMe.txt", 'r') as f:
            readme = f.read()
        return f"""/{self.call_sign} Call A batch file.
Batch files can be called by simply writing /{self.call_sign} batchpath.bat however...
{readme}"""

    def _try_execute_path(self, path: str):
        if os.path.exists(path):
            try:
                instance = Batch(path)
                instance.run_path = path
                instance.run_batch()
            except Exception as e:
                print(e)
                return False
            return True
        else:
            return False

    def _process_command(self, string: str):
        x = re.match(r"(?P<sub_command>\w*):: (?P<prompt>.*)", string)
        if not x:
            can_execute = self._try_execute_path(string)
            if not can_execute:
                display_text('Batch File Failed to run, Check Batch Path')
            else:
                display_text('Batch File Successfully Running')
        sub_command = x.group('sub_command')
        prompt = x.group('prompt')
        match sub_command:
            case 'save':
                self._save_batch_from(prompt)
            case 'help':
                self._get_batch_help(prompt)
            case 'run':
                self._run_batch_command(prompt)

    def _save_batch_from(self, string: str):
        save_pattern = re.match(r"(?P<path>.*)\[(?P<sudo>.*)]", string)
        if not save_pattern:
            display_text('Batch File Failed to save, Check Command Description')
        elif not os.path.isdir(save_pattern.group('path')):
            display_text('Batch File Failed to save, Check Save Path')
        elif not save_pattern.group('sudo'):
            display_text('Batch File Failed to save, Check Save Pseudonym')
        else:
            Batch(save_pattern.group('path'), save_pattern.group('sudo')).save_path()
            display_text(f'Batch File Successfully Saved under name {save_pattern.group("sudo")}')

    def _get_batch_help(self, string: str):
        match string.lower():
            case 'saved':
                display = "Your Current Saved Batch Files are:\n"
                for batch in Batch.all_batches:
                    display += f"\n{batch.sudo}: {batch.directory}\n"
                    if os.path.exists(batch.read_path):
                        display += f"\n{open(batch.read_path,'r').read()}\n"
            case _:
                x:Batch = self._get_saved_batch_from_sudo(string)
                if not x:
                    display_text('failed to find saved path')
                else:
                    if os.path.exists(x.read_path):
                        with open(x.read_path, 'r') as f:
                            display_text(f.read(), '400')
                    else:
                        display_text('failed to find readme.txt path within saved directory')

    def _run_batch_command(self, string: str):
        pattern = re.match(r"(?P<sudo>\w*)(\[(?P<vars>.*)])?", string)
        batch_name = pattern.group('sudo')
        batch: Batch = self._get_saved_batch_from_sudo(batch_name)
        if not pattern.group('vars'):
            if not batch:
                display_text('failed to find saved path')
                print([b.sudo for b in Batch.all_batches])
                return
            else:
                batch.run_batch()
                print(batch.run_path)
                display_text(f'Batch: {batch_name} File Successfully Running')
                return
        else:
            vdict = {}
            var_list = pattern.group('vars').split(', ')
            for var in var_list:
                key, value = var.split('=')
                vdict[key] = value
            try:
                batch.write_init(vdict)
                batch.run_batch()
            except Exception as e:
                display_text(e)

    def _get_saved_batch_from_sudo(self, string):
        for batch in Batch.all_batches:
            if batch.sudo.lower() == string.lower():
                return batch
            else:
                return None

    def _check_batch_json(self):
        if not json.load(open(json_save_path, 'r')).get('batch_saves'):
            save_data = json.load(open(json_save_path))
            save_data['batch_saves'] = {}
            json.dump(obj=save_data, fp=open(json_save_path, 'w'))

    def execute(self, string: str):
        self._process_command(string)

# endregion