import xml.etree.ElementTree as ET
import argparse
import numpy as np

import xml.etree.ElementTree as ET
import argparse
import numpy as np
import transformations

# Command line parameters
parser = argparse.ArgumentParser(description='Rotates an SDF on a given axis determined by a point')
parser.add_argument('--source', dest='source', action='store', type=str)
parser.add_argument('--destination', dest='destination', action='store', type=str)
parser.add_argument('--sdf-model-name', dest='sdf_model_name', action='store', 
                    type=str)
parser.add_argument('--translate-xyz', dest='translate_xyz', action='store', 
                    default='0 0 0', type=str)
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

t_arr = [float(f) for f in args.translate_xyz.split(" ")]

for pose in model.findall("./*/pose"): # change top-level pose elements
    arr = [float(f) for f in pose.text.split(" ")]
    arr[0] += t_arr[0]
    arr[1] += t_arr[1]
    arr[2] += t_arr[2]
    pose.text = " ".join([str(a) for a in arr])

tree.write(args.destination, xml_declaration=True, method="xml")