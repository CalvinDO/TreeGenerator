import bpy
import math

FRAMES_PER_UNIT = 1
JUMP_HEIGHT = 0.5
# a
points = bpy.data.collections["points"].objects
sphere: bpy.types.Object = bpy.data.objects["Sphere"]


sphere.location = points[0].location
sphere.keyframe_insert(data_path="location", frame=0)


at_keyframe = FRAMES_PER_UNIT


def get_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2)


for i in range(1, len(points)):

    distance_to_last_point = get_distance(
        points[i-1].location, points[i].location)

    new_keyframe_loc = at_keyframe + FRAMES_PER_UNIT*distance_to_last_point
    intermediate_keyframe_loc = at_keyframe + \
        (FRAMES_PER_UNIT * distance_to_last_point) / 2

    intermediate_point = points[i-1].location + \
        (points[i].location - points[i-1].location) / 2

    intermediate_point.z += JUMP_HEIGHT * distance_to_last_point

    sphere.location = points[i].location
    sphere.keyframe_insert(data_path="location", frame=new_keyframe_loc)

    sphere.location = intermediate_point
    sphere.keyframe_insert(data_path="location",
                           frame=intermediate_keyframe_loc)

    at_keyframe = new_keyframe_loc
