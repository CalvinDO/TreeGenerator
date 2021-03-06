from random import random
from bmesh.types import BMVert, BMesh
import bpy
import bmesh
import math
from bpy.types import Mesh, Object
import mathutils
import numpy as np
from numpy.core.numeric import cross, outer


def main(context):
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

    minBranchLength: float = 0.02

lengthDivider: float = 1
lengthDividerIterationMultiplicator: float = 1.1

    lengthDivider: float = 1
    lengthDividerIterationMultiplicator: float = 1.2

mainBranchAngle: float = 5  # 120
mainBranchAngle *= 1 + (np.random.uniform(-1, 1) / 10000)

secondBranchAdditionalAngle: float = 20  # 120
secondBranchAdditionalAngle *= 1 + (np.random.uniform(-1, 1) / 10000)
secondBranchLengthDividerDivider: float = 1

    angle *= 1 + (np.random.uniform(-1, 1) / 10000)

    truncVector: mathutils.Vector = mathutils.Vector((0.001, 0, 1))
    currentOriginVectorLength: float = truncVector.length


    vertex: BMVert
    branchVector: mathutils.Vector
    iteration: int
    lengthDivider: float

    def __init__(self, vertex, branchVector, iteration, lengthDevider):
        self.vertex = vertex
        self.branchVector = branchVector
        self.iteration = iteration
        self.lengthDivider = lengthDevider

        def __init__(self, vertex, branchVector, iteration, lengthDevider):
            self.vertex = vertex
            self.branchVector = branchVector
            self.iteration = iteration
            self.lengthDevider = lengthDevider

        def fork(self):

        firstStarVert: BMVert = getExtrudedFirstStarVert(
            self.vertex, self.branchVector.copy(), truncVector, self.lengthDivider)

            firstStarVert: BMVert = getExtrudedFirstStarVert(
                self.vertex, self.branchVector.copy(), truncVector, self.lengthDevider)

        branch1: Branch = Branch(
            firstStarVert, firstStarVec, self.iteration + 1, self.lengthDivider * lengthDividerIterationMultiplicator)
        branch1.fork()

            branch1: Branch = Branch(
                firstStarVert, firstStarVec, self.iteration + 1, self.lengthDevider * lengthDividerIterationMultiplicator)
            branch1.fork()

        shortenedLengthDivider: float = self.lengthDivider / \
            secondBranchLengthDividerDivider

        secondStarVert: BMVert = getExtrudedRotatedStarVertex(
            self.vertex, firstStarVec, self.branchVector.normalized(), randomStarAngle,  shortenedLengthDivider)
        secondStarVec: mathutils.Vector = secondStarVert.co - self.vertex.co

        branch2: Branch = Branch(
            secondStarVert, secondStarVec, self.iteration + 1, shortenedLengthDivider * lengthDividerIterationMultiplicator)
        branch2.fork()

            branch2: Branch = Branch(
                secondStarVert, secondStarVec, self.iteration + 1, self.lengthDevider * lengthDividerIterationMultiplicator)
            branch2.fork()


    def getRodriguesMatrix(axisVector: mathutils.Vector, _angle: float):
        w: mathutils.Matrix = mathutils.Matrix(
            ((0, - axisVector.z,  axisVector.y), (axisVector.z, 0, - axisVector.x), (- axisVector.y,  axisVector.x, 0)))
        return mathutils.Matrix.Identity(
            3) + math.sin(_angle) * w + (2 * math.sin(_angle/2)**2) * mathutils.Matrix(np.matmul(w, w))


    lastStarVecCopy: mathutils.Vector = _lastStarVec.copy()

    lastStarVecCopy.rotate(getRodriguesMatrix(
        _normalizedOriginVector, math.radians(_angleDegRodrigues)))

        lastStarVecCopy: mathutils.Vector = _lastStarVec.copy()
        lastStarVecCopy.rotate(getRodriguesMatrix(
            _normalizedOriginVector, math.radians(_angleDegRodrigues)))

    # rotate further apart from main Branch

    crossedLastVector: mathutils.Vector = _normalizedOriginVector.cross(
        lastStarVecCopy).normalized()

    lastStarVecCopy.rotate(getRodriguesMatrix(
        crossedLastVector, math.radians(secondBranchAdditionalAngle)))

    outputVert: BMVert = bmesh.ops.extrude_vert_indiv(
        treeMesh, verts=[_centerVert])['verts'][0]
    outputVert.co += lastStarVecCopy

    return outputVert

        outputVert: BMVert = bmesh.ops.extrude_vert_indiv(
            treeMesh, verts=[_centerVert])['verts'][0]
        outputVert.co += lastStarVecCopy
        return outputVert


    def getExtrudedFirstStarVert(_centerVert: BMVert, _originVector: mathutils.Vector, _trunc: mathutils.Vector, _lengthDivider):

    crossedZVector: mathutils.Vector = _originVector.cross(_trunc).normalized()
    rotatedOriginVector: mathutils.Vector = _originVector.copy()
    rotatedOriginVector.rotate(getRodriguesMatrix(
        crossedZVector, math.radians(mainBranchAngle)))

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


    scaledTruncVector = truncVector.copy()
    scaledTruncVector /= lengthDivider

    randomizeVector(scaledTruncVector)


    # initial branches

    firstVertex: BMVert = treeMesh.verts.new((0, 0, 0))


    centerVert: BMVert = bmesh.ops.extrude_vert_indiv(
        treeMesh, verts=[firstVertex])['verts'][0]
    centerVert.co = truncVector


    starVert1: BMVert = getExtrudedFirstStarVert(
        centerVert, truncVector, mathutils.Vector((1, 0, 0)), lengthDivider)

    starVec1: mathutils.Vector = starVert1.co - centerVert.co

    branch1: Branch = Branch(starVert1, starVec1, 1, lengthDivider)
    branch1.fork()


    randomStarAngle: float = np.random.uniform(
        180 - starAngleStandardDerivation, 180 + starAngleStandardDerivation)

    starVert2: BMVert = getExtrudedRotatedStarVertex(
        centerVert, starVec1, truncVector.normalized(),  randomStarAngle, lengthDivider)

    starVec2: mathutils.Vector = starVert2.co - centerVert.co

    branch2: Branch = Branch(starVert2, starVec2, 1, lengthDivider)
    branch2.fork()


# starVert4: BMVert = bmesh.ops.extrude_vert_indiv(
# treeMesh, verts=[centerVert])['verts'][0]
# starVert4.co += scaledTruncVector

    # starVert4: BMVert = bmesh.ops.extrude_vert_indiv(
    # treeMesh, verts=[centerVert])['verts'][0]
    #starVert4.co += scaledTruncVector


    treeMesh.to_mesh(mesh)
    treeMesh.free()







class SimpleOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.simple_operator"
    bl_label = "Generate Tree"


    def execute(self, context):
        main(context)
        return {'FINISHED'}







class LayoutDemoPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Layout Demo"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        # Big render button
        layout.label(text="Tree")
        row = layout.row()
        row.scale_y = 3.0
        row.operator("object.simple_operator")



def register():
    bpy.utils.register_class(SimpleOperator)
    bpy.utils.register_class(LayoutDemoPanel)


def unregister():
    bpy.utils.unregister_class(SimpleOperator)
    bpy.utils.unregister_class(LayoutDemoPanel)


if __name__ == "__main__":
    register()