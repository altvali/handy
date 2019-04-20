import xml.etree.ElementTree as ET
import argparse
import numpy

# Command line parameters
parser = argparse.ArgumentParser(description='Translates and rotates an SDF ')
parser.add_argument('--source', dest='source', action='store', type=str)
parser.add_argument('--destination', dest='destination', action='store', type=str)
parser.add_argument('--sdf-model-name', dest='sdf_model_name', action='store', 
                    type=str)
parser.add_argument('--origin-xyz', dest='origin_xyz', action='store', 
                    default='0 0 0', type=str)
parser.add_argument('--translation-xyz', dest='translation_xyz', action='store',
                    default='0 0 0', type=str)
parser.add_argument('--rotation-rpy', dest='rotation_rpy', action='store',
                    .0default='0 0 0', type=str)
args = parser.parse_args()

tree = ET.parse(args.source)
root = tree.getroot()

# assumes root is <sdf>, with a child <world>, with one of <world>'s children
# being the sdf_model_name, in order to avoid searching for it recursively
assert root.tag == 'sdf'
assert len(root) == 1
assert root[0].tag == 'world'

model = root[0].find("./model[@name='%s']" % (args.sdf_model_name,))
assert model is not None

t_arr = [float(f) for f in args.translation_xyz.split(" ")]
r_arr = [float(f) for f in args.rotation_rpy.split(" ")]

# rotation matrixes
# (https://en.wikipedia.org/wiki/Rotation_matrix#In_three_dimensions)
mx = np.array([[ 1,                0,                 0],
               [ 0,                np.cos(r_arr[0]), -np.sin(r_arr[0])],
               [ 0,                np.sin(r_arr[0]),  np.cos(r_arr[0])]])

my = np.array([[ np.cos(r_arr[1],  0,                 np.sin(r_arr[1])],
               [ 0,                1,                 0],
               [-np.sin(r_arr[1]), 0,                 np.cos(r_arr[1])]])

mz = np.array([[ np.cos(r_arr[2]), -np.sin(r_arr[2]),  0],
               [ np.sin(r_arr[2]),  np.cos(r_arr[2]),  0],
               [ 0,                 0,                 1]])

for pose in link.findall("./*/pose"): # change top-level pose elements
        arr   = [float(f) for f in pose.text.split(" ")]
        
        # translate
        arr[0] += t_arr[0]
        arr[1] += t_arr[1]
        arr[2] += t_arr[2]
        
        # rotate        
        elem_xyz = np.array([[arr[0],],
                        [arr[1],],
                        [arr[2],]])
        elem_xyz = np.dot(mx, elem_xyz)
        elem_xyz = np.dot(my, elem_xyz)
        elem_xyz = np.dot(mz, elem_xyz)
        arr[:3] = elem_xyz[:3]
        arr[3] += r_arr[0]
        arr[4] += r_arr[1]
        arr[5] += r_arr[2]
        pose.text = " ".join([str(a) for a in arr])

tree.write(args.destination, xml_declaration=True, method="xml")