import matplotlib as mpl
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

# def plot_field(pos, pressure, ssp, bdy, FREQ, cInt, RMAX, show=False):
#     fig = plt.figure(figsize=(12,9))
#     gs = gridspec.GridSpec(nrows=1, ncols=2, wspace=0, width_ratios=[1, 6])
#     ax1 = fig.add_subplot(gs[0])
#     ax1 = plt.subplot(1, 2, 1)
#     plt.plot(CP, Z)
#     plt.plot(CP[[0, -1]], [SD, SD], 'r')
#     ax1.invert_yaxis()
#     plt.ylim(ZB,0)
#     plt.xlabel("C (m/s)")
#     plt.ylabel("Depth (m)")
#     plt.text(CP[0]-15, SD, "Source", va="center")
#
#     ax2 = fig.add_subplot(gs[1])
#     vmin = -40
#     vmax = 0
#     plt.contourf(Pos1.r.range, Pos1.r.depth, (pressure[0, 0, :, :]), levels=levs, cmap="jet", vmin=vmin, vmax=vmax)
#     # plt.imshow(pressure[0, 0, :, :])
#     plt.gca().invert_yaxis()
#     plt.yticks([])
#     plt.xlabel("Range (m)")
#     # plt.ylabel("Depth (m)")
#     norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
#     # cbar = plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap_spec))
#     cbar = plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap="jet"))
#     cbar.set_label("SPL (dB)")
#     plt.scatter(0, SD, s=500, c="r", marker=".")
#
#     plt.title(f"Freq = {FREQ} Hz        SD = {SD} m")
#
#     if show:
#         plt.show()
#     else:
#         plt.close()
#     return fig

def plot_TL(pressure, pos, parameters, show=True):
    CP = parameters.get('CP')
    Z = parameters.get('Z')
    ZB = parameters.get('ZB')
    SD = parameters.get('SD')
    FREQ = parameters.get('FREQ')

    logpressure = 10 * np.log10(pressure / np.max(pressure))
    levs = np.linspace(np.min(logpressure), np.max(logpressure), 40)

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
    plt.contourf(pos.r.range, pos.r.depth, (logpressure[0, 0, :, :]), levels=levs, cmap="jet", vmin=vmin, vmax=vmax)
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


def plot_MFP(
        asurf,
        rvec,
        zvec,
        vlim=[-10, 0],
        figsize=(12, 9),
        sr=None,
        sd=None,
        show=True
    ):

    nasurf = asurf / np.max(asurf)
    nasurfdb = 10 * np.log10(nasurf)

    fig = plt.figure(figsize=figsize)
    # Plot ambiguity surface:
    plt.imshow(
        nasurfdb,
        aspect='auto',
        extent=[min(rvec), max(rvec), min(zvec), max(zvec)],
        origin='lower',
        vmin=vlim[0],
        vmax=vlim[1],
        interpolation='none'
    )
    plt.gca().invert_yaxis()
    plt.xlabel("Range (m)")
    plt.ylabel("Depth (m)")
    cbar = plt.colorbar()
    cbar.set_label('Normalized Ambiguity Surface (dB)', rotation=270)

    # Plot MFP localization:
    sd_ind_est, sr_ind_est = np.unravel_index(np.argmax(nasurfdb), (len(zvec), len(rvec)))
    plt.scatter(rvec[sr_ind_est], zvec[sd_ind_est], c='y', s=20**2, marker='*')

    # Plot actual location:
    if (sr is not None) and (sd is not None):
        plt.scatter(rvec[rvec == sr], zvec[zvec == sd], c='r', s=20**2, marker='*')
    
    plt.title(f'Act. (Est.) Range = {sr} ({rvec[sr_ind_est]}) m, Depth = {sd} ({zvec[sd_ind_est]}) m')

    if show:
        plt.show()
    else:
        plt.close()
    return fig