import matplotlib as mpl
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec

from TritonOA.env import env

def plot_field(pos, pressure, ssp, bdy, FREQ, cInt, RMAX, show=False):
    fig = plt.figure(figsize=(12,9))
    gs = gridspec.GridSpec(nrows=1, ncols=2, wspace=0, width_ratios=[1, 6])
    ax1 = fig.add_subplot(gs[0])
    ax1 = plt.subplot(1, 2, 1)
    plt.plot(CP, Z)
    plt.plot(CP[[0, -1]], [SD, SD], 'r')
    ax1.invert_yaxis()
    plt.ylim(ZB,0)
    plt.xlabel("C (m/s)")
    plt.ylabel("Depth (m)")
    plt.text(CP[0]-15, SD, "Source", va="center")

    ax2 = fig.add_subplot(gs[1])
    vmin = -40
    vmax = 0
    plt.contourf(Pos1.r.range, Pos1.r.depth, (pressure[0, 0, :, :]), levels=levs, cmap="jet", vmin=vmin, vmax=vmax)
    # plt.imshow(pressure[0, 0, :, :])
    plt.gca().invert_yaxis()
    plt.yticks([])
    plt.xlabel("Range (m)")
    # plt.ylabel("Depth (m)")
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    # cbar = plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap_spec))
    cbar = plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap="jet"))
    cbar.set_label("SPL (dB)")
    plt.scatter(0, SD, s=500, c="r", marker=".")

    plt.title(f"Freq = {FREQ} Hz        SD = {SD} m")

    if show:
        plt.show()
    else:
        plt.close()
    return fig
