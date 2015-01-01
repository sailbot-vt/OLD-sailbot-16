#SailBOT

##Introduction

**What is SailBOT**
SailBOT is a competition to build and program an autonomous sailing robot capable of navigating obstacles in a dynamic, real-world sailing environment. The robot uses on-board sensor input to effectively sail towards marked latitude and longitude coordinate locations and avoid obstacles.

**Project Coding Goals**
The goal of the project is to build upon the SailBOT foundation laid in previous years. It should be extensible, modular, verbose, and minimalistic.

##How to contribute
All members of the SailBOT coding team have full read and write access to the group's internal repositories.

We use [GitHub](https://github.com/), a collaborative coding tool, to version the code.

Now, if you know what you're doing, you can skip most of the steps below. Just clone the repository and get to work. Otherwise, you can keep reading to get set up.

**Download the GitHub GUI**
Download and install the GUI client appropriate for your system: [Windows](https://windows.github.com/) or [Mac](https://mac.github.com/).

**Request access to the repository**
Make sure you have created a GitHub account. Email one of the SailBOT leads with your GitHub username and we will add you.

**Clone**
Code is stored in the GitHub repository. It is synced with the code stored locally on your computer. When you make a change you create a *commit*. This commit is *pushed* to the GitHub server and the repository updates. Other collaborators will *pull* your commit down and their local versions will also updates.

The GUI version of the program makes this process super simple. Once you are added to the repository, click <kbd>+</kbd> to add a new repository then click the <kbd>clone</kbd> tab. Select the SailBOT repository. Clone the repository wherever you would like.
>Note: if you want to use an IDE to code in (highly reccomended), clone the project in your IDE's root folder. Then, <kbd>file</kbd> > <kbd>import</kbd> the project into the IDE. I don't recommend cloning the repository through the IDE itself.

##How it works

###Starting and setting the configuration parameters

**Configuration file**

The starting point for SailBOT code is `main.py` located in the `src` folder. When the program starts, it first checks the configuration file `config.ini` to set variables. This config file is used to circumvent the need to edit the code itself. Instead, if a runtime parameter needs to be changed, it is done through simply editing the configuration file.

A sample configuration file looks like this:

    [DEFAULT]
    debug: True
    port: 8888
    log_name: sailbot.log

`debug`: if `True`, the program will log to the console, to the log file, and to the web client. If the value is `False`, nothing will be logged to any location.
`port`: specifies the port number that the web server will run on.
`log_name`: specifies the name of the log file, created in the root of the `src` folder.

**Loading locations**

The code will then try to load locations from `locations.json` in the root `src` folder. This is written as JSON in accordance to the `Location` module.

A default `locations.json` should look like this:

    [  
       {  
          "latitude":37.216769,
          "longitude":-80.005349
       },
       {  
          "latitude":37.217452,
          "longitude":-80.003410
       },
       {  
          "latitude":37.217490,
          "longitude":-79.999750
       }
    ]

###Threading processes

After the setup sequence has completed successfully, various threads are started to conduct processes in SailBOT. This is the area which needs more development. The threads at present include:

`DataThread(name="Data")`: pushes data out to the server thread; controls the web client.
`MotorThread(name="Motor")`: controls the motors; contains motor movement functions.
`LogicThread(name="Logic")`: makes determinations about the path SailBOT should take during normal operation.

**Why use threads?**

 - If a thread crashes, it doesn't bring down the entire program if handled correctly
 - Better for error handling and memory management
 - More conducive to OOP
 - It is easier to problem solve using threads
 - Threads are easy to spawn in Python
 - Code blocks can infinitely loop in parallel without callbacks or hangs from another process

**Code framework for a Thread**

    import threading
    
    class SomeThread(threading.Thread):
        """ Description of the thread
        """
        
        def run(self):
            self.some_method()
    
  
Then, the thread can be created:

    some_thread = SomeThread(name="A Thread")
    # run() method will be called in the thread class
    some_thread.start() 

