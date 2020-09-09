"""
Put this file in the /path/to/blender/your-version/scripts/addons to work.
"""

import os
import math
from random import randint

import bpy
from bpy import context as C
from bpy import data as D
from bpy import ops as OPS


def clear_scene():
    """ Clear all objects and related data. """
    for camera in D.cameras:
        D.cameras.remove(camera)
    for light in D.lights:
        D.lights.remove(light)
    for action in D.actions:
        D.actions.remove(action)
    for mesh in D.meshes:
        D.meshes.remove(mesh)
    for material in D.materials:
        D.materials.remove(material)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    

def add_light(name='sun', type='SUN', size=1, loc=(0,0,0), energy=4):
    """ Add lighting. """
    OPS.object.light_add(type=type, 
                         radius=size, 
                         align='WORLD', 
                         location=loc)
    C.active_object.name = name
    D.objects[name].data.energy = energy


def add_camera(name='camera', loc=(0,0,0), rot=(0,0,0)):
    """ Add a camera. """
    OPS.object.camera_add(enter_editmode=False, 
                          align='VIEW', 
                          location=loc, 
                          rotation=rot)
    C.active_object.name = name
    C.scene.camera = C.active_object


def load_materials(mat_path=None):
    """
    Load all available materials.
    Hardcoded here, but will be saved in files.
    """
#   materials = json.load(mat_path)
    materials = {
        'Glossy BSDF': {
            'type': 'ShaderNodeBsdfGlossy',
            'color': (0.257, 0.905, 0.779, 1.000),
        },
        'Toon BSDF': {
            'type': 'ShaderNodeBsdfToon',
            'color': (0.232, 0.142, 0.800, 1.000),
        },
        'Glass BSDF': {
            'type': 'ShaderNodeBsdfGlass',
            'color': (0.985, 0.108, 0.559, 1.000),
        }, 
    }
    for name in materials.keys():
        if name not in D.materials.keys():
            new_mat = D.materials.new(name=name)
            new_mat.use_nodes = True
            nodes = new_mat.node_tree.nodes
            mat_out = nodes.get('Material Output')
            mat_in = nodes.new(type=materials[name]['type'])
            mat_in.inputs[0].default_value = materials[name]['color']
            links = new_mat.node_tree.links
            new_link = links.new(mat_in.outputs[0], mat_out.inputs[0])


def gen_moves(space=(10, 10, 10), center=(0, 0, 6), n=3, points=3):
    """ Generate movement points in a certain space. """
    moves = []
    for i in range(n):
        temp = []
        for j in range(points):
            temp.append((randint(center[0]-space[0]/2, center[0]+space[0]/2), 
                         randint(center[1]-space[1]/2, center[1]+space[1]/2), 
                         randint(center[2]-space[2]/2, center[2]+space[2]/2)))
        moves.append(temp)
    return moves


def add_material(obj=None, name=None):
    """ Add an existing material to an object. """
    if name in D.materials.keys():
        obj.data.materials.clear()
        obj.data.materials.append(D.materials[name])
    else:
        print("Wrong material name. ")

   
def add_plane(name='plane',size=200, mat_name='', loc=(0,0,0), rot=(0,0,0)):
    """ Add a plane. """
    OPS.mesh.primitive_plane_add(size=size, 
                                 calc_uvs=True, 
                                 enter_editmode=False, 
                                 align='WORLD', 
                                 location=loc, 
                                 rotation=rot)
    C.active_object.name = name
    add_material(C.active_object, mat_name)


def add_cube(name='cube', size=2, loc=(0,0,0), mat_name=''):
    """ Add a cube. """
    OPS.mesh.primitive_cube_add(size=size, 
                                calc_uvs=True, 
                                enter_editmode=False, 
                                align='WORLD', 
                                location=loc, 
                                rotation=(0, 0, 0))
    C.active_object.name = name
    add_material(C.active_object, mat_name)


def add_uv_sphere(name='sphere', size=2, location=(2,2,2), mat_name=''):
    """ Add a sphere. """
    OPS.mesh.primitive_uv_sphere_add(segments=64, 
                                     ring_count=32, 
                                     radius=size, 
                                     calc_uvs=True, 
                                     enter_editmode=False, 
                                     align='WORLD', 
                                     location=location, 
                                     rotation=(0, 0, 0))
    OPS.object.modifier_add(type='SUBSURF')
    C.object.modifiers["Subdivision"].levels = 3
    C.object.modifiers["Subdivision"].render_levels = 3
#    OPS.object.modifier_apply(apply_as='DATA', modifier="Subdivision")
    OPS.object.shade_smooth()
    C.active_object.name = name
    add_material(C.active_object, mat_name)
    

def add_cylinder(name='cylinder', r=1, h=2, location=(1,1,1), mat_name=''):
    """ Add a cylinder. """
    OPS.mesh.primitive_cylinder_add(vertices=64, 
                                    radius=r, 
                                    depth=h, 
                                    end_fill_type='NGON', 
                                    calc_uvs=True, 
                                    enter_editmode=False, 
                                    align='WORLD', 
                                    location=location, 
                                    rotation=(0, 0, 0))
    C.active_object.name = name
    add_material(C.active_object, mat_name)


