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
parser.add_argument('--origin-xyz', dest='origin_xyz', action='store', 
                    default='0 0 0', type=str)
parser.add_argument('--rotation-axis', dest='rotation_axis', action='store', type=str)
parser.add_argument('--axis-angle', dest='angle', action='store', type=float)
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

o_arr = [float(f) for f in args.origin_xyz.split(" ")]

# rotation matrixes
# (https://en.wikipedia.org/wiki/Rotation_matrix#In_three_dimensions)
rot_mat = {
  'x': np.array([[1, 0, 0], [0, np.cos(args.angle), -np.sin(args.angle)], [0, np.sin(args.angle), np.cos(args.angle)]]),
  'y': np.array([[np.cos(args.angle), 0, np.sin(args.angle)], [0, 1, 0], [-np.sin(args.angle), 0, np.cos(args.angle)]]),
  'z': np.array([[np.cos(args.angle), -np.sin(args.angle), 0], [np.sin(args.angle), np.cos(args.angle), 0], [0, 0, 1]])
}

for pose in model.findall("./*/pose"): # change top-level pose elements
        arr   = [float(f) for f in pose.text.split(" ")]
        if args.rotation_axis == 'x':
          xyz = np.dot(rot_mat[args.rotation_axis],
                       np.array([[0,],
                                 [arr[1]-o_arr[1],],
                                 [arr[2]-o_arr[2],]]))

          arr[0] =   arr[0]+xyz[0][0]
          arr[1] = o_arr[1]+xyz[1][0]
          arr[2] = o_arr[2]+xyz[2][0]
          Re = transformations.euler_matrix(arr[3], arr[4], arr[5], 'rxyz')
          R = transformations.rotation_matrix(args.angle, [1, 0, 0])

        elif args.rotation_axis == 'y':
          xyz = np.dot(rot_mat[args.rotation_axis],
                       np.array([[arr[0]-o_arr[0],],
                                 [0,],
                                 [arr[2]-o_arr[2],]]))

          arr[0] = o_arr[0]+xyz[0][0]
          arr[1] =   arr[1]+xyz[1][0]
          arr[2] = o_arr[2]+xyz[2][0]
          Re = transformations.euler_matrix(arr[3]-np.pi/2, arr[4], arr[5], 'rxyz')
          R = transformations.rotation_matrix(args.angle, [0, 1, 0])

        elif args.rotation_axis == 'z':
          xyz = np.dot(rot_mat[args.rotation_axis],
                       np.array([[arr[0]-o_arr[0],],
                                 [arr[1]-o_arr[1],],
                                 [0,]]))

          arr[0] = o_arr[0]+xyz[0][0]
          arr[1] = o_arr[1]+xyz[1][0]
          arr[2] =   arr[2]+xyz[2][0]
          Re = transformations.euler_matrix(arr[3], arr[4], arr[5], 'rxyz')
          R = transformations.rotation_matrix(args.angle, [0, 0, 1])          

        M  = transformations.concatenate_matrices(Re, R)
        euler = transformations.euler_from_matrix(M, 'rxyz')
        arr[3] = euler[0]
        arr[4] = euler[1]
        arr[5] = euler[2]
        pose.text = " ".join([str(a) for a in arr])

tree.write(args.destination, xml_declaration=True, method="xml")