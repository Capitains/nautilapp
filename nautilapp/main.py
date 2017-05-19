import tkinter as Tkinter
import tkinter.constants as Tkconstants
import tkinter.filedialog as tkFileDialog
import tkinter.scrolledtext as tkscrolledtext
from tkinter import END
import threading
from capitains_nautilus.flask_ext import FlaskNautilus
from capitains_nautilus.cts.resolver import NautilusCTSResolver
from flask import Flask, request
import webbrowser
import os
import rdflib.plugins
import rdflib.plugins.memory
import re
import logging
import requests
import sys
from flask_nemo import Nemo
SPACES = re.compile(r'\s+')


class WidgetLogger(logging.Handler):
    def __init__(self, widget):
        logging.Handler.__init__(self)
        self.setLevel(logging.DEBUG)
        self.widget = widget
        self.widget.config(state=Tkconstants.DISABLED)

    def emit(self, record):
        self.widget.config(state=Tkconstants.NORMAL)
        # Append message (record) to the widget
        self.widget.insert(END, self.format(record) + '\n')
        self.widget.see(END)  # Scroll to the bottom
        self.widget.config(state=Tkconstants.DISABLED)


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class Editor(Tkinter.Frame):
    def __init__(self, root):

        Tkinter.Frame.__init__(self, root)

        # options for buttons
        self.button_opt = {"side": "top", 'padx': 5, 'pady': 5}
        self.button_opt_disabled = {k: v for k, v in self.button_opt.items()}

        # define buttons
        self.load_button = Tkinter.Button(self, text='Load directory', command=self.askdirectory)
        self.load_button.pack(**self.button_opt)
        self.load_button_conf = Tkinter.Button(self, text='Load Config', command=self.askfile)
        self.load_button_conf.pack(**self.button_opt)
        self.clear_button = Tkinter.Button(self, text='Clear directories', command=self.cleardirectories)
        self.clear_button.pack(**self.button_opt)
        self.start_button = Tkinter.Button(self, text='Run Server', command=self.runserver, state=Tkconstants.DISABLED)
        self.start_button.pack(**self.button_opt_disabled)
        self.stop_button = Tkinter.Button(self, text='Stop Server', command=self.stopserver, state=Tkconstants.DISABLED)
        self.stop_button.pack(**self.button_opt_disabled)
        self.open_server_button = Tkinter.Button(self, text='Open Server', command=self.open_server, state=Tkconstants.DISABLED)
        self.open_server_button.pack(**self.button_opt_disabled)

        self.text = tkscrolledtext.ScrolledText(self)
        self.text["width"] = 50
        self.text["height"] = 20
        self.text.pack({"side": "left"})
        self.text.state=Tkconstants.DISABLED

        self.list_dir = Tkinter.Listbox(self)
        self.list_dir["width"] = 50
        self.list_dir["height"] = 20
        self.list_dir.pack({"side": "left"})

        # defining options for opening a directory
        self.dir_opt = options = {}
        options['mustexist'] = True
        options['parent'] = root
        options['title'] = "Select a directory to load into the Nautilus API"
        self.directories = []
        self.running = False
        

    def make_app(self):
        self.app = Flask("nautilus-app")
        @self.app.route('/shutdown', methods=['GET'])
        def shutdown():
            request.environ.get('werkzeug.server.shutdown')()
            return 'Server shutting down...'

        self.logger = WidgetLogger(self.text)
        resolver = NautilusCTSResolver(resource=self.directories)
        resolver.logger.addHandler(self.logger)
        resolver.parse()
        self.nautilus = FlaskNautilus(prefix="/api", resolver=resolver, app=self.app)
        self.nemo = Nemo(base_url="", resolver=resolver, app=self.app)
        self.nautilus.logger.addHandler(self.logger)
        self.nautilus.logger.setLevel(logging.DEBUG)

    def open_server(self):
        webbrowser.open_new("http://127.0.0.1:5000/api/cts")

    def askdirectory(self):
        """ Returns a selected directoryname.
        """
        directory = tkFileDialog.askdirectory(**self.dir_opt)

        if directory is not None and isinstance(directory, str):
            self.print("{} added to the Nautilus App".format(directory))
            self.list_dir.insert(END, directory)
            self.directories.append(directory)

        self.toggle_start()

    def askfile(self):
        """ Returns a selected directoryname.
        """
        opened = tkFileDialog.askopenfile(mode="r")

        if opened is not None:
            for directory in opened.readlines():
                directory = SPACES.sub("", directory)
                if len(directory) > 0 and os.path.isdir(directory):
                    self.print("{} added to the Nautilus App".format(directory))
                    self.list_dir.insert(END, directory)
                    self.directories.append(directory)

        self.toggle_start()

    def cleardirectories(self):
        self.directories = []
        self.list_dir.insert(0, END)
        self.start_button.config(state=Tkconstants.DISABLED)

    def toggle_start(self):
        """ Show the button start depending on directories """
        if len(self.directories) > 0:
            self.start_button.config(state=Tkconstants.NORMAL)
        else:
            self.start_button.config(state=Tkconstants.DISABLED)

    def print(self, line):
        """ Print to the window
        """
        self.text.config(state=Tkconstants.NORMAL)
        self.text.insert("end", line)
        self.text.insert("end", "\n")
        self.text.config(state=Tkconstants.DISABLED)

    def runserver(self):
        """ Run the flask server
        """
        self.make_app()
        self.thread = StoppableThread(target=self.app.run, kwargs=dict(host="127.0.0.1", port=5000))
        self.thread.start()

        self.stop_button.config(state=Tkconstants.NORMAL)
        self.open_server_button.config(state=Tkconstants.NORMAL)
        self.start_button.config(state=Tkconstants.DISABLED)
        self.running = True

    def stop(self):
        #requests.get()
        thread = StoppableThread(target=requests.get, args=("http://127.0.0.1:5000/shutdown", ))
        thread.start()
        thread.stop()
        self.thread.stop()
        self.running = False

    def stopserver(self):
        """ Stop the server
        """
        # There should be a better way to do this
        self.stop()
        self.start_button.config(state=Tkconstants.NORMAL)
        self.open_server_button.config(state=Tkconstants.DISABLED)
        self.stop_button.config(state=Tkconstants.DISABLED)

    @staticmethod
    def run():
        root = Tkinter.Tk()
        editor = Editor(root)
        editor.pack()
        def destroy():
            if editor.running is True:
                editor.stop()
            sys.exit()
        root.protocol("WM_DELETE_WINDOW", destroy)
        root.mainloop()

if __name__ == '__main__':
    Editor.run()
