from bmesh.types import BMVert, BMesh
import bpy
import bmesh
import math
from bpy.types import Mesh, Object
import mathutils
import numpy as np

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

minBranchLength: float = 0.025

lengthFactor: float = 1.6180339
angle: float = 137.5077 / 2


truncVector: mathutils.Vector = mathutils.Vector((0, 0, 1))

firstVertex: BMVert = treeMesh.verts.new((0, 0, 0))
branchVert: BMVert = bmesh.ops.extrude_vert_indiv(
    treeMesh, verts=[firstVertex])['verts'][0]
branchVert.co = truncVector


starVert1Vector: mathutils.Vector = truncVector.copy()
starVert1Vector /= lengthFactor
starVert1Vector.rotate(mathutils.Euler((math.radians(angle), 0, 0)))

starVert1: BMVert = bmesh.ops.extrude_vert_indiv(
    treeMesh, verts=[branchVert])['verts'][0]
starVert1.co = truncVector + starVert1Vector

starVert2Vector: mathutils.Vector = mathutils.Vector(starVert1.co)
starVert2Vector.rotate(mathutils.Euler((0, 0, math.radians(360/3))))
starVert2: BMVert = bmesh.ops.extrude_vert_indiv(
    treeMesh, verts=[branchVert])['verts'][0]
starVert2.co = starVert2Vector

starVert3Vector: mathutils.Vector = mathutils.Vector(starVert2.co)
starVert3Vector.rotate(mathutils.Euler((0, 0, math.radians(360/3))))
starVert3: BMVert = bmesh.ops.extrude_vert_indiv(
    treeMesh, verts=[branchVert])['verts'][0]
starVert3.co = starVert3Vector

for v in treeMesh.verts:

    if (len(v.link_edges) == 1) and v.co.z > 0.1:

        innerVert, outerVert = v.link_edges[0].verts

        if innerVert == v:
            innerVert = outerVert
            outerVert = v

        edgeVector: mathutils.Vector = outerVert.co - innerVert.co
        edgeVector /= lengthFactor
        normalizedEdgeVector: mathutils.Vector = edgeVector.normalized()

        if edgeVector.magnitude < minBranchLength:
            break

        crossedZVector = edgeVector.cross((0, 0, 1)).normalized()
        crossedZVector *= edgeVector.magnitude
        crossedZVert = bmesh.ops.extrude_vert_indiv(
            treeMesh, verts=[outerVert])['verts'][0]
        crossedZWithEdgeVector: mathutils.Vector = crossedZVector + edgeVector
        crossedZWithEdgeVector.normalize()
        crossedZWithEdgeVector *= edgeVector.magnitude

        # until another solution is found, the first branch get's randomly rotated to prevent clustered formations due to interference

        wMatrix: mathutils.Matrix = mathutils.Matrix(
            ((0, - normalizedEdgeVector.z,  normalizedEdgeVector.y), (normalizedEdgeVector.z, 0, - normalizedEdgeVector.x), (- normalizedEdgeVector.y,  normalizedEdgeVector.x, 0)))
        thirstVectorAngle: float = math.radians(np.random.uniform(0, 360))
        thirstVectorRodriguesMatrix: mathutils.Matrix = mathutils.Matrix.Identity(
            3) + math.sin(thirstVectorAngle) * wMatrix + (2 * math.sin(thirstVectorAngle/2)**2) * mathutils.Matrix(np.matmul(wMatrix, wMatrix))

        crossedZWithEdgeVector.rotate(thirstVectorRodriguesMatrix)

        crossedZVert.co += crossedZWithEdgeVector

        secondVectorAngle: float = math.radians(360 / 3)
        secondVectorRodriguesMatrix: mathutils.Matrix = mathutils.Matrix.Identity(
            3) + math.sin(secondVectorAngle) * wMatrix + (2 * math.sin(secondVectorAngle/2)**2) * mathutils.Matrix(np.matmul(wMatrix, wMatrix))

        secondVector: mathutils.Vector = crossedZWithEdgeVector.copy()
        secondVector.rotate(secondVectorRodriguesMatrix)
        secondVertex: BMVert = bmesh.ops.extrude_vert_indiv(
            treeMesh, verts=[outerVert])['verts'][0]

        secondVertex.co += secondVector

        thirdVectorAngle: float = math.radians((360 / 3) * 2)
        thirdVectorRodriguesMatrix: mathutils.Matrix = mathutils.Matrix.Identity(
            3) + math.sin(thirdVectorAngle) * wMatrix + (2 * math.sin(thirdVectorAngle/2)**2) * mathutils.Matrix(np.matmul(wMatrix, wMatrix))

        thirdVector: mathutils.Vector = crossedZWithEdgeVector.copy()
        thirdVector.rotate(thirdVectorRodriguesMatrix)
        thirdVertex: BMVert = bmesh.ops.extrude_vert_indiv(
            treeMesh, verts=[outerVert])['verts'][0]

        thirdVertex.co += thirdVector

        """ leftVector: mathutils.Vector = edgeVector.copy()
        rightVector: mathutils.Vector = edgeVector.copy()

        leftVertex = bmesh.ops.extrude_vert_indiv(
            treeMesh, verts=[outerVert])['verts'][0]
        rightVertex = bmesh.ops.extrude_vert_indiv(
            treeMesh, verts=[outerVert])['verts'][0]

        leftVector.rotate(mathutils.Euler(
            (math.radians(-angle), math.radians(-angle), math.radians(-angle)), 'XYZ'))
        rightVector.rotate(mathutils.Euler(
            (math.radians(angle), math.radians(angle), math.radians(angle)), 'XYZ'))

        leftVertex.co += leftVector
        rightVertex.co += rightVector """


treeMesh.to_mesh(mesh)
treeMesh.free()
