#region Setup for batch file opening
import os
import sys
# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Add that directory to the system path so Python searches there for modules
sys.path.append(script_dir)
os.chdir(script_dir)
#endregion

from Gui import App

app = App()
if __name__ == '__main__':
    app.hide()
    app.mainloop()
