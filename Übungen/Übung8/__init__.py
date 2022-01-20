import bpy

bl_info = {
    "name": "My Addon Name",
    "description": "Description of this addon",
    "author": "Authors name",
    "version": (0, 0, 1),
    "blender": (2, 9, 0),
    "location": "View3D",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Object"}


class OT_geometryNodes(bpy.types.Operator):
    bl_info = "geometry_nodes_addon.first_op"
    bl_label = "My GN Operator"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        ob = bpy.context.object
        gm_mod: bpy.types.NodesModifier = ob.modifiers.new(
            "My GM Mod", "NODES")
        node_cube: bpy.types.GeometryNodemeshCube = gm_mod.node_group.nodes.new(
            "GeometryNode")
        return {"FINISHED"}

    def register():
        ...

    def unregister():
        ...
