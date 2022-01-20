import bpy


def map_range(v, from_min, from_max, to_min, to_max):
    """Bringt einen Wert v von einer Skala (from_min, from_max) auf eine neue Skala (to_min, to_max)"""
    return to_min + (v - from_min) * (to_max - to_min) / (from_max - from_min)


tree = bpy.context.object

my_skinmod: bpy.types.SkinModifier = tree.modifiers.new(
    "my skin mod", type="SKIN")

my_skinmod.branch_smoothing = 0.4
my_skinmod.use_smooth_shade = True
my_skinmod.use_x_symmetry = False

my_subdiv_mod: bpy.types.SubsurfModifier = tree.modifiers.new(
    "my subdiv mod", type="SUBSURF")
my_subdiv_mod.levels = 2
my_subdiv_mod.render_levels = 2

my_mesh: bpy.types.Mesh = tree.data
my_mesh.skin_vertices[0].data[2].radius = 1, 2


for i, v in enumerate(my_mesh.vertices):
    height = v.co.z
    radius = map_range(height, -1, 8, 0.5, 0.1)
    my_mesh.skin_vertices[0].data[i].radius = radius, radius
