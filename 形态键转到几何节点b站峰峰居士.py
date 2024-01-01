import bpy

# --------------------------------------初始化-------------------------------------

key_list = []

# ------------------------------------形态键转属性-----------------------------------
data = bpy.context.object.data
keys = data.shape_keys.key_blocks

for i,key in enumerate(keys):
    if i !=0:
        key_list.append(key.name)
        key_att = data.attributes.new(key.name,'FLOAT_VECTOR','POINT')
        for index in range(len(key.data)):
            key_att.data[index].vector = key.data[index].co
            
# ------------------------------------创建变形节点组-----------------------------------

gn = bpy.data.node_groups.new(".Deform",'GeometryNodeTree')
gn_input = gn.nodes.new('NodeGroupInput')
gn_output = gn.nodes.new('NodeGroupOutput')


gn.inputs.new('NodeSocketGeometry','Geometry')
gn.inputs.new('NodeSocketString','String')
gn.inputs.new('NodeSocketFloat','Float')
gn.outputs.new('NodeSocketGeometry','Geometry')


set_pos = gn.nodes.new('GeometryNodeSetPosition')
input_pos = gn.nodes.new('GeometryNodeInputNamedAttribute')
name_att = gn.nodes.new('GeometryNodeInputNamedAttribute')
v_math = gn.nodes.new('ShaderNodeVectorMath')
v_math2 = gn.nodes.new('ShaderNodeVectorMath')


gn_output.location = (1000,0)
gn_input.location = (-300,0)
set_pos.location = (800,0)
name_att.location = (0,-80)
input_pos.location = (0,-200)

v_math.location = (200,0)
v_math2.location = (500,0)

v_math.operation = 'SUBTRACT'
v_math2.operation = 'SCALE'
name_att.data_type = 'FLOAT_VECTOR'
input_pos.data_type = 'FLOAT_VECTOR'
input_pos.inputs['Name'].default_value = 'Basis'

gn.links.new(name_att.inputs['Name'],gn_input.outputs['String'])
gn.links.new(v_math.inputs[0],name_att.outputs['Attribute'])
gn.links.new(v_math.inputs[1],input_pos.outputs['Attribute'])
gn.links.new(v_math2.inputs[0],v_math.outputs['Vector'])
gn.links.new(v_math2.inputs['Scale'],gn_input.outputs['Float'])
gn.links.new(set_pos.inputs['Geometry'],gn_input.outputs['Geometry'])
gn.links.new(set_pos.inputs['Offset'],v_math2.outputs['Vector'])
gn.links.new(gn_output.inputs['Geometry'],set_pos.outputs['Geometry'])

# --------------------------------创建形态键几何节点修改器--------------------------------------------

gn = bpy.data.node_groups.new("Shape Keys",'GeometryNodeTree')
gn_input = gn.nodes.new('NodeGroupInput')
gn_output = gn.nodes.new('NodeGroupOutput')
gn.inputs.new('NodeSocketGeometry','Geometry')
gn.outputs.new('NodeSocketGeometry','Geometry')
gn_input.location = (-200,0)
gn_output.location = (200*(len(key_list)+2),0)

set_att = gn.nodes.new('GeometryNodeStoreNamedAttribute')
input_pos = gn.nodes.new('GeometryNodeInputPosition')

set_att.inputs['Name'].default_value = 'Basis'
set_att.data_type = 'FLOAT_VECTOR'

set_att.location = (200,0)
input_pos.location = (0,-150)

gn.links.new(set_att.inputs['Geometry'],gn_input.outputs['Geometry'])
gn.links.new(set_att.inputs[2],input_pos.outputs['Position'])

modif_node = bpy.context.object.modifiers.new("ShapeKeys",'NODES')

for i,name in enumerate(key_list,1):
    new_node = gn.nodes.new('GeometryNodeGroup')
    new_node.node_tree = bpy.data.node_groups[".Deform"]
    new_node.location = (200*(i+1),0)
    new_node.inputs['String'].default_value = name
    gn.inputs.new('NodeSocketFloat',name)
    gn.inputs[i].min_value = 0
    gn.inputs[i].max_value = 1
    new_node.name = name
    
    if i == 1:
        gn.links.new(gn.nodes[name].inputs['Geometry'],set_att.outputs['Geometry'])
    else:
        gn.links.new(gn.nodes[name].inputs['Geometry'],gn.nodes[key_list[i-2]].outputs['Geometry'])
        
    gn.links.new(gn.nodes[name].inputs['Float'],gn_input.outputs[i])
    gn.links.new(gn_output.inputs['Geometry'],gn.nodes[name].outputs['Geometry'])


modif_node.node_group = gn



