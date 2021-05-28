import bpy
import os
from inspect import getfile

from bpy.types import AddonPreferences, Operator
from bpy.props import StringProperty
from bl_ui.space_userpref import USERPREF_PT_addons as originalClass

from . import replacement_class


class BAPMUI_AP_main(AddonPreferences):
    bl_idname = __package__

    lastClass: StringProperty()
    classDict = {
            "": originalClass,
            "space_userpref.py": originalClass,
            "replacement_class.py": replacement_class.USERPREF_PT_addons
            }

    def draw(self, context):
        layout = self.layout
        row = layout.row()

        if self.lastClass == "space_userpref.py" or self.lastClass == "":
            row.operator(
                        "bapmui.change_class",
                        text="Minimal Addon View").classOpt = "replacement_class.py"
        else:
            row.operator(
                        "bapmui.change_class",
                        text="Original Addon View").classOpt = "space_userpref.py"


class BAPMUI_OT_change_class(Operator):
    """Switch 'USERPREF_PT_addons' Class"""
    bl_idname = "bapmui.change_class"
    bl_label = ""

    classOpt: StringProperty()

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences

        currentClass = os.path.basename(getfile(bpy.types.USERPREF_PT_addons))

        if currentClass != self.classOpt:
            bpy.utils.unregister_class(bpy.types.USERPREF_PT_addons)
            bpy.utils.register_class(addon_prefs.classDict[self.classOpt])

            addon_prefs.lastClass = self.classOpt

        return {'FINISHED'}


class PREFERENCES_OT_addon_warning(Operator):
    """Addon Warning - For now click to view warning about this addon"""
    bl_idname = "preferences.addon_warning"
    bl_label = ""

    warning: StringProperty()

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Warning:")
        row = layout.row()
        row.label(text=self.warning)


class PREFERENCES_OT_addon_info(Operator):
    """- Addon Info -"""
    bl_idname = "preferences.addon_info"
    bl_label = ""

    module: StringProperty()

    @staticmethod
    def getMod(module_name):
        import addon_utils

        for mod in addon_utils.modules():
            if mod.__name__ == module_name:
                return mod

    @staticmethod
    def getInfo(mod):
        import addon_utils
        info = addon_utils.module_bl_info(mod)
        return info

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=425)

    def draw(self, context):
        layout = self.layout

        mod = self.getMod(self.module)
        info = self.getInfo(mod)

        col = layout.column()
        if info["name"]:
            split = col.row().split(factor=0.18)
            split.label(text="Name:")
            split.label(text=info["name"])
        if info["description"]:
            split = col.row().split(factor=0.18)
            split.label(text="Description:")
            split.label(text=info["description"])
        if info["author"]:
            split = col.row().split(factor=0.18)
            split.label(text="Author:")
            split.label(text=info["author"], translate=False)
        if info["version"]:
            split = col.row().split(factor=0.18)
            split.label(text="Version:")
            split.label(
                        text=".".join(str(x) for x in info["version"]),
                        translate=False
                        )
        if info["blender"]:
            split = col.row().split(factor=0.18)
            split.label(text="Blender:")
            split.label(
                        text=".".join(str(x) for x in info["blender"]),
                        translate=False
                        )
        if info["location"]:
            split = col.row().split(factor=0.18)
            split.label(text="Location:")
            split.label(text=info["location"])
        if mod:
            split = col.row().split(factor=0.18)
            split.label(text="File:")
            split.label(text=mod.__file__, translate=False)
        if info["category"]:
            split = col.row().split(factor=0.18)
            split.label(text="Category:")
            split.label(text=info["category"])
        if info["support"]:
            split = col.row().split(factor=0.18)
            split.label(text="Support:")
            split.label(text=info["support"])
        if info["warning"]:
            split = col.row().split(factor=0.18)
            split.label(text="Warning:")
            split.label(text=info["warning"])
        split = col.row()
        if info["doc_url"]:
            split.operator(
                        "wm.url_open", text="Documentation", icon='HELP',
                        ).url = info["doc_url"]
        if info.get("tracker_url"):
            split.operator(
                        "wm.url_open", text="Report a Bug", icon='URL',
                        ).url = info["tracker_url"]
        split.operator(
                    "preferences.addon_remove", text="Remove", icon='CANCEL',
                    ).module = mod.__name__


def updateClass(self, context):
    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences

    currentClass = os.path.basename(getfile(bpy.types.USERPREF_PT_addons))
    classOpt = addon_prefs.lastClass

    if currentClass != classOpt:

        bpy.utils.unregister_class(bpy.types.USERPREF_PT_addons)
        bpy.utils.register_class(addon_prefs.classDict[classOpt])

    return


classes = [
    BAPMUI_AP_main,
    BAPMUI_OT_change_class,
    PREFERENCES_OT_addon_info,
    PREFERENCES_OT_addon_warning
    ]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    updateClass(None, bpy.context)


def unregister():
    bpy.utils.unregister_class(bpy.types.USERPREF_PT_addons)
    bpy.utils.register_class(originalClass)
    for cls in classes:
        bpy.utils.unregister_class(cls)
