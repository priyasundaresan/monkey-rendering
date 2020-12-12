import bpy
import os
import json
import time
import bpy, bpy_extras
from math import *
from mathutils import *
import random
import numpy as np
from random import sample
import bmesh

'''Usage: blender -b -P render.py'''

def clear_scene():
    '''Clear existing objects in scene'''
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)
    for block in bpy.data.textures:
        if block.users == 0:
            bpy.data.textures.remove(block)
    for block in bpy.data.images:
        if block.users == 0:
            bpy.data.images.remove(block)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def add_camera_light():
    bpy.ops.object.light_add(type='SUN', radius=1, location=(0,0,0))
    bpy.ops.object.camera_add(location=(0,0,11), rotation=(0,0,0))
    bpy.context.scene.camera = bpy.context.object

def set_render_settings(engine, render_size, generate_masks=True):
    # Set rendering engine, dimensions, colorspace, images settings
    if os.path.exists("./images"):
        os.system('rm -r ./images')
    os.makedirs('./images')
    if os.path.exists("./annots"):
        os.system('rm -r ./annots')
    os.makedirs('./annots')
    scene = bpy.context.scene
    scene.render.resolution_percentage = 100
    scene.render.engine = engine
    render_width, render_height = render_size
    scene.render.resolution_x = render_width
    scene.render.resolution_y = render_height
    scene.use_nodes = True
    scene.render.image_settings.file_format='JPEG'
    if engine == 'BLENDER_WORKBENCH':
        scene.render.image_settings.color_mode = 'RGB'
        scene.display_settings.display_device = 'None'
        scene.sequencer_colorspace_settings.name = 'XYZ'
    elif engine == "BLENDER_EEVEE":
        scene.view_settings.view_transform = 'Raw'
        scene.eevee.taa_samples = 1
        scene.eevee.taa_render_samples = 1
    elif engine == 'CYCLES':
        scene.render.image_settings.file_format='JPEG'
        #scene.cycles.samples = 50
        scene.cycles.samples = 10
        scene.view_settings.view_transform = 'Standard'
        scene.cycles.max_bounces = 1
        scene.cycles.min_bounces = 1
        scene.cycles.glossy_bounces = 1
        scene.cycles.transmission_bounces = 1
        scene.cycles.volume_bounces = 1
        scene.cycles.transparent_max_bounces = 1
        scene.cycles.transparent_min_bounces = 1
        scene.view_layers["View Layer"].use_pass_object_index = True
        scene.render.tile_x = 16
        scene.render.tile_y = 16

def render(episode):
    bpy.context.scene.render.filepath = "./images/%05d.jpg"%episode
    bpy.ops.render.render(write_still=True)
    scene = bpy.context.scene
    tree = bpy.context.scene.node_tree
    links = tree.links
    render_node = tree.nodes["Render Layers"]
    id_mask_node = tree.nodes.new(type="CompositorNodeIDMask")
    id_mask_node.use_antialiasing = True
    id_mask_node.index = 1
    composite = tree.nodes.new(type = "CompositorNodeComposite")
    links.new(render_node.outputs['IndexOB'], id_mask_node.inputs["ID value"])
    links.new(id_mask_node.outputs[0], composite.inputs["Image"])
    scene.render.filepath = 'masks/%05d.jpg'%episode
    bpy.ops.render.render(write_still=True)
    for node in tree.nodes:
        if node.name != "Render Layers":
            tree.nodes.remove(node)

def annotate(obj, episode, num_annotations, render_size):
    scene = bpy.context.scene
    vertices = [obj.matrix_world @ v.co for v in list(obj.data.vertices)]
    vertices = vertices[::25]
    pixels = []
    for i in range(len(vertices)):
        v = vertices[i]
        camera_coord = bpy_extras.object_utils.world_to_camera_view(scene, bpy.context.scene.camera, v)
        pixel = [round(camera_coord.x * render_size[0]), round(render_size[1] - camera_coord.y * render_size[1])]
        pixels.append(pixel)
    np.save('annots/%05d.npy'%episode, np.array(pixels))

def generate_face():
    bpy.ops.import_mesh.ply(filepath="face/11091_FemaleHead_v4.ply")
    bpy.ops.object.editmode_toggle()
    # bpy.ops.mesh.subdivide(number_cuts=3) # Tune this number for detail
    bpy.ops.object.modifier_add(type='SUBSURF')
    bpy.context.object.modifiers["Subdivision"].levels=3 # Smooths the cloth so it doesn't look blocky
    bpy.ops.object.editmode_toggle()
    obj = bpy.context.object
    obj.pass_index = 1
    return obj

def generate_state(obj):
    dx = 0.2 + np.random.uniform(0,0.4,1)*random.choice((-1,1))
    dy = np.random.uniform(-2,-1.3,1)*random.choice((0,1))
    dz = np.random.uniform(0.4,0.8,1)
    obj.location = (dx,dy,dz)
    scale_range = np.random.uniform(0.16, 0.18)
    obj.scale = [scale_range]*3
    obj.rotation_euler = (random.uniform(0, np.pi/4), \
                          random.uniform(-np.pi/4, np.pi/4), \
                          random.uniform(-np.pi/4, np.pi/4))
    print(obj.rotation_euler)
    return obj.location, obj.rotation_euler

def generate_dataset(iters=1):
    render_size = (240,240)
    set_render_settings('CYCLES', render_size)
    clear_scene()
    add_camera_light()
    num_annotations = 3
    # monkey = generate_monkey()
    monkey = generate_face()
    for episode in range(iters):
        generate_state(monkey)
        render(episode)
        annotate(monkey, episode, num_annotations, render_size)

if __name__ == '__main__':
    generate_dataset(2000)
