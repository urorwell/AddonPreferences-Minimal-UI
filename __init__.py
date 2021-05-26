bl_info = {
    "name" : "Addon Prefences - Minimal - UI",
    "author" : "Noyogi",
    "version" : (1,0),
    "blender" : (2,92,0),
    "location" : "Preferences > Addons",
    "description": "Simplifies Addon Panel",
    "warning" : "Only tested on 2.92, on Ubuntu 20.04",
    "doc_url" : "",
    "category" : "Interface",
}


# import os, sys # for using another py script
from . import bAPMUI

def register():
    bAPMUI.register()

def unregister():
    bAPMUI.unregister()

if __name__ == "__main__":
    register()
