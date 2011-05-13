**Red-R** in a nutshell.
==========================


**Red-R** core is a framework for performing data manipulation.  Red-R uses principals of data flow programming to perform analysis tasks.  Weather or not one is actually programming is a matter of somantics.  Users will generally do things much more complicated than simple if, else, for and while statements.  Nor was Red-R designed to deploy stand alone programs.  However, some people regard configuring a computer to perform a series of tasks programming, so the terminology is up to the reader.  

The core provides an environment to connect "widgets" together and to have those widgets send data to other widgets.  The ability to connect tools that each do rather simple tasks to build new tools that do complicated tasks is very powerful.  For example; the widget Read Files reads in data from a text file and emits that data from it's output socket.  Another tool, View Data Table, can receive that data and display it.  Read Files, at it's core, simply executes a function and you can think of this as returning some value.  View Data Table could also be thought of as a function which takes a parameter, a data table, and displays it.  Other widgets may take several inputs, or emit several outputs.

A widget developers goal should be to generate a user interface that allows the user to execute the function that the developer wants.  Ideally, the function will either do something useful or "return" a value that is useful later on (or both).

How one does that is fairly simple once you understand two core concepts, widgets and signals.

Widgets
~~~~~~~

widgets are the functional module of Red-R.  Nothing much gets done without them.  A widget is technically an instance of some OWRpy derived class.  Widgets can be accessed from the canvas by clicking the widget's icon, which is displayed on the canvas.  Developers should look to OWRpy for more information on exactly how to build this class and the documentation on making Widgets but they aren't that complicated.

A simple widget has an __init__ statement which simply constructs the GUI, sets any global parameters (for example reserving R variable names if using R), and setting up the input and output signal classes (discussed later).  Widget may also have process statements.  Process statements are called when a connection is made to an input socket.  Process statements should try to do something with the data that they get, usually appending the data to a holder to work with it.  Attaching data may populate the widget with new parameters so the user can make some choices about the data, or the widget may just execute automatically.  Finally, most widgets will have a commit statement.  This is activated by clicking the commit button or perhaps by other functions processing.  The commit button should do the heavy work of the widget, typically processing the data or making a call to *R* to assign data to some variable.  If the data is to be used later, then the widget will want to send the data from an output socket using the rSend() function.

Everything else is handled by Core.

Signals
~~~~~~~~

Signals are what is transmitted between widgets.  Signals all inherit from BaseRedRVariable class in signals, a Core module.  Signals are data containers for Red-R data.  Most signals simply carry strings as their data elements, representing variable names which live in the *R* space.  Signals also contain methods for converting their data to other data types, this is important for connection permissions.

When a widget connects to another the input channel receives either None or a signal type specified in the input constructor.  Core promises you that you are getting a signal of the type specified (unless a package developer lies to us).  Signals have the ability to convert their type and return a modified signal class that matches the input signal class.

For example:  In *R* a data.frame is a special type of list.  Let's suppose there is a widget that can take a list and display the names for subsetting (like List Selector).  If we make a data.frame signal with Read Files, it would be really nice to be able to connect that with the list selection widget.  When a connection is made between Read Files and List Selector Core sees that List Selector wants an RList signal and that RDataFrame has a method for converting to an RList.  Core calls the method for conversion in RDataFrame and sends the returned RList to List Selector.