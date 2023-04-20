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
        rd = bpy.context.scene.render
        return rd.engine in cls.COMPAT_ENGINES

    def __init__(self):
        self.active_op = self.active_operation()


    def active_operation_index(self):
        return(bpy.context.scene.cam_active_operation)

    def active_operation(self):
        active_op = None
        try:
            active_op = bpy.context.scene.cam_operations[self.active_operation_index()]
        except IndexError:
            pass
            
        return(active_op)

    def operations_count(self):
        return(len(bpy.context.scene.cam_operations))

    def has_operations(self):
        return (self.operations_count() > 0)

    def opencamlib_version(self):
        try:
            import ocl
        except ImportError:
            try:
                import opencamlib as ocl
            except ImportError as e:
                return
        return(ocl.version())

