from bmesh.types import BMVert, BMesh
import bpy
import bmesh
import math
from bpy.types import Mesh, Object
import mathutils
import numpy as np
from numpy.core.numeric import cross, outer

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
angle: float = 120

angle *= 1 + (np.random.uniform(-1, 1) / 10000)
print(angle)


def getRodriguesMatrix(axisVector: mathutils.Vector, _angle: float):
    w: mathutils.Matrix = mathutils.Matrix(
        ((0, - axisVector.z,  axisVector.y), (axisVector.z, 0, - axisVector.x), (- axisVector.y,  axisVector.x, 0)))
    return mathutils.Matrix.Identity(
        3) + math.sin(_angle) * w + (2 * math.sin(_angle/2)**2) * mathutils.Matrix(np.matmul(w, w))


def getExtrudedRotatedStarVertex(_centerVert: BMVert, _lastStarVec: mathutils.Vector, _normalizedOriginVector: mathutils.Vector, _angleDeg: float):
    lastStarVecCopy: mathutils.Vector = _lastStarVec.copy()
    lastStarVecCopy.rotate(getRodriguesMatrix(
        _normalizedOriginVector, math.radians(_angleDeg)))

    outputVert: BMVert = bmesh.ops.extrude_vert_indiv(
        treeMesh, verts=[_centerVert])['verts'][0]
    outputVert.co += lastStarVecCopy
    return outputVert


def getExtrudedFirstStarVert(_centerVert: BMVert, _originVector: mathutils.Vector, _trunc: mathutils.Vector):
    _originVector /= lengthFactor

    crossedZVector: mathutils.Vector = _originVector.cross(_trunc).normalized()
    rotatedOriginVector: mathutils.Vector = _originVector.copy()
    rotatedOriginVector.rotate(getRodriguesMatrix(
        crossedZVector, math.radians(angle)))

    rotatedOriginVector.rotate(getRodriguesMatrix(
        _originVector.normalized(), math.radians(np.random.uniform(0, 360))))

    firstStarVert: BMVert = bmesh.ops.extrude_vert_indiv(
        treeMesh, verts=[_centerVert])['verts'][0]
    firstStarVert.co += rotatedOriginVector

    # crossedZVector *= _originVector.magnitude

    # rotatedOriginVector.rotate(getRodriguesMatrix(
    #     crossedZVector.normalized(), math.radians(angle)))
    # #firstStarVector.rotate(getRodriguesMatrix(    crossedZVector.normalized(), math.radians(angle)))

    # firstStarVector.normalize()
    # firstStarVector *= _originVector.magnitude
    # # until another solution is found, the first branch get's randomly rotated to prevent clustered formations due to interference
    # firstStarVector.rotate(getRodriguesMatrix(
    #     _originVector.normalized(), math.radians(np.random.uniform(0, 360))))

    # firstStarVert.co += firstStarVector

    return firstStarVert


def randomizeVector(vector: mathutils.Vector):
    vector.x *= 1 + \
        (np.random.uniform(-1, 1) / (10000 * vector.magnitude))
    vector.y *= 1 + \
        (np.random.uniform(-1, 1) / (10000 * vector.magnitude))


truncVector: mathutils.Vector = mathutils.Vector((0.001, 0, 1))
scaledTruncVector = truncVector.copy()
scaledTruncVector /= lengthFactor

randomizeVector(scaledTruncVector)

firstVertex: BMVert = treeMesh.verts.new((0, 0, 0))

centerVert: BMVert = bmesh.ops.extrude_vert_indiv(
    treeMesh, verts=[firstVertex])['verts'][0]
centerVert.co = truncVector


starVert1 = getExtrudedFirstStarVert(
    centerVert, truncVector, mathutils.Vector((1, 0, 0)))
starVec1: mathutils.Vector = starVert1.co - centerVert.co

starVert2 = getExtrudedRotatedStarVertex(
    centerVert, starVec1, truncVector.normalized(),  360 / 3)

starVert3 = getExtrudedRotatedStarVertex(
    centerVert, starVec1, truncVector.normalized(), 360 / 3 * 2)

starVert4: BMVert = bmesh.ops.extrude_vert_indiv(
    treeMesh, verts=[centerVert])['verts'][0]
starVert4.co += scaledTruncVector


for v in treeMesh.verts:
    if (len(v.link_edges) == 1) and v.co.z > 0.1:

        innerVert, outerVert = v.link_edges[0].verts

        if innerVert == v:
            innerVert = outerVert
            outerVert = v

        originVector: mathutils.Vector = outerVert.co - innerVert.co
        if originVector.x == 0 and originVector.y == 0:
            randomizeVector(originVector)

        normalizedOriginVector: mathutils.Vector = originVector.normalized()

        firstStarVert: BMVert = getExtrudedFirstStarVert(
            outerVert, originVector, truncVector)
        firstStarVec: mathutils.Vector = firstStarVert.co - outerVert.co

        if firstStarVec.magnitude < minBranchLength:
            break

        secondStarVert: BMVert = getExtrudedRotatedStarVertex(
            outerVert, firstStarVec, normalizedOriginVector, 360 / 3)

        thirdStarVert: BMVert = getExtrudedRotatedStarVertex(
            outerVert, firstStarVec, normalizedOriginVector, 360 / 3 * 2)

        thouthStarVert: BMVert = bmesh.ops.extrude_vert_indiv(
            treeMesh, verts=[outerVert])['verts'][0]
        thouthStarVert.co += originVector


treeMesh.to_mesh(mesh)
treeMesh.free()
