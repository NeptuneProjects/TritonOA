import os
import sys
sys.path.append("/Users/williamjenkins/Research/Code/TritonOA/")

import matplotlib as mpl
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

from TritonOA.io import readwrite
from TritonOA.env import env

# ********************** STEP 1: DEFINE ENVIRONMENT FILE **********************
# Block 1: Title ==============================================================
TITLE = "TESTKRAKEN"
# Block 2: Frequency ==========================================================
FREQ = 100
# Block 3: Number of media ====================================================
NMEDIA = 1
# Block 4: Top Options ========================================================
TOPOPT = "CVF"
# Block 4a: Top Halfspace Properties ==========================================
top_halfspace_flag = False
if top_halfspace_flag:
    ZT = 0
    CPT = 0
    CST = 0
    RHOT = 0
    APT = 0
    AST = 0
# Block 5: Sound Speed Profile ================================================
NMESH = 1500
SIGMA_TOP = 0.5
ZB = 1500

SSP_TYPE = "read"

Z = np.linspace(0,ZB,NMESH)
if SSP_TYPE == "isospeed":
    CP = 1500 * np.ones(Z.shape)
elif SSP_TYPE == "positive":
    CP = np.linspace(1440, 1500, NMESH)
elif SSP_TYPE == "negative":
    CP = np.linspace(1525, 1475, NMESH)
elif SSP_TYPE == "defined":
    CP = np.zeros(Z.shape)
elif SSP_TYPE == "read":
    df = pd.read_csv("/Users/williamjenkins/Documents/SIO/Travel/2021 Norway UAK/Acoustic_positioning_exercise/Software/XBT.csv")
    Z_BT = np.array(df.Var1)
    CP_BT = np.array(df.Var2)
    f = interp1d(Z_BT, CP_BT)
    CP = f(Z)
    CP[0:5] = 1442

CS = 0 * np.ones(Z.shape)
RHO = 1.035 * np.ones(Z.shape)
AP = 0 * np.ones(Z.shape)
AS = 0 * np.ones(Z.shape)

ssp = env.SSPraw(Z, CP, CS, RHO, AP, AS)
# Block 6: Bottom Options =====================================================
BOTOPT = "A"
SIGMA_BOT = 0.5
# Block 6b: Bottom Halfspace Properties =======================================
CPB = 5000
CSB = 0
RHOB = 3.8
APB = 0.2
ASB = 0
# Block 7: Phase Speed Limits =================================================
CLOW = 0
CHIGH = CPB
# Block 8: Maximum Range ======================================================
RMAX = 10
# Block 9: Source/Receiver Depths =============================================
NSD = 1
SD = 15.5
NRD = NMESH
RD = Z

# ********************** STEP 2: WRITE ENVIRONMENT FILE ***********************
top = env.TopBndry(TOPOPT)
halfspace = env.HS(CPB, CSB, RHOB, APB, ASB)
bottom = env.BotBndry(BOTOPT, halfspace)
bdy = env.Bndry(top, bottom)

depth = [0, ZB]
ssp_list = [ssp]
NMESH = [NMESH]
sigma = [SIGMA_TOP, SIGMA_BOT] # Roughness at each layer; only affects attenuation (imag. part)
ssp = env.SSP(ssp_list, depth, NMEDIA, TOPOPT, NMESH, sigma)

cInt = env.cInt(CLOW, CHIGH)

s = env.Source([SD])
X = np.arange(0, RMAX, 0.01)
r = env.Dom(X, Z)
pos = env.Pos(s,r)
# pos.s.depth = [SD]
pos.Nsd = NSD
pos.Nrd = NRD

readwrite.write_env(f"{TITLE}.env", "KRAKEN", TITLE, FREQ, ssp, bdy, pos, [], cInt, RMAX)

# ********************* STEP 3: CALCULATE ACOUSTIC FIELD **********************
readwrite.write_fieldflp(TITLE, "R", pos)
os.system(f"krakenc.exe {TITLE}")
os.system(f"field.exe {TITLE}")

# **************************** STEP 4: PLOT MODES *****************************
options = {"fname": f"{TITLE}.mod", "freq": 0}
modes = readwrite.read_modes(**options)
delta_k = np.max(modes.k.real) - np.min(modes.k.real)
bandwidth = delta_k * 2.5 / 2 / (2*np.pi)

print(modes)
print("Range cell size (m):", 2 * np.pi / delta_k)
print("Bandwidth (Hz):", bandwidth)
print("Coherence time (s):", 1 / bandwidth)
print("Cell cross time (s):", 2 * np.pi / delta_k / 2.5)

# modes.plot()

# **************************** STEP 5: PLOT FIELD *****************************
[_, _, _, _, Pos1, pressure] = readwrite.read_shd(f"{TITLE}.shd")
pressure = abs(pressure)
pressure[pressure == 0] = 1e-30
pressure = 10 * np.log10(pressure / np.max(pressure))
levs = np.linspace(np.min(pressure), np.max(pressure), 40)

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

plt.show()
