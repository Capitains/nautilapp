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
import re
SPACES = re.compile(r'\s+')


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

        self.list_dir = Tkinter.Listbox(self)
        self.list_dir["width"] = 50
        self.list_dir["height"] = 20
        self.list_dir.pack({"side": "left"})

        # defining options for opening a directory
        self.dir_opt = options = {}
        options['mustexist'] = True
        options['parent'] = root
        options['title'] = "Select a directory to load into the Nautilus API"

        self.app = Flask("nautilus-app")

        @self.app.route('/shutdown', methods=['GET'])
        def shutdown():
            request.environ.get('werkzeug.server.shutdown')()
            return 'Server shutting down...'
        self.directories = []

    def open_server(self):
        webbrowser.open_new("http://127.0.0.1:5000/cts")

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
        self.text.insert("end", line)
        self.text.insert("end", "\n")

    def runserver(self):
        """ Run the flask server
        """
        resolver = NautilusCTSResolver(resource=self.directories)
        resolver.parse()
        self.nautilus = FlaskNautilus(resolver=resolver, app=self.app)
        self.thread = StoppableThread(target=self.app.run, kwargs=dict(host="127.0.0.1", port=5000))
        self.thread.start()

        self.stop_button.config(state=Tkconstants.NORMAL)
        self.open_server_button.config(state=Tkconstants.NORMAL)
        self.start_button.config(state=Tkconstants.DISABLED)

    def stopserver(self):
        """ Stop the server
        """
        # There should be a better way to do this
        webbrowser.open_new("http://127.0.0.1:5000/shutdown")
        self.thread.stop()
        self.start_button.config(state=Tkconstants.NORMAL)
        self.open_server_button.config(state=Tkconstants.DISABLED)
        self.stop_button.config(state=Tkconstants.DISABLED)

    @staticmethod
    def run():
        root = Tkinter.Tk()
        Editor(root).pack()
        root.mainloop()

if __name__ == '__main__':
    Editor.run()
