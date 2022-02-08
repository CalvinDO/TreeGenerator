from re import search
from numpy.core.numeric import cross, outer
import numpy as np
import mathutils
from bpy.types import Mesh, Object
import math
import bmesh
import bpy
from bmesh.types import BMVert, BMesh
from random import random

bl_info = {
    "name": "Tree Generator",
    "author": "Your Name Here",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh > Tree Generator",
    "description": "Adds a new Tree",
    "warning": "",
    "doc_url": "",
    "category": "Add Mesh",
}


def main(varFromOperator):

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    "Copy your Code here"
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


####################################################################################################################################
####################################################################################################################################
################################DEMO###############################################################################################
################################CODE################################################################################################
####################################################################################################################################
####################################################################################################################################

    bpy.ops.object.select_all(action='SELECT')  # selektiert alle Objekte
    # löscht selektierte objekte
    bpy.ops.object.delete(use_global=False, confirm=False)
    bpy.ops.outliner.orphans_purge()  # löscht überbleibende Meshdaten etc

    mesh: Mesh = bpy.data.meshes.new("tree mesh")
    treeObject: Object = bpy.data.objects.new("tree object", mesh)
    bpy.context.collection.objects.link(treeObject)

    treeMesh: BMesh = bmesh.new()
    treeMesh.from_mesh(mesh)

    # skin modifier
    def map_range(v, from_min, from_max, to_min, to_max):
        """Bringt einen Wert v von einer Skala (from_min, from_max) auf eine neue Skala (to_min, to_max)"""
        return to_min + (v - from_min) * (to_max - to_min) / (from_max - from_min)

    print(" ------- ")

    maxIteration: int = varFromOperator.maxIteration

    lengthDivider: float = varFromOperator.lengthDevider
    lengthDividerIterationMultiplicator: float = varFromOperator.lengthDividerIterationMultiplicator

    lengthStandardDerivationFactor: float = varFromOperator.lengthStandardDerivationFactor
    starAngleStandardDerivation: float = 0

    radiusReductionAcceleration: float = varFromOperator.radiusReductionAcceleration

    radiusGeneralThickness: float = varFromOperator.radiusGeneralThickness

    angle: float = varFromOperator.angle  # 120

    angle *= 1 + (np.random.uniform(-1, 1) / 10000)

    truncVector: mathutils.Vector = mathutils.Vector((0.001, 0, 1))
    currentOriginVectorLength: float = truncVector.length

    treeMesh.to_mesh(mesh)

    import array

    vertexIndices = [0] * (2 ** (maxIteration + 2))
    vertexIterations = [0] * (2 ** (maxIteration + 2))
    vertexPositions = [mathutils.Vector.zero] * (2 ** (maxIteration + 2))

    class Branch:

        vertex: BMVert
        branchVector: mathutils.Vector
        iteration: int
        lengthDevider: float
        currentVertexIndex: int = 0

        def __init__(self, vertex, branchVector, iteration, lengthDevider):
            self.vertex = vertex
            self.branchVector = branchVector
            self.iteration = iteration
            self.lengthDevider = lengthDevider

            vertexIndices[Branch.currentVertexIndex] = self.vertex.index
            vertexIterations[Branch.currentVertexIndex] = self.iteration
            vertexPositions[Branch.currentVertexIndex] = self.vertex.co
            Branch.currentVertexIndex += 1

        def fork(self):

            if self.iteration > maxIteration:
                return

            firstStarVert: BMVert = getExtrudedFirstStarVert(
                self.vertex, self.branchVector.copy(), truncVector, self.lengthDevider)

            firstStarVec: mathutils.Vector = firstStarVert.co - self.vertex.co

            branch1: Branch = Branch(
                firstStarVert, firstStarVec, self.iteration + 1, self.lengthDevider * lengthDividerIterationMultiplicator)
            branch1.fork()

            randomStarAngle: float = np.random.uniform(
                180 - starAngleStandardDerivation, 180 + starAngleStandardDerivation)

            secondStarVert: BMVert = getExtrudedRotatedStarVertex(
                self.vertex, firstStarVec, self.branchVector.normalized(), randomStarAngle,  self.lengthDevider)
            secondStarVec: mathutils.Vector = secondStarVert.co - self.vertex.co

            branch2: Branch = Branch(
                secondStarVert, secondStarVec, self.iteration + 1, self.lengthDevider * lengthDividerIterationMultiplicator)
            branch2.fork()

    def getRodriguesMatrix(axisVector: mathutils.Vector, _angle: float):
        w: mathutils.Matrix = mathutils.Matrix(
            ((0, - axisVector.z,  axisVector.y), (axisVector.z, 0, - axisVector.x), (- axisVector.y,  axisVector.x, 0)))
        return mathutils.Matrix.Identity(
            3) + math.sin(_angle) * w + (2 * math.sin(_angle/2)**2) * mathutils.Matrix(np.matmul(w, w))

    def getExtrudedRotatedStarVertex(_centerVert: BMVert, _lastStarVec: mathutils.Vector, _normalizedOriginVector: mathutils.Vector, _angleDegRodrigues: float, _lengthDivider: float):

        lastStarVecCopy: mathutils.Vector = _lastStarVec.copy()
        lastStarVecCopy.rotate(getRodriguesMatrix(
            _normalizedOriginVector, math.radians(_angleDegRodrigues)))

        lastStarVecCopy.normalize()
        lastStarVecCopy /= np.random.uniform(_lengthDivider -
                                             _lengthDivider * lengthStandardDerivationFactor, _lengthDivider + _lengthDivider * lengthStandardDerivationFactor)

        outputVert: BMVert = bmesh.ops.extrude_vert_indiv(
            treeMesh, verts=[_centerVert])['verts'][0]
        outputVert.co += lastStarVecCopy
        return outputVert

    def getExtrudedFirstStarVert(_centerVert: BMVert, _originVector: mathutils.Vector, _trunc: mathutils.Vector, _lengthDivider):

        _originVector /= np.random.uniform(_lengthDivider -
                                           lengthStandardDerivationFactor, _lengthDivider + lengthStandardDerivationFactor)

        crossedZVector: mathutils.Vector = _originVector.cross(
            _trunc).normalized()
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

    Branch.currentVertexIndex += 1

    centerVert: BMVert = bmesh.ops.extrude_vert_indiv(
        treeMesh, verts=[firstVertex])['verts'][0]
    centerVert.co = truncVector

    Branch.currentVertexIndex += 1

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

    # starVert3 = getExtrudedRotatedStarVertex(
    # centerVert, starVec1, truncVector.normalized(), 360 / 3 * 2)

    # starVert4: BMVert = bmesh.ops.extrude_vert_indiv(
    # treeMesh, verts=[centerVert])['verts'][0]
    # starVert4.co += scaledTruncVector

    treeMesh.to_mesh(mesh)

    # skin modifier:

    my_skinmod: bpy.types.SkinModifier = treeObject.modifiers.new(
        "my skin mod", type="SKIN")

    my_skinmod.branch_smoothing = 0.4
    my_skinmod.use_smooth_shade = True
    my_skinmod.use_x_symmetry = False

    my_subdiv_mod: bpy.types.SubsurfModifier = treeObject.modifiers.new(
        "my subdiv mod", type="SUBSURF")
    my_subdiv_mod.levels = 1
    my_subdiv_mod.render_levels = 1

    correctOrderVertexIndices = [0] * (2 ** (maxIteration + 2))

    for vertexIndex in range(len(vertexIndices)):

        vertexIteration = vertexIterations[vertexIndex]
        print(vertexIteration)
        radius = (1 / (lengthDivider *
                       lengthDividerIterationMultiplicator)) ** (vertexIteration * radiusReductionAcceleration)

        radius *= radiusGeneralThickness

        #radius = vertexIteration / 10

        searchedPos = mesh.vertices[vertexIndex].co
        correctPosIndex = 91919191

        for index, vertex in enumerate(mesh.vertices):
            if vertex.co == searchedPos:
                correctPosIndex = vertex.index
                print(mesh.vertices[vertex.index].co, mesh.vertices[index].co)

        correctOrderVertexIndices[vertexIndex] = correctPosIndex
        mesh.skin_vertices[0].data[correctOrderVertexIndices[vertexIndex]
                                   ].radius = radius, radius

        print("vertex data->    index: ", vertexIndices[vertexIndex], "||| correct order index: ", correctOrderVertexIndices[vertexIndex], "||| iteration: ", vertexIterations[vertexIndex], "||| position: ",
              vertexPositions[correctOrderVertexIndices[vertexIndex]], "||| realPosition: ", mesh.vertices[vertexIndex].co, "||| skinRadius: ", mesh.skin_vertices[0].data[vertexIndex].radius[:])

    treeMesh.free()


