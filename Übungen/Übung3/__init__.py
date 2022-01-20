bl_info = {
    "name": "Cube Tower Generator",
    "author": "Ich <ich@webmail.hs-furtwangen.de>",
    "version": (1, 0),
    "blender": (2, 91, 2),
    "location": "Search menu",
    "description": "Adds a Tower of random Cubes",
    "warning": "",
    "doc_url": "",
    "category": "Add Mesh",
}



import bpy
import random


class OT_MESH_CUBETOWER(bpy.types.Operator):
    """Generate a Cube Tower"""
    
    bl_idname = "object.add_cubetower"
    bl_label = "Add Cube Tower"
    bl_options = {"REGISTER", "UNDO"}
    
    
    num = bpy.props.IntProperty(
            name = "Cube Number",
            description = "Defines the number of cubes",
            default = 5)


    cube_size_min = bpy.props.FloatProperty(
        name = "Min Cube Size",
        default = 0.5)
        
        
    cube_size_max = bpy.props.FloatProperty(
        name = "Max Cube Size",
        default = 2.0)
        
    
    my_vec = bpy.props.FloatVectorProperty(
        name = "Color Vector",
        default = (1,1,1),
        subtype = "COLOR")
    
    @classmethod
    def poll(cls, context):
        return bpy.context.mode == "OBJECT"
   
   
    
    def execute(self, context):
        
        
        
        
        total_height = 0
        rand_offset = 0.4
        
        bpy.ops.mesh.primitive_plane_add(size = 30)

        for i in range(self.num):
            
            c_cube_size = random.uniform(self.cube_size_min, self.cube_size_max)
            bpy.ops.mesh.primitive_cube_add(location = (0,0,total_height + c_cube_size/2), size = c_cube_size)
            
            bpy.ops.rigidbody.object_add()
            
            total_height += c_cube_size
            
        return {"FINISHED"}
   
 
def menu_func(self, context):
        self.layout.operator(OT_MESH_CUBETOWER.bl_idname, icon="SELECT_EXTEND")
     
    
    
def unregister():
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)
    bpy.utils.unregister_class(OT_MESH_CUBETOWER)
    
    
              
def register():
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)
    bpy.utils.register_class(OT_MESH_CUBETOWER)
   

if __name__ == "__main__":
    register()