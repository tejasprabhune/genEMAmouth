import maya.standalone
maya.standalone.initialize("Python")
import maya.cmds as cmds
import numpy as np
import argparse
import os
from mtoa.cmds.arnoldRender import arnoldRender


parser = argparse.ArgumentParser("Generates and renders a mouth rig from " +
                                 "input data")
parser.add_argument("--ema_data", 
                    default=r"../TongueMocapData/ema/npy/0899.npy",
                    help="input EMA data location (.npy file) used to build rig")
parser.add_argument("--input_wav",
                    default=r"../TongueMocapData/wav/0899.wav")
parser.add_argument("--output_mb",
                    default=r"./0899.mb",
                    help="location to output maya scene file")
args = parser.parse_args()
args.output_mb = os.path.abspath(args.output_mb)

ema_data = np.load(args.ema_data, allow_pickle=True)
pos_seq = dict()
pos_seq['td'] = ema_data[:, 0:3]    # tongue dorsum
pos_seq['tb'] = ema_data[:, 3:6]    # tongue blade
pos_seq['br'] = ema_data[:, 6:9]    # tongue blade - right
pos_seq['bl'] = ema_data[:, 9:12]   # tongue blade - left
pos_seq['tt'] = ema_data[:, 12:15]  # tongue tip
pos_seq['ul'] = ema_data[:, 15:18]  # upper lip
pos_seq['lc'] = ema_data[:, 18:21]  # lip corner - right
pos_seq['ll'] = ema_data[:, 21:24]  # lower lip
pos_seq['li'] = ema_data[:, 24:27]  # jaw incisor
pos_seq['lj'] = ema_data[:, 27:30]  # jaw parasagittal

# Extracts x, y, or z column based on 0, 1, or 2 dim for any given part in pos_seq
get_col = lambda part, dim : [pos_seq[part][i][dim] for i in range(0, len(pos_seq[part]))]


# Demeaning process: Parts are not necessarily centered at the origin, so we 
# use demeaning to center based on the total xs, ys, and zs.
parts = ["ll", "li", "lj", "tt", "br", "bl", "tb", "td", "lc", "ul"]
sum_xyz = [0, 0, 0]
count_xyz = [0, 0, 0]
max_xyz = [0, 0, 0]

for part in parts:
    xs = get_col(part, 0)
    ys = get_col(part, 1)
    zs = get_col(part, 2)
    xyz = [xs, ys, zs]

    for i in range(0, 3):
        sum_xyz[i] += (sum(xyz[i]))
        count_xyz[i] += (len(xyz[i]))
        if (max_xyz[i] < max(xyz[i])):
            max_xyz[i] = max(xyz[i])

means = [0, 0, 0]
for i in range(0, 3):
    means[i] = sum_xyz[i] / count_xyz[i]

for part in parts:
    for i in range(0, len(pos_seq[part])):
        pos_seq[part][i] = [(pos_seq[part][i][0] - means[0]), 
                            (pos_seq[part][i][1] - means[1]), 
                            (pos_seq[part][i][2] - means[2])]

def get_formatted_keys(part: str) -> list:
    """
    Shifts coordinates to match Maya coordinate style.

    Tongue Mocap Data orients coordinates such that x describes back to front, 
    y describes right to left, and z describes bottom to top. Maya orients x as
    right to left, y going bottom to top, and z going back to front. As such,
    we reorient (x, y, z) to (y, z, x) when using in Maya scripting.

    Additionally, we divide each coordinate by 2 to reduce the overall scale of
    the scene.

    Args:
        part (str): data keyword for body part

    Returns:
        keyframes (list): list of lists containing each keyframe for this part
        as key, x, y, z in Maya format
    
    """
    keyframes = []
    xs, ys, zs = get_col(part, 0), get_col(part, 1), get_col(part, 2)

    for i in range(0, len(xs)):
        keyframes.append([i, ys[i] / 2, zs[i] / 2, xs[i] / 2])

    return keyframes

