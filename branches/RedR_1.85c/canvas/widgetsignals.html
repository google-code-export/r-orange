Widgets and Signals Primer; how data is processed.
=========================================================

In the introduction we briefly discussed Widgets and Signals.  Now we further discuss these and how they are used.  Before we begin with that though, let's have a brief discussion of what data we are processing anyway.

Python data lives in Python.  Python data can be sent in a Signal with no problem and extracted by widgets.  All of this can happen with no dependence on R.  In fact, if one wanted to make Red-R widgets and signals that know nothing of R that would be fine.  However, Red-R is largely built around R.  It's not that Python isn't a good enough language, it's simply that R has lot's of packages that do very specific functions that users would like to do.  So how do we interact with R?

Interaction with R uses a module named :mod: `RSession`.  The key functions in RSession send strings to R which are evaluated and returned to Python.  Red-R keeps as much R data in R as possible.  To do this we generate strings that can be appended to a function for assignmen and pass the strings around in the Python world.  For example:  Say we want to assign a variable to the R call `c(1,2,3)`.  In R such a thing would look like `variable<-c(1,2,3)`.  In Red-R we do exactly the same thing but in a bit more complicated way.  First a widget will make a unique string (a constant name followed by an identifier and a time stamp, which looks like variable_1_12342315123.87).  So not to confuse the developer later, this string is generated automatically and placed in a Python dict named Rvariables with the key `variable`.  So to make the call to R in Python we use the code `'%s<-c(1,2,3)' % self.Rvariables['variable']` (note that these functions generally happen in widgets so self the widget class).

To make the signal, we simply set the self.Rvariables['variabel'] string as the data element.  For simplicity, when we use terminology like "This widget sends a data.frame." we mean that this widget generates a signal that holds a string which represents an object of the data.frame class in R.  Since it's always assumed that R data is represented as a string in Python, it's more convinient to think of sending the data instead of a string.  Interestingly, one can send entire R functions as a signal, for example the PlotAttribute signal takes instructions to add data to a plot which are executed by the plotting widget at plot time.  To the great confusion of seasoned R users, we actually are generating the plot atribute command (as a string), such as points(a, b) before we even begin the plot function.

Setting up sockets
~~~~~~~~~~~~~~~~~~~~~~~~

Widgets declare input and output sockets by adding inputs or outputs to their input and output signal managers.  This is done using the syntax `self.inputs.addInput('<id>', '<name>', [<signalClass>, ...], <processFunction>[, multiple = <bool>])` where id is an internal widget id (this should never change or loading and saving will break!!), name is the string that will appear to the user when connecting widgets, signalClass is a signal class that this widget will accept, these can be set as a list of signal classes, processFunction is the function that will be executed when data is attached or removed from the signal class, and multiple is an optional parameter that allows the widget to accept more than one signal in the same slot.

With an input signal declared the widget will have an input socket to which data can be attached.  When data is attached the function (processFunction) will be executed with the signal class as the first argument.  If multiple is True then the sending widget ID (a string) will be sent as the second argument.  

The same is done for outputs except that outputs only send one signal class per output socket and there are no multiple signals sent from output sockets.

Processing input data
~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the previous section we discussed the processFunction.  What will be done with a signal when it is received is largely dependent on what the user want to do.  Signals have functions themselves, may contain optional or accessory data, or may require further processing.  Most widget though will simply need to extract the data element by calling `getData()` on the signal.  `getData()` will return the data element of a signal, which as discussed above, is usually a string.

Most widgets will want to set the GUI of the widget based on the data received.  For example, we may need to set the elements of a combo box to the names of columns in a data frame.  An example of a processFunction that does this is shown below;

    def processFunction(self, data):
        if data:  # we need to see if we got data, remember that we could get None also 
            self.myData = data.getData()
            names = self.R('names(%s)' % self.myData, wantType = redR.CONVERT) # this is a call to R which is discussed in more detail in other sections, just believe us when we say that this will return a Python list of names of the variable specified in self.myData.
            self.myCombo.update(names) # in the example myCombo is a :mod: `comboBox` of the GUI, update is a function of that class.
            self.commitFunction()  ## in this case we run the commitFunction as soon as data is connected, you may not want to do this in your own widget.  The commitFunction will be discussed in the next section.
        else:
            self.myData = ''
            
Commit Function
~~~~~~~~~~~~~~~~~~~~

Above the processFunction executes the commitFunction in the execution of the connect signal.  This widget is of the "Process on Connect" type.  That is, the widget will run when data is connected.  Widgets like this are quite useful in Red-R as they allow users to join multiple widgets together in a way that when new data is put in the leading widget, all of the downstream widgets will execute with no user input.

Commit functions will generally format a string command (or many string commands) to be executed in R, execute those functions, assign the results to new variables, and send the variables as output signals.  

You will note that above we set self.myData to '' if there is no data in the signal.  Developers will typically check if required data elements are empty and return if so; if self.data == '': <let the user know that you can't process> return.

Formatting the executed string may require getting data from the GUI.  These things are covered in more depth in other sections.  At the end there is usually a call to R using self.R().  

If the widget has an output, the widget should set a new signal by constructing a signal of the output class specified in the output specification described above: newData = <signalClass>(self, data = self.Rvariables['newData'], ...).  This is sent using the self.rSend() function: self.rSend(<id>, newData).

Summary
~~~~~~~~~~

Herein, we have described a bare bones widget.  Functional widgets will be much more complicated than this, typically requiring several parameters to be set by the user in the GUI.  However, this serves to lay out the general schema of how data is passed between widgets.  The next sections will discuss widget and signal class development in more detail.