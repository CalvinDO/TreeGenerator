from quopri import decodestring
from re import S, search
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

    for col in bpy.data.collections:
        for obj in col.all_objects:
            obj.select_set(False)

    # selektiert alle Generierten Objekte

    generatedObjectsCollectionName = varFromOperator.generatedObjectsCollection

    try:
        for obj in bpy.data.collections[generatedObjectsCollectionName].all_objects:
            obj.select_set(True)
    except KeyError:
        print("Name der Collection für die generierten Objekte ist ungültig!")
        pass

    # löscht selektierte objekte
    bpy.ops.object.delete(use_global=False, confirm=False)
    bpy.ops.outliner.orphans_purge()  # löscht überbleibende Meshdaten etc

    mesh: Mesh = bpy.data.meshes.new("tree mesh")
    treeObject: Object = bpy.data.objects.new("tree object", mesh)
    bpy.data.collections[generatedObjectsCollectionName].objects.link(
        treeObject)

    treeMesh: BMesh = bmesh.new()
    treeMesh.from_mesh(mesh)

    treeMatName = varFromOperator.branchMaterial

    mat = bpy.data.materials.get(treeMatName)

    # Assign it to object
    if treeObject.data.materials:
        # assign to 1st material slot
        treeObject.data.materials[0] = mat
    else:
        # no slots
        treeObject.data.materials.append(mat)

    print(" ------- ")

    maxIteration: int = varFromOperator.maxIteration

    lengthDivider: float = varFromOperator.lengthDevider
    lengthDividerIterationMultiplicator: float = varFromOperator.lengthDividerIterationMultiplicator

    lengthStandardDerivationFactor: float = varFromOperator.lengthStandardDerivationFactor
    starAngleStandardDerivation: float = 45

    radiusReductionAcceleration: float = varFromOperator.radiusReductionAcceleration

    radiusGeneralThickness: float = varFromOperator.radiusGeneralThickness

    generateLeafs: bool = varFromOperator.generateLeafs

    sunOptimizationFactor: float = varFromOperator.sunOptimizationFactor
    spaceOptimizationFactor: float = varFromOperator.spaceOptimizationFactor

    angle: float = varFromOperator.angle  # 120

    angle *= 1 + (np.random.uniform(-1, 1) / 10000)

    truncVector: mathutils.Vector = mathutils.Vector((0.001, 0, 1))
    currentOriginVectorLength: float = truncVector.length

    treeMesh.to_mesh(mesh)

    import array

    vertexIndices = [0] * (2 ** (maxIteration + 2))
    vertexIterations = [0] * (2 ** (maxIteration + 2))
    vertexPositions = [mathutils.Vector.zero] * (2 ** (maxIteration + 2))

    # leafs:

    if generateLeafs:

        try:

            leafObject: Object = bpy.data.objects[varFromOperator.leaf]
        except KeyError:
            print("Please enter the name of a leaf in your scene!")
            return
        leafObject.select_set(True)

    sunVector: mathutils.Vector = ((0, 0, 1))

    def duplicate(obj: Object, collection=None):

        obj_copy: Object = obj.copy()
        obj_copy.data = obj_copy.data.copy()

        if obj_copy.animation_data:
            obj_copy.animation_data.action = obj_copy.animation_data.action.copy()

        collection.objects.link(obj_copy)

        return obj_copy

    class Branch:

        vertex: BMVert
        branchVector: mathutils.Vector
        iteration: int
        lengthDevider: float
        currentVertexIndex: int = 0
        positionSumVector: mathutils.Vector = mathutils.Vector((0, 0, 0))

        def __init__(self, vertex, branchVector, iteration, lengthDevider):
            self.vertex = vertex
            self.branchVector = branchVector
            self.iteration = iteration
            self.lengthDevider = lengthDevider

            vertexIndices[Branch.currentVertexIndex] = self.vertex.index
            vertexIterations[Branch.currentVertexIndex] = self.iteration
            vertexPositions[Branch.currentVertexIndex] = self.vertex.co

            Branch.currentVertexIndex += 1

            Branch.positionSumVector += mathutils.Vector(
                (self.vertex.co.x, self.vertex.co.y, 0))

        def fork(self):

            if self.iteration > maxIteration:

                if not generateLeafs:
                    return

                duplicatedLeaf: Object = duplicate(
                    leafObject, collection=bpy.data.collections[generatedObjectsCollectionName])
                duplicatedLeaf.location = self.vertex.co

                branchVectorRotation: mathutils.Quaternion = self.branchVector.to_track_quat(
                    '-Y', 'Z')

                branchVectorEuler: mathutils.Euler = branchVectorRotation.to_euler()

                duplicatedLeaf.rotation_euler = branchVectorEuler

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

        illuminationBoostFactor: float = 1
        spaceBoostFactor: float = 1

        if lastStarVecCopy.length > 0:

            # grow to sun
            sunAnglePercentage: float = lastStarVecCopy.angle(sunVector) / 180
            sunAnglePercentage *= sunOptimizationFactor
            illuminationBoostFactor = np.clip(1 - sunAnglePercentage, 0, 1)

            # grow to free space

            if Branch.currentVertexIndex > 3:
                print(Branch.currentVertexIndex)

                currentNegatedSumVector: mathutils.Vector = - Branch.positionSumVector
                currentDirectionXY: mathutils.Vector = mathutils.Vector(
                    (lastStarVecCopy.x, lastStarVecCopy.y, 0))
                spaceAnglePercentage: float = currentDirectionXY.angle(
                    currentNegatedSumVector) / 180
                spaceAnglePercentage *= spaceBoostFactor
                spaceBoostFactor = np.clip(1 - spaceAnglePercentage, 0.02, 1)

        outputVert.co += (lastStarVecCopy *
                          (illuminationBoostFactor * spaceBoostFactor))

        return outputVert

    def getExtrudedFirstStarVert(_centerVert: BMVert, _originVector: mathutils.Vector, _trunc: mathutils.Vector, _lengthDivider):

        _originVector /= np.random.uniform(_lengthDivider -
                                           lengthStandardDerivationFactor, _lengthDivider + lengthStandardDerivationFactor)

        crossedZVector: mathutils.Vector = _originVector.cross(
            _trunc)
        crossedZVector.normalize()
        rotatedOriginVector: mathutils.Vector = _originVector.copy()
        rotatedOriginVector.rotate(getRodriguesMatrix(
            crossedZVector, math.radians(angle)))

        rotatedOriginVector.rotate(getRodriguesMatrix(
            _originVector.normalized(), math.radians(np.random.uniform(0, 360))))

        firstStarVert: BMVert = bmesh.ops.extrude_vert_indiv(
            treeMesh, verts=[_centerVert])['verts'][0]

        illuminationBoostFactor: float = 1
        spaceBoostFactor: float = 1

        if rotatedOriginVector.length > 0:

            # grow to sun
            sunAnglePercentage: float = rotatedOriginVector.angle(
                sunVector) / (math.pi / 2)

            sunAnglePercentage *= sunOptimizationFactor
            illuminationBoostFactor = np.clip(
                1 - sunAnglePercentage, 0.25, 1)

            # grow to free space
            if Branch.currentVertexIndex > 3:
                currentNegatedSumVector: mathutils.Vector = - Branch.positionSumVector
                currentDirectionXY: mathutils.Vector = mathutils.Vector(
                    (rotatedOriginVector.x, rotatedOriginVector.y, 0))
                currentDirectionXY.normalize()

                spaceAnglePercentage: float = currentDirectionXY.angle(
                    currentNegatedSumVector) / (math.pi / 2)
                spaceAnglePercentage *= spaceBoostFactor
                spaceBoostFactor = np.clip(1 - spaceAnglePercentage, 0.02, 1)

        firstStarVert.co += (rotatedOriginVector *
                             (illuminationBoostFactor * spaceBoostFactor))
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
        radius = (1 / (lengthDivider *
                       lengthDividerIterationMultiplicator)) ** (vertexIteration * radiusReductionAcceleration)

        radius *= radiusGeneralThickness

        # radius = vertexIteration / 10

        searchedPos = mesh.vertices[vertexIndex].co
        correctPosIndex = 91919191

        for index, vertex in enumerate(mesh.vertices):
            if vertex.co == searchedPos:
                correctPosIndex = vertex.index

        correctOrderVertexIndices[vertexIndex] = correctPosIndex
        mesh.skin_vertices[0].data[correctOrderVertexIndices[vertexIndex]
                                   ].radius = radius, radius

    treeMesh.free()
    for col in bpy.data.collections:
        for obj in col.all_objects:
            obj.select_set(False)
    leafObject.hide_set(True)

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

    # leafType: bpy.props.EnumProperty(
    #     items=(
    #         ('leaf 1', "leaf 1", ""),
    #         ('leaf 2', "leaf 2", ""),
    #         ('leaf 3', "leaf 3", ""),
    #         ('leaf 4', "leaf 4", ""),
    #         ('leaf 5', "leaf 5", ""),
    #         ('leaf 6', "leaf 6", ""),
    #         ('leaf 7', "leaf 7", ""),
    #         ('leaf 8', "leaf 8", ""),
    #         ('leaf 9', "leaf 9", ""),
    #     ),
    #     default='leaf 1'
    # )

    generateLeafs: bpy.props.BoolProperty(
        name='Blätter generieren',
        description='Schaltet um, ob Blätter generiert werden',
        default=True
    )

    leaf: bpy.props.StringProperty(
        name='Blatt',
        description='Name des Blattes in der Szene',
        default='leaf 4'
    )

    branchMaterial: bpy.props.StringProperty(
        name='Zweig-Material',
        description='Name des Materials, welches die Äste bekommen sollen',
        default='TreeBark'
    )

    generatedObjectsCollection: bpy.props.StringProperty(
        name='GenerierteObjekteCollection',
        description='Name der Collection, in der die generierten Objekte abgelegt werden',
        default='TreeCollection'
    )

    angle: bpy.props.FloatProperty(
        name='Winkel',
        description='Winkel zwischen den Ästen',
        default=28,
        min=10,
        max=45)

    maxIteration: bpy.props.IntProperty(
        name='Ast-Abspaltungen/ Iterationen',
        description='Anzahl der Ast-Abspaltungen/ Iterationen. (Achtung, Blätteranzahl verdoppelt sich pro Iteration!)',
        default=7,
        min=3,
        max=10)

    lengthDevider: bpy.props.FloatProperty(
        name='Astverkürzung',
        description='Faktor, um den jeder Ast durchschnittlich kürzer ist als sein Vorgänger',
        default=1.03,
        min=1,
        max=2.5)

    lengthDividerIterationMultiplicator: bpy.props.FloatProperty(
        name='relative Astverkürzung',
        description='Faktor, mit dem sich die Astverkürzung pro Abspaltung erhöht',
        default=1.17,
        min=1,
        max=2)

    lengthStandardDerivationFactor: bpy.props.FloatProperty(
        name='Astverkürzung Zufallsabweichung',
        description='Multiplikative Abweichungs-Range, in der sich die Astverkürzung zufällig bewegt',
        default=0.07,
        min=0,
        max=0.85)

    spaceOptimizationFactor: bpy.props.FloatProperty(
        name='Platzoptimierung',
        description='Einfluss-Faktor der Platzoptimierung',
        default=0.91,
        min=0,
        max=1)

    sunOptimizationFactor: bpy.props.FloatProperty(
        name='Sonnenoptimierung',
        description='Einfluss-Faktor der Sonnenoptimierung',
        default=0.52,
        min=0,
        max=1)

    radiusReductionAcceleration: bpy.props.FloatProperty(
        name='Radius Verkürzung',
        description='Faktor, mit dem sich der Radius pro Abspaltung verkleinert',
        default=2.05,
        min=0.5,
        max=4)

    radiusGeneralThickness: bpy.props.FloatProperty(
        name='Radius',
        description='Initialer Radius, nichtlinear',
        default=0.35,
        min=0.1,
        max=1)

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, execute):
        main(self)
        return {'FINISHED'}


class LayoutDemoPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "TreeGenerator"
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
