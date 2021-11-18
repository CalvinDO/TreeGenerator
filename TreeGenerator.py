from bmesh.types import BMVert, BMesh
import bpy
import bmesh
import math
from bpy.types import Mesh, Object
import mathutils


bpy.ops.object.select_all(action='SELECT')  # selektiert alle Objekte
# löscht selektierte objekte
bpy.ops.object.delete(use_global=False, confirm=False)
bpy.ops.outliner.orphans_purge()  # löscht überbleibende Meshdaten etc

mesh: Mesh = bpy.data.meshes.new("tree mesh")
treeObject: Object = bpy.data.objects.new("tree object", mesh)
bpy.context.collection.objects.link(treeObject)


treeMesh: BMesh = bmesh.new()
treeMesh.from_mesh(mesh)

print(" ------- ")

minBranchLength: float = 0.05

lengthFactor: float = 1.6180339
angle: float = 137.5077 / 2

firstVertex: BMVert = treeMesh.verts.new((0, 0, 0))
secondVertex: BMVert = bmesh.ops.extrude_vert_indiv(
    treeMesh, verts=[firstVertex])['verts'][0]
secondVertex.co = (0, 0, 1)

for v in treeMesh.verts:

    if (len(v.link_edges) == 1) and v.co.z > 0.1:

        innerVert, outerVert = v.link_edges[0].verts

        if innerVert == v:
            innerVert = outerVert
            outerVert = v

        edgeVector: mathutils.Vector = outerVert.co - innerVert.co
        edgeVector /= lengthFactor

        if edgeVector.magnitude < minBranchLength:
            break

        leftVector: mathutils.Vector = edgeVector.copy()
        rightVector: mathutils.Vector = edgeVector.copy()

        leftVertex = bmesh.ops.extrude_vert_indiv(
            treeMesh, verts=[outerVert])['verts'][0]
        rightVertex = bmesh.ops.extrude_vert_indiv(
            treeMesh, verts=[outerVert])['verts'][0]

        rotx = math.atan2(edgeVector.y, edgeVector.z)
        roty = math.atan2(edgeVector.x * math.cos(rotx), edgeVector.z)
        rotz = math.atan2(math.cos(rotx), math.sin(rotx) * math.sin(roty))

        edgeVectorRotation: mathutils.Euler = mathutils.Euler(
            (rotx, roty, rotz), 'XYZ')

        #edgeVectorMinusRotation: mathutils.Euler = mathutils.Euler((rotx - 45, roty - 45, rotz - 45), 'XYZ')

        additionalRotation: mathutils.Euler = mathutils.Euler(
            (math.radians(angle), math.radians(angle), 0.0), 'XYZ')

        additionalNegativeRotation: mathutils.Euler = mathutils.Euler(
            (math.radians(-angle), math.radians(-angle), 0.0), 'XYZ')

        finalLeftRotation: mathutils.Euler = edgeVectorRotation.copy()
        finalLeftRotation.rotate(additionalRotation)

        finalRightRotation: mathutils.Euler = edgeVectorRotation.copy()
        finalRightRotation.rotate(additionalRotation)

        leftVector.rotate(additionalRotation)
        rightVector.rotate(additionalNegativeRotation)

        leftVertex.co += leftVector
        rightVertex.co += rightVector

        print("lölasdf")

treeMesh.to_mesh(mesh)
treeMesh.free()
