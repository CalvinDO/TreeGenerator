from bmesh.types import BMVert, BMesh
import bpy
import bmesh
import math
import mathutils

mesh = bpy.context.object.data

treeMesh: BMesh = bmesh.from_edit_mesh(mesh)

print(" ------- ")

branchAmount: int = 0

lengthFactor: float = 1.6180339
angle: float = 137.5077 / 2
for v in treeMesh.verts:

    if branchAmount > 1000:
        break

    if (len(v.link_edges) == 1) and v.co.z > 0.1:

        innerVert, outerVert = v.link_edges[0].verts
        if innerVert == v:
            innerVert = outerVert
            outerVert = v

        edgeVector: mathutils.Vector = outerVert.co - innerVert.co
        edgeVector /= lengthFactor

        leftVector: mathutils.Vector = edgeVector.copy()
        rightVector: mathutils.Vector = edgeVector.copy()

        leftVert = bmesh.ops.extrude_vert_indiv(
            treeMesh, verts=[outerVert])['verts'][0]
        rightVert = bmesh.ops.extrude_vert_indiv(
            treeMesh, verts=[outerVert])['verts'][0]

        leftVector.rotate(mathutils.Euler(
            (0.0, math.radians(angle), 0.0), 'XYZ'))
        rightVector.rotate(mathutils.Euler(
            (0.0, math.radians(-angle), 0.0), 'XYZ'))

        leftVert.co += leftVector
        rightVert.co += rightVector

        branchAmount += 1

bmesh.update_edit_mesh(mesh)
