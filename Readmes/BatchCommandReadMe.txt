
batch file command is primarily designed to be used with directories
set up in the following way:

---------------------------------------------------------------------------------
an optional init.txt:
this file that can hold starting variables that can be read by the program you are opening
with the batch file, these variables should be structured in key value pairs like so:

key_1::value_1
key_2::value_2

these can be modified by your command strip directly however this isn't required.

---------------------------------------------------------------------------------

an optional readme.txt file:
this can be used as a description of the batch file as well as
an explanation of which variables within
the init.tct file are changeable and what they do

----------------------------------------------------------------------------------
REQUIRED run.bat:
make sure to have the run.bat in the directory you are referencing named run.bat.
---------------------------------------------------------------------------------

=================================================================================
COMMANDS:
=================================================================================

you can save the file path under a pseudonym by writing:

save:: c://filepath[pseudonym]

This save it under whatever pseudonym you want within the command bar
----------------------------------------------------------------------------------
you can run the saved bat on its own by just writing:

run:: pseudonym

----------------------------------------------------------------------------------
you can run it with the variables changed in the init by writing

run:: pseudonym[variable_1=1, variable2=2]

this will change those variables before the batch file is executed

---------------------------------------------------------------------------------

you can also write

help:: pseudonym

which will open the readme file in the batch files directory

or

help:: saved

to get a reminder on what Batch Files You have saved.

--------------------------------------------------------------------------------