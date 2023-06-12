import bpy

# Panel definitions
class CAMButtonsPanel:
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    # COMPAT_ENGINES must be defined in each subclass, external engines can add themselves here

    @classmethod
    def poll(cls, context):
        rd = bpy.context.scene.render
        if rd.engine in cls.COMPAT_ENGINES:
            if hasattr(cls,'always_show_panel') and cls.always_show_panel:
                return True
            op = cls.active_operation()
            if op and op.valid:
                return True
        return False

    @classmethod
    def active_operation_index(cls):
        return(bpy.context.scene.cam_active_operation)

    @classmethod
    def active_operation(cls):
        active_op = None
        try:
            active_op = bpy.context.scene.cam_operations[cls.active_operation_index()]
        except IndexError:
            pass
        return(active_op)

    def __init__(self):
        self.op = self.active_operation()

    def operations_count(self):
        return(len(bpy.context.scene.cam_operations))

    def has_operations(self):
        return (self.operations_count() > 0)

