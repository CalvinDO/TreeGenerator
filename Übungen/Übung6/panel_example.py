import bpy


class viewport_PT_previewsetitngs(bpy.types.Panel):
    bl_label = "Viewport Preview Settings"
    bl_idname = "myviewportpanel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    @classmethod
    def poll(self, context):
        return bpy.context.scene.render.engine == "CYCLES"

    def draw(self, context):
        ev = bpy.context.scene.eevee
        layout = self.layout
        layout.use_property_split = True


class viewport_PT_previewsetitngs_ao(bpy.types.Panel):
    bl_label = "Viewport Preview AO Settings"
    bl_idname = "myviewportpanel_ao"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw_header(self, context):
        self.layout.prop(bpy.context.scene.eevee, "use_gtao", text="")

    def draw(self, context):
        ev = bpy.context.scene.eevee
        layout = self.layout
        layout.use_property_split = True

        layout.label(text="my icon", icon="QUIT")
        layout.prop(ev, "gtao_distance")
        layout.prop(context.scene, "my_string_prop")


def register():
    #bpy.types.Scene.my_string_prop = bpy.props.StringProperty(name = "mystring", subtype = "PASSWORD")
    bpy.utils.register_class(viewport_PT_previewsetitngs)
    bpy.utils.register_class(viewport_PT_previewsetitngs_ao)


def unregister():
    bpy.utils.unregister_class(viewport_PT_previewsetitngs)
    bpy.utils.unregister_class(viewport_PT_previewsetitngs_ao)


if __name__ == "__main__":
    register()
