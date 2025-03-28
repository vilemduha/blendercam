import bpy
from bpy.types import Operator
from bpy.props import StringProperty


class CAM_Popup_Panel(Operator):
    bl_idname = "cam.popup"
    bl_label = ""

    text: StringProperty(name="text", default="")

    def execute(self, context):
        print(self.text)
        return {"FINISHED"}

    def invoke(self, context, event):
        window = context.window
        wm = context.window_manager

        width = window.width
        height = window.height
        popup_width = 300
        v_offset = 100

        x = int(width / 2 + popup_width / 2)
        y = int(height / 2 + v_offset)
        context.window.cursor_warp(x, y)

        return wm.invoke_props_dialog(self, width=popup_width, title="Fabex CNC")

    def draw(self, context):
        layout = self.layout

        if not self.text == "":
            layout.label(text=self.text, icon="INFO")

        operations = context.scene.cam_operations
        operations_count = len(operations)
        operation_index = context.scene.cam_active_operation
        self.op = operations[operation_index] if operations_count > 0 else None

        if self.op is None:
            return
        else:
            if not self.op.info.warnings == "":
                # Operation Warnings
                box = layout.box()
                col = box.column(align=True)
                col.alert = True
                col.label(text="!!! WARNING !!!", icon="ERROR")
                for line in self.op.info.warnings.rstrip("\n").split("\n"):
                    if len(line) > 0:
                        icon = "BLANK1"
                        if line.startswith(("Bounds", "Path", "Operation", "X", "Y", "Z")):
                            icon = "MOD_WIREFRAME"
                        if line.startswith(("Memory", "Detail")):
                            icon = "MEMORY"
                        if line.startswith(("!!!")):
                            icon = "ERROR"
                        col.label(text=line, icon=icon)
