import bpy
import sys

# Panel definitions
class CAMButtonsPanel:
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    # COMPAT_ENGINES must be defined in each subclass, external engines can add themselves here

    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        return rd.engine in cls.COMPAT_ENGINES

    def __init__(self):
        self.scene = bpy.context.scene


    def active_operation_index(self):
        return(self.scene.cam_active_operation)

    def active_operation(self):
        active_op = None
        try:
            active_op = self.scene.cam_operations[self.active_operation_index()]
        except IndexError:
            print(f"Invalid operation index {self.active_operation_index()}")

        return(active_op)

    def operations_count(self):
        return(len(self.scene.cam_operations))

    def has_operations(self):
        return (self.operations_count() > 0)

    def opencamlib_version(self):
        try:
            import ocl
            return(ocl.version())
        except ImportError as e:
            return
