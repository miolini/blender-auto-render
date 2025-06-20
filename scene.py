# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#  Massively Parallel Forth Processor Grid - Visualization Generator 
#
#  This script is now a "pure" scene generator. All render settings
#  (resolution, fps, etc.) are controlled by the external launcher script.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import bpy
import bmesh
import math
import random
from mathutils import Vector

# --- CONFIGURATION PARAMETERS ---
GRID_SIZE_X = 16
GRID_SIZE_Y = 16
GRID_SIZE_Z = 16
CORE_SIZE = 0.4
ROUTER_SIZE = 0.15
SPACING = 1.5
COOLING_PLATE_THICKNESS = 0.05
NUM_PACKETS = 30
PACKET_TRAVEL_TIME = 10

# --- UTILITY FUNCTIONS ---

def clean_scene():
    if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for item in bpy.data.meshes: bpy.data.meshes.remove(item)
    for item in bpy.data.materials: bpy.data.materials.remove(item)
    for item in bpy.data.actions: bpy.data.actions.remove(item)
    for item in bpy.data.collections:
        if item.name != "Scene Collection":
            bpy.data.collections.remove(item)

def get_core_position(x, y, z):
    return Vector((x * SPACING, y * SPACING, z * SPACING))

def create_material(name, color, alpha=1.0, emission_color=(0,0,0,1), emission_strength=1.0, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Alpha'].default_value = alpha
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    if sum(emission_color[:3]) > 0:
        bsdf.inputs['Emission Color'].default_value = emission_color
        bsdf.inputs['Emission Strength'].default_value = emission_strength
    if alpha < 1.0:
        mat.blend_method = 'BLEND'
        mat.shadow_method = 'NONE'
    return mat

def create_primitive(object_name, collection, primitive_type, **kwargs):
    bm = bmesh.new()
    if primitive_type == 'CUBE':
        bmesh.ops.create_cube(bm, **kwargs)
    elif primitive_type == 'SPHERE':
        bmesh.ops.create_uvsphere(bm, **kwargs)
    else:
        bm.free()
        raise ValueError(f"Unsupported primitive type: {primitive_type}")
    mesh = bpy.data.meshes.new(object_name + "_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(object_name, mesh)
    collection.objects.link(obj)
    return obj

# --- MODEL CREATION FUNCTIONS ---

def create_base_models():
    base_model_coll = bpy.data.collections.new("BaseModels")
    bpy.context.scene.collection.children.link(base_model_coll)
    core_obj = create_primitive("Base_ForthCore", base_model_coll, 'CUBE', size=CORE_SIZE)
    core_obj.data.materials.append(MAT_CORE)
    router_obj = create_primitive("Base_NoCRouter", base_model_coll, 'SPHERE', radius=ROUTER_SIZE, u_segments=16, v_segments=8)
    router_obj.data.materials.append(MAT_ROUTER)
    base_model_coll.hide_render = True
    base_model_coll.hide_viewport = True
    return core_obj, router_obj

def create_grid(core_base, router_base):
    grid_coll = bpy.data.collections.new("ForthGrid")
    bpy.context.scene.collection.children.link(grid_coll)
    for z in range(GRID_SIZE_Z):
        for y in range(GRID_SIZE_Y):
            for x in range(GRID_SIZE_X):
                pos = get_core_position(x, y, z)
                core_inst = bpy.data.objects.new(f"Core_{x}_{y}_{z}", core_base.data)
                core_inst.location = pos
                grid_coll.objects.link(core_inst)
                router_inst = bpy.data.objects.new(f"Router_{x}_{y}_{z}", router_base.data)
                router_inst.location = pos
                grid_coll.objects.link(router_inst)

def create_chiplets():
    chiplet_coll = bpy.data.collections.new("Chiplets")
    bpy.context.scene.collection.children.link(chiplet_coll)
    size_x = GRID_SIZE_X * SPACING
    size_y = GRID_SIZE_Y * SPACING
    size_z = GRID_SIZE_Z * SPACING
    center_pos = get_core_position((GRID_SIZE_X-1)/2, (GRID_SIZE_Y-1)/2, (GRID_SIZE_Z-1)/2)
    chiplet_box = create_primitive("Chiplet_Box", chiplet_coll, 'CUBE', size=1)
    chiplet_box.location = center_pos
    chiplet_box.scale = (size_x, size_y, size_z)
    chiplet_box.data.materials.append(MAT_CHIPLET)

def create_cooling_grid():
    cooling_coll = bpy.data.collections.new("CoolingGrid")
    bpy.context.scene.collection.children.link(cooling_coll)
    plate_mesh = bpy.data.meshes.new("BasePlate_Mesh")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    bm.to_mesh(plate_mesh)
    bm.free()
    plate_mesh.materials.append(MAT_COOLING_PLATE)
    grid_width = (GRID_SIZE_X - 1) * SPACING
    grid_depth = (GRID_SIZE_Y - 1) * SPACING
    grid_height = (GRID_SIZE_Z - 1) * SPACING
    for z in range(GRID_SIZE_Z - 1):
        plate_obj = bpy.data.objects.new(f"Plate_Z_{z}", plate_mesh)
        plate_obj.location = get_core_position(grid_width / (2*SPACING), grid_depth / (2*SPACING), z + 0.5)
        plate_obj.scale = (grid_width + SPACING, grid_depth + SPACING, COOLING_PLATE_THICKNESS)
        cooling_coll.objects.link(plate_obj)
    for y in range(GRID_SIZE_Y - 1):
        plate_obj = bpy.data.objects.new(f"Plate_Y_{y}", plate_mesh)
        plate_obj.location = get_core_position(grid_width / (2*SPACING), y + 0.5, grid_height / (2*SPACING))
        plate_obj.scale = (grid_width + SPACING, COOLING_PLATE_THICKNESS, grid_height + SPACING)
        cooling_coll.objects.link(plate_obj)
    for x in range(GRID_SIZE_X - 1):
        plate_obj = bpy.data.objects.new(f"Plate_X_{x}", plate_mesh)
        plate_obj.location = get_core_position(x + 0.5, grid_depth / (2*SPACING), grid_height / (2*SPACING))
        plate_obj.scale = (COOLING_PLATE_THICKNESS, grid_depth + SPACING, grid_height + SPACING)
        cooling_coll.objects.link(plate_obj)

# --- ANIMATION FUNCTIONS ---

def create_packet(name, start_frame, collection, material):
    packet = create_primitive(name, collection, 'SPHERE', radius=0.3, u_segments=16, v_segments=8)
    packet.data.materials.append(material)
    packet.hide_viewport = True
    packet.hide_render = True
    packet.keyframe_insert(data_path="hide_viewport", frame=start_frame - 1)
    packet.keyframe_insert(data_path="hide_render", frame=start_frame - 1)
    packet.hide_viewport = False
    packet.hide_render = False
    packet.keyframe_insert(data_path="hide_viewport", frame=start_frame)
    packet.keyframe_insert(data_path="hide_render", frame=start_frame)
    return packet

def animate_packet_route(packet, start_frame, start_coord, end_coord, anim_end_frame):
    current_frame = start_frame
    packet.location = get_core_position(start_coord[0], start_coord[1], start_coord[2])
    packet.keyframe_insert(data_path="location", frame=current_frame)
    dist_x = abs(end_coord[0] - start_coord[0])
    dist_y = abs(end_coord[1] - start_coord[1])
    dist_z = abs(end_coord[2] - start_coord[2])
    frame_after_x = start_frame + dist_x * PACKET_TRAVEL_TIME
    packet.location = get_core_position(end_coord[0], start_coord[1], start_coord[2])
    packet.keyframe_insert(data_path="location", frame=frame_after_x)
    frame_after_y = frame_after_x + dist_y * PACKET_TRAVEL_TIME
    packet.location = get_core_position(end_coord[0], end_coord[1], start_coord[2])
    packet.keyframe_insert(data_path="location", frame=frame_after_y)
    frame_after_z = frame_after_y + dist_z * PACKET_TRAVEL_TIME
    packet.location = get_core_position(end_coord[0], end_coord[1], end_coord[2])
    packet.keyframe_insert(data_path="location", frame=frame_after_z)
    packet.hide_viewport = True
    packet.hide_render = True
    packet.keyframe_insert(data_path="hide_viewport", frame=frame_after_z + 1)
    packet.keyframe_insert(data_path="hide_render", frame=frame_after_z + 1)

# --- MAIN EXECUTION ---

if __name__ == "__main__":
    print("--- Starting Scene Generation (v15) ---")
    clean_scene()

    # Note: FPS, Resolution, and Frame Range are now set by the launcher script.
    anim_end_frame = bpy.context.scene.frame_end

    # --- Create Materials ---
    MAT_CORE = create_material("Core_Mat", (0.2, 0.5, 0.8, 1))
    MAT_ROUTER = create_material("Router_Mat", (0.8, 0.8, 0.1, 1))
    MAT_CHIPLET = create_material("Chiplet_Casing", (0.7, 0.8, 1.0, 1.0), alpha=0.7)
    MAT_COOLING_PLATE = create_material("Cooling_Plate", (0.4, 0.9, 1.0, 1.0), alpha=0.05)
    packet_colors = [
        (1, 0.1, 0.1, 1), (0.1, 1, 0.1, 1), (0.1, 0.5, 1, 1),
        (1, 1, 0.1, 1), (1, 0.1, 1, 1)
    ]
    MAT_PACKETS = [create_material(f"Packet_Mat_{i}", (1,1,1,1), emission_color=color, emission_strength=50.0) for i, color in enumerate(packet_colors)]

    # --- Create Geometry ---
    print("Creating base models...")
    core_base, router_base = create_base_models()
    print("Creating core grid...")
    create_grid(core_base, router_base)
    print("Creating chiplet casing...")
    create_chiplets()
    print("Creating 3D cooling grid...")
    create_cooling_grid()

    # --- Create High-Traffic Animation ---
    print(f"Generating {NUM_PACKETS} random packet animations...")
    anim_coll = bpy.data.collections.new("AnimationObjects")
    bpy.context.scene.collection.children.link(anim_coll)
    for i in range(NUM_PACKETS):
        start_coord = (random.randint(0, GRID_SIZE_X-1), random.randint(0, GRID_SIZE_Y-1), random.randint(0, GRID_SIZE_Z-1))
        end_coord = (random.randint(0, GRID_SIZE_X-1), random.randint(0, GRID_SIZE_Y-1), random.randint(0, GRID_SIZE_Z-1))
        while start_coord == end_coord:
            end_coord = (random.randint(0, GRID_SIZE_X-1), random.randint(0, GRID_SIZE_Y-1), random.randint(0, GRID_SIZE_Z-1))
        # Ensure start_frame is within valid range
        max_start_frame = max(0, int(anim_end_frame) - 500)
        start_frame = random.randint(0, max_start_frame) if max_start_frame > 0 else 0
        packet_mat = random.choice(MAT_PACKETS)
        packet = create_packet(f"Packet_{i}", start_frame, anim_coll, packet_mat)
        animate_packet_route(packet, start_frame, start_coord, end_coord, anim_end_frame)

    # --- WIDE ORBITING CAMERA RIG ---
    print("Setting up wide, orbiting camera...")
    scene_coll = bpy.context.scene.collection
    center_of_grid = get_core_position((GRID_SIZE_X - 1) / 2.0, (GRID_SIZE_Y - 1) / 2.0, (GRID_SIZE_Z - 1) / 2.0)
    pivot = bpy.data.objects.new("CameraPivot", None)
    pivot.location = center_of_grid
    scene_coll.objects.link(pivot)
    camera_arm = bpy.data.objects.new("CameraArm", None)
    camera_arm.location = (GRID_SIZE_X * SPACING * 3.5, -GRID_SIZE_Y * SPACING * 3.5, GRID_SIZE_Z * SPACING * 0.8)
    scene_coll.objects.link(camera_arm)
    camera_arm.parent = pivot
    cam_data = bpy.data.cameras.new('Camera')
    camera = bpy.data.objects.new('Camera', cam_data)
    scene_coll.objects.link(camera)
    bpy.context.scene.camera = camera
    copy_loc_cam = camera.constraints.new(type='COPY_LOCATION')
    copy_loc_cam.target = camera_arm
    track_constraint = camera.constraints.new(type='TRACK_TO')
    track_constraint.target = pivot
    pivot.rotation_euler = (0, 0, 0)
    pivot.keyframe_insert(data_path="rotation_euler", frame=0)
    pivot.rotation_euler = (0, 0, 2 * math.pi)
    pivot.keyframe_insert(data_path="rotation_euler", frame=anim_end_frame)
    if pivot.animation_data and pivot.animation_data.action:
        fcurve = pivot.animation_data.action.fcurves.find('rotation_euler', index=2)
        if fcurve:
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = 'LINEAR'

    # --- Final Scene Setup ---
    print("Setting up lighting and render settings...")
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.01, 0.01, 0.015, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.5
    light_data = bpy.data.lights.new('Sun', type='SUN')
    light_data.energy = 50
    light = bpy.data.objects.new('Sun', light_data)
    light.location = (GRID_SIZE_X * SPACING, -GRID_SIZE_Y * SPACING, GRID_SIZE_Z * SPACING * 2)
    scene_coll.objects.link(light)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.eevee.use_bloom = True
    scene.eevee.bloom_threshold = 1.0
    scene.eevee.bloom_intensity = 0.08
    scene.eevee.bloom_radius = 7

    print("--- Scene Generation Finished Successfully ---")