# Generate Avatar from EMA

[Paper used for data](https://openaccess.thecvf.com/content/CVPR2022/papers/Medina_Speech_Driven_Tongue_Animation_CVPR_2022_paper.pdf)

## Using the Maya Script

Maya uses their own Python environment which is located as `mayapy` in 
`C:\Program Files\Autodesk\Maya<VersionNumber>\bin\` or 
`/usr/autodesk/Maya<VersionNumber>/bin/` (Linux).

Adding this to `PATH` then allows us to do `mayapy <py_file>.py`.

The second setup step needed is to install `numpy` to this separate `mayapy`
instance by running `mayapy -m pip install numpy`

The reason this is needed is to use the `maya.cmds` library, where we are able
to generate whole Maya ASCII files and polygons within those files.