ema_data = {}

for part in parts:
    ema_data[part] = get_formatted_keys(part)

### Maya Scene Setup
cmds.workspace("temp", n=True)
cmds.workspace(dir="./")

cmds.file(newFile=True, force=True)

cmds.select(all=True)

cmds.delete()

cmds.currentUnit(t="palf")

cmds.polyPlane(sx=1, sy=1, n="tonguePlane")

cmds.polySplit( ip=[(1, 0), (3, 1)] )
cmds.polySplit( ip=[(2, 0), (3, 0)] )

cmds.rotate(0, 45, 0)

sel = cmds.ls(sl=True, o=True)[0]
sel_vtx = cmds.ls('{}.vtx[:]'.format(sel), fl=True)

tongue_parts = ['tt', 'bl', 'br', 'td', 'tb']

for i in range(0, len(tongue_parts)):
    cmds.select(sel_vtx[i])
    cmds.cluster(name=tongue_parts[i])
    
def clear_keys(part):
    startTime = cmds.playbackOptions(query=True, minTime=True)
    endTime = cmds.playbackOptions(query=True, maxTime=True)

    cmds.cutKey(part, time=(startTime, endTime), attribute='translateX')
    cmds.cutKey(part, time=(startTime, endTime), attribute='translateY')
    cmds.cutKey(part, time=(startTime, endTime), attribute='translateZ')   

def keyYTranslate(part, key, y):
    cmds.setKeyframe(part, time=key, attribute='translateY', value=y)

def keyXTranslate(part, key, x):
    cmds.setKeyframe(part, time=key, attribute='translateX', value=x)
    
def keyZTranslate(part, key, z):
    cmds.setKeyframe(part, time=key, attribute='translateZ', value=z)

def animateX(part, keys):
    for key in keys:
        keyXTranslate(part, key[0], key[1])

def animateY(part, keys):
    for key in keys:
        keyYTranslate(part, key[0], key[2])
        
def animateZ(part, keys):
    for key in keys:
        keyZTranslate(part, key[0], key[3])
        
def animateXYZ(part, keys):
    animateX(part, keys)
    animateY(part, keys)
    animateZ(part, keys)

cmds.file("../tongue.mb", i=True)

for part in tongue_parts:
    clear_keys(part + "Handle")
    animateXYZ(part + "Handle", ema_data[part])
    cmds.parentConstraint(part + "Handle", "tongue_" + part, mo=True)

clear_keys("lowerHandle")
lj_coords = [[x[i] - ema_data["lj"][0][i] for i in range(0, len(x))] for x in ema_data["lj"]]
animateY("lowerHandle", lj_coords)


#for filename in os.listdir("."):
#    os.rename(filename, filename[0:-6] + ".exr")
cmds.setAttr("cameraShape2.renderable", True)
cmds.setAttr("defaultRenderGlobals.currentRenderer", "mayaHardware2", type="string")
cmds.setAttr("defaultResolution.width", 1920)
cmds.setAttr("defaultResolution.height", 1080)

cmds.hide("tonguePlane")
for i in range(0, 250):
    cmds.currentTime(i)
    cmds.setAttr("defaultRenderGlobals.imageFilePrefix", f"{i}", type="string")
    cmds.ogsRender(cam="camera2")
    #arnoldRender(960, 540, True, True,'camera2', ' -layer defaultRenderLayer')

cmds.file(rename=args.output_mb)
cmds.file(save=True, type='mayaBinary', force=True)

os.system("ffmpeg -f image2 -r 50 -i C:/Users/tejas/Documents/maya/projects/images/camera2/%01d.png -vcodec mpeg4 -y -vb 40M ./" + f"{args.ema_data[0:-4]}.mp4")
os.system(f"ffmpeg -i {args.ema_data[0:-4]}.mp4 -i {args.input_wav} -c copy -c:a aac output.mp4")