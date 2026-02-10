# Python Command Bar

The Python Command Bar is an application I developed for python developers to expand upon and customise, allowing them to personalise it to their own specifications. the project uses regex to parse the string typed in the console command bar and execute a variety of commands based on user input, the console is designed with modularity and scalability in mind making it easy for other developers to add or remove commands and personalise the functionality of the command bar to their own needs and specifications.

**Commands Out of the box:**
Out of the box the python command bar has several useful commands and features built in.
- **Web Saving:**
	- **Callsign:** /web
	- Python console allows users to save certain web URLs under pseudonyms and launch them from the bar using those pseudonyms for quick and easy access from anywhere on the PC.
- **Executable launching:**
	- **Callsign:** /run
	- The console also allows users to save Executable file paths under a pseudonym and launch it from anywhere on the PC.
- **Evaluating Python Strings:**
	- **Callsign:** /calc
	- allows the user to reserialize and evaluate single line python expressions straight from the command bar, its primary use is as an advanced calculator that shows the output of any calculation in the dropdown of the bar.
- **Theme:**
	- **Callsign:** /theme 
	- allows the user to change the theme of the command bar to any of the built in themes, themes can be easily added by the user by editing a Json file
- **Batch File calling:**
	- **Callsign:** /batch
	- Allows the user to save batch files within the console bar and call them with custom variables, this is useful for running quick automation scripts and the guide for setting up batch files in a way that integrates seamlessly with the command bar can be seen under the help command
- **Help:**
	- **Callsign:** /help
	- Help allows the user to see the documentation/description of each of the commands by simply typing /help followed by the callsign of the command that the user needs help with. /help will bring up the documentation of each of the commands.
- **Other Features:**
	- The command bar has an autocomplete feature allowing the user to begin typing a callsign and the autocomplete will show up with all the callsigns matching the text in the command bar.
	- The command bar also allows users to repeat previous commands by using the up and down arrows on the key-board.
	- The command bar is able to be shown or hidden by using the \<ctrl>+\<shift>+\</> keys.
