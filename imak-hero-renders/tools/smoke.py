import bpy, time
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = 64
sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 960, 540
bpy.ops.mesh.primitive_monkey_add(); bpy.ops.object.shade_smooth()
bpy.ops.mesh.primitive_plane_add(size=10, location=(0,0,-1))
bpy.ops.object.light_add(type='AREA', location=(2,-2,4)); bpy.context.object.data.energy=800
bpy.ops.object.camera_add(location=(4,-4,3), rotation=(1.1,0,0.78)); sc.camera = bpy.context.object
sc.render.filepath = 'preview/smoke.png'
t=time.time(); bpy.ops.render.render(write_still=True); print('render s', round(time.time()-t,1))
print('denoisers', [e.identifier for e in sc.cycles.bl_rna.properties['denoiser'].enum_items])