def add_movement(obj=None, track=None):
    """ Add dynamics and link to key frames. """
    track = track.copy()
    track.insert(0, tuple(obj.location))
    frame = 0
    for pos in track:
        C.scene.frame_set(frame)
        obj.location = pos
        obj.rotation_euler[0] += math.radians(90)
        obj.keyframe_insert(data_path='location', index=-1)
        obj.keyframe_insert(data_path='rotation_euler', index=-1)
        frame += 30


def render_setting(length=None):
    """ This function might be loaded from a config file. """
    C.scene.render.engine = 'CYCLES'
    C.scene.cycles.device = 'GPU'
    C.scene.render.resolution_x = 512
    C.scene.render.resolution_y = 512
#    C.scene.render.resolution_x = 960
#    C.scene.render.resolution_y = 540
#    C.scene.render.resolution_x = 1920
#    C.scene.render.resolution_y = 1080

    C.scene.cycles.samples = 256
    C.scene.render.tile_x = 32
    C.scene.render.tile_y = 32
#    C.scene.use_denoising = True

    C.scene.render.fps = 30
    C.scene.render.image_settings.file_format = 'FFMPEG'
#    C.scene.render.ffmpeg.format = 'MPEG4'
    C.scene.render.ffmpeg.format = 'AVI'
    C.scene.frame_end = C.scene.render.fps * length


def prepare_scene(bg_color=None, length=None):
    """ Prepare scene. """
    load_materials()
    render_setting(length)
    add_light('sun', 'SUN', 2, loc=(0,-50,50), energy=2.0)
    D.objects['sun'].rotation_euler=(math.radians(45), 0, 0)
    add_light('area', 'AREA', 100, loc=(0,0,50), energy=10000)
    add_camera('camera',
               loc=(50,-50,50),
               rot=(math.radians(60),0,math.radians(45)))
    add_plane('plane1', 100, bg_color)
    add_plane('plane2', 100, bg_color, loc=(0,50,0), rot=(math.radians(90),0,0))
    add_plane('plane3', 100, bg_color, loc=(50,0,0), rot=(0,math.radians(90),0))
    add_plane('plane4', 100, bg_color, loc=(-50,0,0),rot=(0,math.radians(90),0))


def render(path=None, obj_name='', color='', bg_color='', move=''):
    """ Render demo. """
    clear_scene()
    prepare_scene(bg_color, len(move))
    
    if obj_name == 'cube':
        add_cube('cube', 2, (1,1,1), color)
        add_movement(D.objects['cube'], move)
    elif obj_name == 'sphere':
        add_uv_sphere('sphere', 1, (1,1,1), color)
        add_movement(D.objects['sphere'], move)
    elif obj_name == 'cylinder':
        add_cylinder('cylinder', 1, 2, (1,1,1), color)
        add_movement(D.objects['cylinder'], move)
    
    if path:
        C.scene.render.filepath = path
#        OPS.render.render(animation=True, use_viewport=True)
        OPS.render.render(animation=True)


def render_group(group_dir):
    if not os.path.exists(group_dir):
        os.mkdir(group_dir)
    # This should will be loaded from files.
    group_config = {
        'shapes': ['cube', 'sphere', 'cylinder'],
        'moves': gen_moves(),
        'colors': ['Glass BSDF', 'Glossy BSDF', 'Toon BSDF'],
        'bg_colors': ['Glass BSDF', 'Glossy BSDF', 'Toon BSDF']
    }
    group = {}
    group['center'] = {
        'shape': group_config['shapes'].pop(
            randint(0, len(group_config['shapes'])-1)),
        'color': group_config['colors'].pop(
            randint(0, len(group_config['colors'])-1)),
        'bg_color': group_config['bg_colors'].pop(
            randint(0, len(group_config['colors'])-1)),
        'move': group_config['moves'].pop(
            randint(0, len(group_config['moves'])-1))
    }
    group['comp1'] = {
        'shape': group['center']['shape'],
        'color': group_config['colors'][randint(0, len(group_config['colors'])-1)],
        'bg_color': group_config['bg_colors'][randint(0, len(group_config['bg_colors'])-1)],
        'move': group_config['moves'][randint(0, len(group_config['moves'])-1)]
    }
    group['comp2'] = {
        'shape': group_config['shapes'][randint(0, len(group_config['shapes'])-1)],
        'color': group['center']['color'],
        'bg_color': group_config['bg_colors'][randint(0, len(group_config['bg_colors'])-1)],
        'move': group_config['moves'][randint(0, len(group_config['moves'])-1)]
    }
    group['comp3'] = {
        'shape': group_config['shapes'][randint(0, len(group_config['shapes'])-1)],
        'color': group_config['colors'][randint(0, len(group_config['colors'])-1)],
        'bg_color': group['center']['bg_color'],
        'move': group_config['moves'][randint(0, len(group_config['moves'])-1)]
    }
    group['comp4'] = {
        'shape': group_config['shapes'][randint(0, len(group_config['shapes'])-1)],
        'color': group_config['colors'][randint(0, len(group_config['colors'])-1)],
        'bg_color': group_config['bg_colors'][randint(0, len(group_config['bg_colors'])-1)],
        'move': group['center']['move']
    }
    
    for i in group.keys():
        path = os.path.join(group_dir, i+'.avi')
        render(
            path=path, 
            obj_name=group[i]['shape'], 
            color=group[i]['color'], 
            bg_color=group[i]['bg_color'], 
            move=group[i]['move'])
