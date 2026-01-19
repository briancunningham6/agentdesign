import bpy
import math
import os
import sys


def parse_args():
    argv = sys.argv
    if "--" not in argv:
        raise SystemExit("Usage: blender -b -P render_stl_blender.py -- input.stl output.png")
    args = argv[argv.index("--") + 1 :]
    if len(args) != 2:
        raise SystemExit("Expected input.stl and output.png")
    return args[0], args[1]


def setup_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except Exception:
        scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGB"
    if scene.world is None:
        scene.world = bpy.data.worlds.new("World")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.94, 0.95, 0.96, 1.0)
        bg.inputs[1].default_value = 0.6
    try:
        scene.view_settings.view_transform = "Standard"
        scene.view_settings.exposure = 1.0
    except Exception:
        pass
    try:
        eevee = scene.eevee
        eevee.taa_render_samples = 64
        eevee.use_gtao = True
        eevee.gtao_distance = 1.0
    except Exception:
        pass


def import_stl(path):
    if not os.path.exists(path):
        raise SystemExit(f"STL not found: {path}")

    if hasattr(bpy.ops.wm, "stl_import"):
        bpy.ops.wm.stl_import(filepath=path)
    else:
        bpy.ops.import_mesh.stl(filepath=path)
    obj = bpy.context.selected_objects[0]
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    obj.location = (0.0, 0.0, 0.0)
    obj.hide_render = False
    bpy.context.view_layer.update()
    size = max(obj.dimensions.x, obj.dimensions.y, obj.dimensions.z)
    if size > 5000:
        scale = 100.0 / size
        obj.scale = (scale, scale, scale)
    elif size < 1:
        scale = 100.0 / max(size, 0.001)
        obj.scale = (scale, scale, scale)
    bpy.context.view_layer.update()
    obj.data.materials.clear()
    mat = bpy.data.materials.new(name="BaseMaterial")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.35, 0.4, 0.46, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.35
        if "Specular" in bsdf.inputs:
            bsdf.inputs["Specular"].default_value = 0.45
    obj.data.materials.append(mat)
    return obj


def add_camera(target_obj):
    size = max(target_obj.dimensions.x, target_obj.dimensions.y, target_obj.dimensions.z)
    cam_distance = max(200.0, size * 2.5)
    cam_location = (cam_distance, -cam_distance, cam_distance * 0.8)

    bpy.ops.object.camera_add(location=cam_location)
    cam = bpy.context.active_object
    bpy.context.scene.camera = cam
    cam.data.clip_start = 0.1
    cam.data.clip_end = 10000

    direction = target_obj.location - cam.location
    rot_quat = direction.to_track_quat("-Z", "Y")
    cam.rotation_euler = rot_quat.to_euler()


def add_lights():
    bpy.ops.object.light_add(type="AREA", location=(200, -150, 180))
    light = bpy.context.active_object
    light.data.energy = 4500
    light.data.size = 200

    bpy.ops.object.light_add(type="AREA", location=(-200, 150, 120))
    light = bpy.context.active_object
    light.data.energy = 3500
    light.data.size = 160

    bpy.ops.object.light_add(type="POINT", location=(0, 0, 300))
    light = bpy.context.active_object
    light.data.energy = 1400

    bpy.ops.object.light_add(type="SUN", location=(0, 0, 400))
    light = bpy.context.active_object
    light.data.energy = 2.5


def render(output_path):
    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)


def main():
    stl_path, output_path = parse_args()
    setup_scene()
    obj = import_stl(stl_path)
    add_camera(obj)
    add_lights()
    render(output_path)


if __name__ == "__main__":
    main()
