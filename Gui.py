
#region imports
import customtkinter as ctk
import keyboard
import tkinter as tk
from PIL import Image
from Commands import *
#endregion

#region Gui Custom Componants
"""Class for global UI variables Needed for shared Properties used throughut Ui Elements, Like themes"""
class UiGlobal:
    def __init__(self):
        self._theme:Theme = dark_default

    @property
    def theme(self):
        return self._theme

    @theme.setter
    def theme(self, theme:Theme):
        self._theme = theme
        Theme.theme_changed.emit(theme)

ui_global = UiGlobal()

"""Command for the changing of themes"""
@active_command
class ThemeChangeCommand(Command):
    def __init__(self, call_sign='theme'):
        super().__init__(call_sign)
        Theme.UnpackThemes()

    def execute(self, string:str):
        for theme in Theme.all_themes:
            if string.lower() == theme.name.lower():
                ui_global.theme = theme
    @property
    def description(self) -> str:
        return f"{self.call_sign}: Change theme. Available themes:\n {[theme.name for theme in Theme.all_themes]}"

#Emits a signal every time the text changes
class SignalTextVar(tk.StringVar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_changed = Signal()
        self.trace_add('write', lambda a, b, c: self._on_text_changed())

    def _on_text_changed(self):
        text = self.get()
        self.text_changed.emit(text)

#a button that can store a dictionary of metadata
class MetaButton(ctk.CTkButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._meta = {}
        self.button_clicked = Signal()
        self.configure(command = self.button_clicked.emit)
        Theme.theme_changed.connect(self._on_theme_change)
        self._on_theme_change(ui_global.theme)

    def set_meta(self, key, value):
        self._meta[key] = value

    def get_meta(self, key):
        return self._meta[key]

    def get_meta_dict(self):
        return self._meta

    def _on_theme_change(self, theme:Theme):
        self.configure(fg_color=theme.color_1, font=(theme.font_name, 16), text_color=theme.font_color,
                       hover_color=theme.color_3)


#region screenframes
#ABC for main frame
class ScreenFrame(ctk.CTkScrollableFrame):
    all_screens = []
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._meta = {}

    def set_meta(self, key, value):
        self._meta[key] = value

    def get_meta(self, key):
        return self._meta[key]

    def get_meta_dict(self):
        return self._meta

    def call(self, string:str):
        pass

# Label screenframe
class Labelframe(ScreenFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(corner_radius=0, border_width = 0)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._label = ctk.CTkLabel(self, text='xxx', justify='center', anchor='n', wraplength=self.winfo_screenwidth())
        self._label.grid(row=0, column=0, sticky='nsew')
        Theme.theme_changed.connect(self._on_theme_change)
        self._on_theme_change(ui_global.theme)

    @property
    def label(self):
        return self._label

    @property
    def label_text(self):
        return self._label.cget('text')

    @label_text.setter
    def label_text(self, value:str):
        self.label.configure(text=value)

    def call(self, string:str):
        self._label.configure(text=string)

    def _on_theme_change(self, theme:Theme):
        self.configure(fg_color=theme.color_2,scrollbar_button_color=theme.font_color, border_color=theme.color_3)
        self._label.configure(text_color=theme.font_color, font=(theme.font_name, 16))

class AutocompleteSection(ScreenFrame):
    def __init__(self, parent, list, input:ctk.CTkEntry):
        super().__init__(parent)
        self.configure(corner_radius=0, border_width=0)
        self.list = list
        self.input = input
        self._active = True
        self.columnconfigure(0, weight=1)

        #region Signals
        self.active_changed =  Signal()
        self.auto_pressed = Signal()
        Theme.theme_changed.connect(self._on_theme_change)
        self._on_theme_change(ui_global.theme)
        #endregion
    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self.active_changed.emit(value)
        self._active = value

    def on_button_clicked(self, button:MetaButton):
        text = button.get_meta('text')
        self.input.delete(0, tk.END)
        self.input.insert(tk.END, f'/{text}')
        self.pack_forget()
        self.auto_pressed.emit()

    def trigger_buttons(self, string):
        for button in self.winfo_children():
            button.destroy()
        if string == '/' or string == '':
            call_reset_geometry.emit()
            return
        row = 0
        for item in self.list:
            string = string.replace('/', '')
            if string in item:
                auto_button = MetaButton(self, text=item, fg_color= '#1a1a1a', hover_color= '#333333', text_color= '#cccccc',
                                         corner_radius=0)
                auto_button.button_clicked.connect(lambda b = auto_button: self.on_button_clicked(b))
                auto_button.set_meta('text', item)
                auto_button.grid(row=row, column=0, sticky='ew')
                row += 1

    def call(self, string:str):
        self.trigger_buttons(string)

    def _on_theme_change(self, theme:Theme):
        self.configure(fg_color=theme.color_2, scrollbar_button_color=theme.font_color, border_color=theme.color_3)

#endregion
#endregion

#region Application Gui
class App(ctk.CTk):
    def __init__(self):
        super(App, self).__init__()

        #region Constants
        self.STANDARD_HEIGHT = 30
        self.SCREEN_WIDTH_RATIO = 0.8
        self.FOCUS_OPACITY = 0.8
        self.UNFOCUSED_OPACITY = 0.2
        #endregion

        self.call_key = r"ctrl+shift+/"
        self._theme = dark_default

        #region Gui Signals and Lists
        self.commands = Command.all_commands
        self.popped_up = Signal()
        self.hidden = Signal()
        self.command_submitted = Signal()
        #used for allowing the arrow keys to Cycle through previous entries
        self.log = []
        self.log_no = 0
        #endregion

        #region Styling and setup
        self.title = "Custom Command Line"
        self.wm_title(self.title)
        self.icon = r"C:\Users\hp\PycharmProjects\CustomCommandLine\Icons\default_icon.ico"
        self.iconbitmap(self.icon)
        self.overrideredirect(True)
        self.wm_attributes("-alpha", 0.4)
        self.active = False
        self.resizable = True
        self.wm_attributes("-topmost", True)
        self._sort_geometry()
        self.configure(ipadx=10, ipady=10)
        #endregion

        #region Gui Widgets
        self.top_frame = ctk.CTkFrame(self, corner_radius=20, fg_color= 'transparent')
        self.top_frame.pack(side=ctk.TOP, fill='x', expand=False)

        raw_logo = Image.open(r"C:\Users\hp\PycharmProjects\CustomCommandLine\Icons\side_icon_a.png")
        self.logo_dimensions = (self.STANDARD_HEIGHT, self.STANDARD_HEIGHT)

        self.logo = ctk.CTkImage(raw_logo, size = self.logo_dimensions)
        self.logo_lab = ctk.CTkLabel(self.top_frame, text = '', image=self.logo)
        self.logo_lab.pack(side=ctk.LEFT)

        self.command_var = SignalTextVar()
        self.input_font_size = self.STANDARD_HEIGHT*0.6
        entry_width = int(self.winfo_screenwidth() * self.SCREEN_WIDTH_RATIO) - self.STANDARD_HEIGHT*2

        self.input_entry = ctk.CTkEntry(self.top_frame, placeholder_text= "/Enter Command",
                                        font=('DS-Digital', self.input_font_size), justify='center',
                                        corner_radius=0, border_width=0,width=entry_width,
                                        textvariable=self.command_var)

        self.input_entry.place(relx=0.5, rely=0.5, anchor='center')
        #endregion

        #region Screen frame
        """The screen frame is the bit that pops up below the bar at the bottom self.screenframe is switched out in
        the _on_screen_frame called function"""
        self.autocomplete = AutocompleteSection(self, Command.all_callsigns, self.input_entry)
        self.label_frame = Labelframe(self)
        self.screen_frame = Labelframe(self)
        #endregion

        #region hotkeys and bindings
        keyboard.add_hotkey(self.call_key, self._on_call_hotkey)
        self.input_entry.bind('<Return>', lambda event: self.submit_text())
        self.input_entry.bind('<Up>', lambda event: self._on_up_arrow_pressed())
        self.input_entry.bind('<Down>', lambda event: self._on_down_arrow_pressed())
        self.input_entry.bind("<FocusIn>", lambda event: self._on_focus())
        self.input_entry.bind('<FocusOut>', lambda event: self._on_focus_loss())
        #endregion

        #region Initial Setup
        self.hide()
        self._on_theme_changed(ui_global.theme)
        #endregion

        #region signal connectors
        self.command_var.text_changed.connect(self._on_text_changed)
        self.autocomplete.auto_pressed.connect(self._sort_geometry)

        close_app.connect(self.destroy)
        call_ui_hide.connect(self._on_call_ui_hide)
        call_ui_screen_frame.connect(self._on_screen_frame_called)

        call_reset_geometry.connect(self._sort_geometry)
        Theme.theme_changed.connect(self._on_theme_changed)
        ready.emit()
        #endregion


    def hide(self):
        self.log_no = 0
        self.input_entry.delete(0, 'end')
        self.input_entry.insert(0, '/')
        self._sort_geometry()
        self.hidden.emit()
        self.screen_frame.pack_forget()
        self.active = False
        self.withdraw()

    def pop_up(self):
        self.popped_up.emit()
        self.active = True
        self.deiconify()
        self.input_entry.focus_force()

    def submit_text(self):
        if self.input_entry.get():
            text = self.input_entry.get()
            self._on_text_submitted(text=text)
        else:
            self._on_call_ui_hide()
    #endregion

    #region Private Methods

    def _on_theme_changed(self, theme:Theme):
        self.configure(fg_color=theme.color_1)
        self.top_frame.configure(fg_color=theme.color_1)
        self.input_entry.configure(fg_color=theme.color_1, text_color=theme.font_color,
                                   font=(theme.font_name, self.input_font_size))
        new_img = Image.open(theme.logo_img)
        self.logo = ctk.CTkImage(new_img, size = self.logo_dimensions)
        self.logo_lab.configure(image=self.logo)


    def _on_text_changed(self, text):
        if ' ' in text:
            call_reset_geometry.emit()
            return
        call_ui_screen_frame.emit('auto', text, '100')

    def _sort_geometry(self, height_override = ''):
        if height_override == '':
            height_override = self.STANDARD_HEIGHT

        sw = self.winfo_screenwidth()
        width = sw * self.SCREEN_WIDTH_RATIO
        pos_x = sw/2 - width/2
        self.geometry(f'{int(width)}x{height_override}+{int(pos_x)}+15')

    def _on_text_submitted(self, text):
        active_command:Command = None
        self.log.append(text)
        pattern = re.compile(r"/(?P<call>\w+)\s(?P<command>.*)")
        if pattern.match(text):
            m = pattern.match(text)
            for command in self.commands:
                if command.call_sign == m.group('call'):
                    active_command = command
                    break
            if active_command:
                active_command.execute(m.group('command'))

    def _on_call_hotkey(self):
        if self.active:
            self.hide()
        else:
            self.pop_up()

    def _on_call_ui_hide(self):
        self.hide()

    def _on_screen_frame_called(self, type:str = 'label', string:str = '', height = '100'):
        self.screen_frame.pack_forget()
        match type.lower():
            case 'label':
                self.screen_frame = self.label_frame
            case 'auto':
                self.screen_frame = self.autocomplete
        self.screen_frame.pack(fill='both', expand=1)
        height = int(height) + self.input_entry._current_height
        self._sort_geometry(height_override=str(height))
        self.screen_frame.call(string)

    def _on_up_arrow_pressed(self):
        self.log_no -= 1
        if self.log_no < 0:
            self.log_no = len(self.log) - 1
        self._get_back_log()

    def _on_down_arrow_pressed(self):
        self.log_no += 1
        if self.log_no > len(self.log) - 1:
            self.log_no = 0
        self._get_back_log()

    def _get_back_log(self):
        if not self.log:
            return
        self.input_entry.delete(0, 'end')
        self.input_entry.insert(0, self.log[self.log_no])

    def _on_focus(self):
        self.wm_attributes("-alpha", self.FOCUS_OPACITY)

    def _on_focus_loss(self):
        self.wm_attributes("-alpha", self.UNFOCUSED_OPACITY)
    #endregion

#endregion