####################################################################################################################################
####################################################################################################################################
################################DEMO###############################################################################################
################################CODE################################################################################################
####################################################################################################################################
####################################################################################################################################


class SimpleOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.simple_operator"
    bl_label = "Generate Tree"
    bl_options = {"REGISTER", "UNDO"}

    Baumarten: bpy.props.EnumProperty(
        items=(
            ('Tree1', "Laubbaum", ""),
            ('Tree2', "Tannenbaum", "")
        ),
        default='Tree1'
    )

    angle: bpy.props.FloatProperty(
        name='Winkel',
        description='XYZ',
        default=25,
        min=10,
        max=35)

    maxIteration: bpy.props.IntProperty(
        name='Ast-Abspaltungen',
        description='XYZ',
        default=7,
        min=3,
        max=12)

    subdivViewportRes: bpy.props.IntProperty(
        name='Viewport Auflösung',
        description='Noch keine Funktion',
        default=7,
        min=3,
        max=12)

    lengthDevider: bpy.props.FloatProperty(
        name='Astverkürzung',
        description='XYZ',
        default=1,
        min=0.6,
        max=1.7)

    radiusReductionAcceleration: bpy.props.FloatProperty(
        name='RadiusVerkürzung',
        description='XYZ',
        default=3,
        min=1,
        max=5)

    radiusGeneralThickness: bpy.props.FloatProperty(
        name='Radius',
        description='XYZ',
        default=0.5,
        min=0.1,
        max=1)

    lengthStandardDerivationFactor: bpy.props.FloatProperty(
        name='Astverkürzung Zufallsabweichung',
        description='XYZ',
        default=0.4,
        min=0.1,
        max=0.85)

    lengthDividerIterationMultiplicator: bpy.props.FloatProperty(
        name='lengthDividerIterationMultiplicator',
        description='relative Astverkürzung',
        default=1.2,
        min=1,
        max=1.9)

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, execute):
        main(self)
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
