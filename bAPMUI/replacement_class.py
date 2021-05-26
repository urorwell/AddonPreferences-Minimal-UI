import bpy
from bpy.types import Panel

class AddOnPanel:
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_context = "addons"


class USERPREF_PT_addons(AddOnPanel, Panel):
    bl_label = "Add-ons"
    bl_options = {'HIDE_HEADER'}

    @staticmethod
    def is_user_addon(mod, user_addon_paths):
        import os

        if not user_addon_paths:
            for path in (
                    bpy.utils.script_path_user(),
                    bpy.utils.script_path_pref(),
            ):
                if path is not None:
                    user_addon_paths.append(os.path.join(path, "addons"))

        for path in user_addon_paths:
            if bpy.path.is_subdir(mod.__file__, path):
                return True
        return False


    @staticmethod
    def draw_error(layout, message):
        lines = message.split("\n")
        box = layout.box()
        sub = box.row()
        sub.label(text=lines[0])
        sub.label(icon='ERROR')
        for l in lines[1:]:
            box.label(text=l)


    def draw(self, context):
        import os
        import addon_utils

        layout = self.layout

        wm = context.window_manager
        prefs = context.preferences
        used_ext = {ext.module for ext in prefs.addons}

        addon_user_dirs = tuple(
            p for p in (
                os.path.join(prefs.filepaths.script_directory, "addons"),
                bpy.utils.user_resource('SCRIPTS', "addons"),
            )
            if p
        )

        # collect the categories that can be filtered on
        addons = [
            (mod, addon_utils.module_bl_info(mod))
            for mod in addon_utils.modules(refresh=False)
        ]

        split = layout.split(factor=0.6)

        row = split.row()
        row.prop(wm, "addon_support", expand=True)

        row = split.row(align=True)
        row.operator("preferences.addon_install", icon='IMPORT', text="Install...")
        row.operator("preferences.addon_refresh", icon='FILE_REFRESH', text="Refresh")

        row = layout.row()
        row.prop(prefs.view, "show_addons_enabled_only")
        row.prop(wm, "addon_filter", text="")
        row.prop(wm, "addon_search", text="", icon='VIEWZOOM')

        col = layout.column()

        # set in addon_utils.modules_refresh()
        if addon_utils.error_duplicates:
            box = col.box()
            row = box.row()
            row.label(text="Multiple add-ons with the same name found!")
            row.label(icon='ERROR')
            box.label(text="Delete one of each pair to resolve:")
            for (addon_name, addon_file, addon_path) in addon_utils.error_duplicates:
                box.separator()
                sub_col = box.column(align=True)
                sub_col.label(text=addon_name + ":")
                sub_col.label(text="    " + addon_file)
                sub_col.label(text="    " + addon_path)

        if addon_utils.error_encoding:
            self.draw_error(
                col,
                "One or more addons do not have UTF-8 encoding\n"
                "(see console for details)",
            )

        show_enabled_only = prefs.view.show_addons_enabled_only
        filter = wm.addon_filter
        search = wm.addon_search.lower()
        support = wm.addon_support

        # initialized on demand
        user_addon_paths = []

        for mod, info in addons:
            module_name = mod.__name__
            is_enabled = module_name in used_ext

            if info["support"] not in support:
                continue

            # check if addon should be visible with current filters
            is_visible = (
                (filter == "All") or
                (filter == info["category"]) or
                (filter == "User" and (mod.__file__.startswith(addon_user_dirs)))
            )
            if show_enabled_only:
                is_visible = is_visible and is_enabled

            if is_visible:
                if search and not (
                        (search in info["name"].lower()) or
                        (info["author"] and (search in info["author"].lower())) or
                        ((filter == "All") and (search in info["category"].lower()))
                ):
                    continue

                # Addon UI Code
                col_box = col.column()
                box = col_box.box()
                colsub = box.column()
                row = colsub.row(align=True)

                if is_enabled:
                    addon_preferences = prefs.addons[module_name].preferences
                    if addon_preferences is not None:
                        row.operator(
                            "preferences.addon_expand",
                            icon='DISCLOSURE_TRI_DOWN' if info["show_expanded"] else 'DISCLOSURE_TRI_RIGHT',
                            emboss=False,
                        ).module = module_name

                row.operator(
                    "preferences.addon_disable" if is_enabled else "preferences.addon_enable",
                    icon='CHECKBOX_HLT' if is_enabled else 'CHECKBOX_DEHLT', text="",
                    emboss=False,
                ).module = module_name

                sub = row.row()
                sub.active = is_enabled
                sub.label(text=info["name"])

                if info["warning"]:
                    sub.operator("preferences.addon_warning", icon='ERROR', icon_value=0).warning = info["warning"]

                sub.operator("preferences.addon_info", icon='INFO', icon_value=0).module = module_name

                # Expanded UI - AddonPreferences (only if additional info is available)
                if info["show_expanded"]:
                    user_addon = USERPREF_PT_addons.is_user_addon(mod, user_addon_paths)
                    tot_row = bool(info["doc_url"]) + bool(user_addon)

                    if is_enabled:
                        addon_preferences = prefs.addons[module_name].preferences
                        if addon_preferences is not None:
                            draw = getattr(addon_preferences, "draw", None)
                            if draw is not None:
                                addon_preferences_class = type(addon_preferences)
                                box_prefs = box.box()
                                addon_preferences_class.layout = box_prefs
                                try:
                                    draw(context)
                                except:
                                    import traceback
                                    traceback.print_exc()
                                    box_prefs.label(text="Error (see console)", icon='ERROR')
                                del addon_preferences_class.layout


        # Append missing scripts
        # First collect scripts that are used but have no script file.
        module_names = {mod.__name__ for mod, info in addons}
        missing_modules = {ext for ext in used_ext if ext not in module_names}

        if missing_modules and filter in {"All", "Enabled"}:
            col.column().separator()
            col.column().label(text="Missing script files")

            module_names = {mod.__name__ for mod, info in addons}
            for module_name in sorted(missing_modules):
                is_enabled = module_name in used_ext
                # Addon UI Code
                box = col.column().box()
                colsub = box.column()
                row = colsub.row(align=True)

                row.label(text="", icon='ERROR')

                if is_enabled:
                    row.operator(
                        "preferences.addon_disable", icon='CHECKBOX_HLT', text="", emboss=False,
                    ).module = module_name

                row.label(text=module_name, translate=False)
