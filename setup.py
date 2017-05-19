from distutils.core import setup
import py2exe

setup(
    windows=[
        {
            "script": "nautilapp/__main__.py"
        }
    ],
    options={
        "py2exe": {
            "includes":
                [
                    "tkinter", "os", "lxml"
                ],
            'bundle_files': 1,
            'compressed': False
        }
    },
    zipfile=None
)
