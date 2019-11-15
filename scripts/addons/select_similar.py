bl_info = {
    "name": "Select Similar extended",
    "author": "Vilem Novak",
    "version": (1, 0),
    "blender": (2, 69, 0),
    "location": "View3D > Select > Grouped",
    "description": "Adds a new Mesh Object",
    "warning": "",
    "wiki_url": "",
    "category": "Add Mesh"}

import bpy
from bpy.props import *
prec=0.001;



def precc3(v1,v2,prec):
    return v1[0]-prec<v2[0]<v1[0]+prec and v1[1]-prec<v2[1]<v1[1]+prec and v1[2]-prec<v2[2]<v1[2]+prec

condition = 'VERTEX_COLOR';

def compare(o,o1, rules):

    return 0;

def compareColor(col1,col2,threshold):
    r=col2[0]-threshold<col1[0]<col2[0]+threshold
    g=col2[1]-threshold<col1[1]<col2[1]+threshold
    b=col2[2]-threshold<col1[2]<col2[2]+threshold
    return r and g and b

def selectSimilarObject(condition,threshold):
    ao=bpy.context.active_object
    if condition =='MATERIAL_COLOR':
        if len(ao.material_slots)>0:
            m=ao.material_slots[0].material.diffuse_color

            for o in bpy.context.scene.objects:
                #print (o.material_slots)
                if len(o.material_slots)>0 and o.material_slots[0].material!=None:
                    #print (precc3(m,o.material_slots[0].material.diffuse_color,prec))
                    if precc3(m,o.material_slots[0].material.diffuse_color,prec):
                        o.select=1;

    if condition =='DIMENSIONS':
        d = ao.dimensions
        for o in bpy.context.scene.objects:
            if o.dimensions.x-prec<d.x<o.dimensions.x+prec and o.dimensions.y-prec<d.y<o.dimensions.y+prec and o.dimensions.z-prec<d.z<o.dimensions.z+prec:
                o.select=1

    if condition == 'VERTEX_COUNT':
        # select similar num of verts
        n=len(ao.data.vertices);
        for o in bpy.context.scene.objects:
            if o.type == 'MESH':
                if len(o.data.vertices)==n:# and o.material_slots[0].material == mat:
                    o.select=1

def selectSimilarMesh(condition,threshold):
    bpy.ops.object.editmode_toggle()
    print(condition,threshold)
    if condition == 'VERTEX_COLOR':
        ao=bpy.context.active_object
        m=ao.data
        if len(m.vertex_colors)>0:
            for li in range(0,len(m.loops)):
                l=m.loops[li]
                v=m.vertices[l.vertex_index]
                if v.select:
                    color = m.vertex_colors['Col'].data[li].color
                    print(color)
            for li in range(0,len(m.loops)):
                l=m.loops[li]
                v=m.vertices[l.vertex_index]

                color1 = m.vertex_colors['Col'].data[li].color
                if compareColor(color, color1, threshold):
                    v.select=True
    bpy.ops.object.editmode_toggle()


class SelectSimilarObject(bpy.types.Operator):
    """Select similar objects"""
    bl_idname = "object.select_similar_addon"
    bl_label = "Select similar objects"
    bl_options = {'REGISTER', 'UNDO'}

    condition = EnumProperty(
            name="type",
            description="type",
            items=(('DIMENSIONS','DIMENSIONS','DIMENSIONS'),
                    ('MATERIAL_COLOR','MATERIAL_COLOR','MATERIAL_COLOR'),
                    ('VERTEX_COLOR','VERTEX_COLOR','VERTEX_COLOR'),
                    ('VERTEX_COUNT','VERTEX_COUNT','VERTEX_COUNT')
            ),
            default='DIMENSIONS'
            )
    threshold = FloatProperty(
            name="Threshold",
            description="Threshold",
            min=0.000001, max=100.0,
            default=0.1,
            )

    conditions=[]
    def execute(self, context):

        selectSimilarObject(self.condition,self.threshold)

        return {'FINISHED'}

class SelectSimilarMesh(bpy.types.Operator):
    """Select similar elements"""
    bl_idname = "mesh.select_similar_addon"
    bl_label = "Select similar elements"
    bl_options = {'REGISTER', 'UNDO'}

    condition = EnumProperty(
            name="type",
            description="type",
            items=(
                    ('VERTEX_COLOR','VERTEX_COLOR','VERTEX_COLOR'),
                    ('VERTEX_COUNT','VERTEX_COUNT','VERTEX_COUNT')
            ),
            default='VERTEX_COLOR'
            )
    threshold = FloatProperty(
            name="Threshold",
            description="Threshold",
            min=0.000001, max=100.0,
            default=0.1,
            )

    conditions=[]
    #view_align = BoolProperty(
    #        name="Align to View",
    #        default=False,
    #        )
    # generic transform props



    def execute(self, context):

        selectSimilarMesh(self.condition,self.threshold)

        return {'FINISHED'}

def register():
    bpy.utils.register_class(SelectSimilarObject)
    bpy.utils.register_class(SelectSimilarMesh)
    #bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(SelectSimilarObject)
    bpy.utils.unregister_class(SelectSimilarMesh)
    #bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()

    # test call
    #bpy.ops.mesh.primitive_box_add()
