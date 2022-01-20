# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
import bmesh
import random
import math
import mathutils

bl_info = {
    "name": "OperatorenAddon",
    "author": "Calvin",
    "description": "",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Generic"
}


def map_range(v, from_min, from_max, to_min, to_max):
    """Bringt einen Wert v von einer Skala (from_min, from_max) auf eine neue Skala (to_min, to_max)"""
    return to_min + (v - from_min) * (to_max - to_min) / (from_max - from_min)


class OT_Mesh_Grassshrub(bpy.types.Operator):
    bl_idname = "mesh.grass_generator"
    bl_label = "Generate Grass"
    bl_description = "Description that shows in blender tooltips"
    bl_options = {"REGISTER", "UNDO"}

    HEIGHT_MIN: bpy.props.IntProperty(
        name="Min height", min=1, max=30, default=10)
    HEIGHT_MAX: bpy.props.IntProperty(
        name="Max height", min=1, max=30, default=10)

    TIP_WIDTH_MIN: bpy.props.FloatProperty(
        name="Tip Min Width", min=0.01, max=0.2, default=0.1)
    TIP_WIDTH_MAX: bpy.props.FloatProperty(
        name="Tip Max Width", min=0.01, max=0.2, default=0.1)

    BASE_WIDTH_MIN: bpy.props.FloatProperty(
        name="Base Min Width", min=0.01, max=1, default=0.5)
    BASE_WIDTH_MAX: bpy.props.FloatProperty(
        name="Base Max Width", min=0.01, max=1, default=0.5)

    BASE_ROT_MIN: bpy.props.FloatProperty(
        name="Base Min Width", min=0.01, max=1, default=0.5)
    BASE_ROT_MAX: bpy.props.FloatProperty(
        name="Base Max Width", min=0.01, max=1, default=0.5)

    TIP_ROT_MIN: bpy.props.IntProperty(
        name="Tip Rot Min", min=1, max=60, default=40)
    TIP_ROT_MAX: bpy.props.IntProperty(
        name="Tip Rot Max", min=60, max=90, default=60)

    ROT_FALLOFF: bpy.props.FloatProperty(
        name="Rotation Falloff", min=0.2, max=10, default=1)

    NUM_BLADS: bpy.props.FloatProperty(
        name="Blades", min=1, max=64, default=10)

    grassheight: bpy.props.IntProperty(name="height", default=5, min=1, max=20)

    @staticmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        grass_mesh = bpy.data.meshes.new("grass mesh")
        grass_object = bpy.data.objects.new("grass object", grass_mesh)
        bpy.context.collection.objects.link(grass_object)

        bm = bmesh.new()
        bm.from_mesh(grass_mesh)

        height = random.randint(self.HEIGHT_MIN, self.HEIGHT_MAX)
        tip_width = random.uniform(self.TIP_WIDTH_MIN, self.TIP_WIDTH_MAX)
        base_width = random.uniform(self.BASE_WIDTH_MIN, self.BASE_WIDTH_MAX)

        last_vert_1 = None
        last_vert_2 = None

        rot_base = random.randint(self.BASE_ROT_MIN, self.BASE_ROT_MAX)
        rot_tip = random.randint(self.TIP_ROT_MIN, self.TIP_ROT_MAX)

        c_blade = []

        for i in range(height):
            progress = i / height
            pos_x = map_range(i, 0, height, base_width, tip_width)
            vert_1 = bm.verts.new((-pos_x, 0, i))
            vert_2 = bm.verts.new((pos_x, 0, i))

            rot_angle = map_range(
                math.pow(progress, self.ROT_FALLOFF), 0, 1, rot_base, rot_tip)

            rot_matrix = mathutils.Matrix.Rotation(
                math.radians(rot_angle), 4, "X")
            bmesh.ops.rotate(bm, cent=(0, 0, 0),
                             matrix=rot_matrix, verts=[vert_1, vert_2])

            if i is not 0:
                bm.faces.new((last_vert_1, last_vert_2, vert_2, vert_1))

            last_vert_1 = vert_1
            last_vert_2 = vert_2

            c_blade.append(vert_1)
            c_blade.append(vert_2)

        random_blade_angle = random.uniform(0, 360)
        rot_matrix_blade = mathutils.Matrix.Rotation(
            math.radians(random_blade_angle), 4, "2")

        bmesh.ops.rotate(bm, cent=(0, 0, 0),
                         matrix=rot_matrix_blade, verts=[vert_1, vert_2])
        bm.to_mesh(grass_mesh)
        bm.free()

        return {"FINISHED"}


register, unregister = bpy.utils.register_classes_factory({OT_Mesh_Grassshrub})

if __name__ == "__main__":
    register()
