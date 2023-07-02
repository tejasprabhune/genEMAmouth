import numpy as np
import matplotlib.pyplot as plt

ema_data = np.load('TongueMocapData/ema/npy/0899.npy', allow_pickle=True)
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

print(pos_seq['td'][1])

get_col = lambda dim : [pos_seq['td'][i][dim] for i in range(0, len(pos_seq['td']))]
xs, ys, zs = get_col(0), get_col(1), get_col(2)
print(xs)

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

ax.scatter(xs, ys, zs, marker = m)
plt.show()