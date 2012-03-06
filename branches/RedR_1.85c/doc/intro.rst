Welcome to **Red-R**'s Core documentation!
===========================================

**Red-R** is a programming framework built on *Python* and *R* to perform statistical programming, data visualization, and analysis.  In general, the idea behind **Red-R** is that if you can see how data is processed in an analysis pipeline then you will be better able to interact with that data.  There are many other benificial consequences of data flow analysis of this kind.  The analysis is self documenting, you can see how the analysis is done at a global level, analyses performed by others are easily understood by new users, etc.

This is the page for the **Red-R** Core documentation.  If you are a regular user the content in this section may be more advanced then you would normally want to see.  You can go back to the main **Red-R** page by clicking any of the icons on the navigation bar above.

If you are looking to extend the core of **Red-R** or simply to make your own packages then this is the place to get all of the information on the *Core*.  Developers looking to get started should see the "Red-R in a nutshell" entry below for a very brief description of what **Red-R** is and some of the common terminology.  Next, there is the "Widgets and Signals Primer; how data is processed." which will describe more in depth the things that are basic to most packages; widgets and signals.  All of this is then summed up in the documents "How to make a widget" and "How to make a signal".

.. toctree::
   :glob:
   :maxdepth: 2
    
   devel/nutshell
   devel/widgetsignals
   devel/makeWidget
   devel/makeSignal