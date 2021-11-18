import numpy as np
from scipy.interpolate import interp1d


class Environment:
    def __init__(self, profiles, nmedia=1):
        self.profiles = profiles
        self.nmedia = nmedia

        assert len(self.profiles) == self.nmedia

        pass

    class SSP:
        def __init__(self, ):
            pass

    
    class Source:
        def __init__(self, depth):
            self.depth = depth
            # self.x = None
            # self.y = None


    class Domain:
        def __init__(self, range, depth, offsets=None):
            self.range = range
            self.depth = depth
            if offsets is not None:
                self.offsets = offsets
    

    class Pos:
        def __init__(self, Source, Domain):
            self.s = Source
            self.r = Domain


    class Halfspace:
        def __init__(
                self,
                alphaR = np.array([]),
                betaR = np.array([]),
                rho=np.array([]),
                alphaI=np.array([]),
                betaI=np.array([])
            ):
            self.alphaR = np.array(alphaR)
            self.betaR = np.array(betaR)
            self.rho = np.array(rho)
            self.alphaI = np.array(alphaI)
            self.betaI = np.array(betaI)
        

    class BotBndry:
        def __init__(self, opt, Halfspace):
            self.opt
            self.halfspace = Halfspace


    class TopBndry:
        def __init__(self, opt):
            self.opt = opt
            # self.cp = None
            # self.cs = None
            # self.rho = None
    
    class Bndry:
        def __init__(self, top, bot):
            self.Top = top
            self.Bot = bot


    class Box:
        def __init__(self, z, r):
            self.r = r
            self.z = z

    pass







if __name__ == "__main__":

    pass
























class Kraken:

    def __init__(self, env):
        pass


    pass




























def pekeris(k2, freq, D, c1, c2, rho1, rho2, realflag):
    '''returns the characteristic function for the Pekeris waveguide
    k is the horizontal wavenumber (row or column vector)
    returns f, the characteristic function
    note: characteristic function vanishes at k = omega / c1
    Mike Porter 11/2009'''

    omega2 = (2 * np.pi * freq) ** 2

    kz1 = np.sqrt(omega2 / c1 ** 2 - k2)
    kz2 = PekerisRoot(k2 - omega2 / c2 ** 2).T

    # Here is the Pekeris characteristic function
    # multiplied by 1i and rearranged a bit

    f = rho2 * kz1 * np.cos(kz1 * D) + rho1 * kz2 * np.sin(kz1 * D) # Formual from JKPS, Ch. 2

    if realflag:
        f = np.real(f)
    
    # Calculate the mode count for the trial eigenvalue, k2
    ModeCount = int(np.floor(kz1 * D / np.pi))

    ii = int(np.where(np.sign(f * np.sin(kz1 * D)) < 0))
    ModeCount[ii] += 1

    return f, ModeCount


def PekerisRoot(z):
    '''Calculates the Pekeris branch of the square root.
    Mike B. Porter, 4/2009'''

    rootz = np.zeros(z.shape) + 1j * np.zeros(z.shape)

    ii = np.where(np.real(z) >= 0.)
    rootz[ii] = np.sqrt(z[ii])
    
    ii = np.where(np.real(z) < 0.)
    rootz[ii] = np.sqrt(-z[ii])

    return rootz



def test_func(**kwargs):
    print(kwargs['a'])
    





    # parameters = dict()

    # # Set Run Type =======================================================================
    # parameters['fullfield'] = True
    # parameters['TITLE'] = 'TestMFP'

    # # Define Geometry ====================================================================
    # parameters['NMEDIA'] = 1
    # parameters['ZB'] = 100 # Bottom depth (m)
    # parameters['NZ'] = 101 # Number of depth points
    # parameters['Z'] = np.linspace(0, parameters['ZB'], parameters['NZ']) # Depth vector (m)
    # parameters['RMAX'] = 5 # Maximum range (km)
    # parameters['dR'] = 1 # Range step (m)
    # parameters['R'] = np.arange(10, 1000 * parameters['RMAX'] + parameters['dR'], parameters['dR']) # Range vector (m)
    # parameters['NR'] = len(parameters['R']) # Number of range points
    # # parameters['X'] = np.arange(0, parameters['RMAX'], 0.001)  # <-------------------------------- ***
    # parameters['NMESH'] = 0

    # # Define Source/Receiver ============================================================
    # # parameters['SD'] = 50
    # # parameters['SR'] = 
    # parameters['NSD'] = 1
    # parameters['RD'] = np.linspace(10, 80, 15)
    # parameters['NRD'] = len(parameters['RD'])
    # parameters['FREQ'] = 100

    # # Define Top Boundary =========================================================
    # parameters['TOPOPT'] = "CVW" # C = Linear SSP interp; V = Vacuum in upper halfspace; W = Wavelength-dependent Attenuation (dB/lambda)
    # parameters['SIGMA_TOP'] = 0 # RMS roughness (m)

    # # Define Sound Speed Profile ================================================
    # # SSP_TYPE = "isospeed"
    # # [parameters.update({k: v}) for k, v in env.default_SSP(SSP_TYPE, parameters['Z'], CP=1500, RHO=1000, AP=0).items()]
    # # [print(k, v) for k, v in env.default_SSP(SSP_TYPE, parameters['Z'], CP=1500, RHO=1000, AP=0).items()]
    # SSP_TYPE = "negative"
    # # [parameters.update({k: v}) for k, v in env.default_SSP(SSP_TYPE, parameters['Z'], CP=1490, dC=20, RHO=1000, AP=0).items()]
    # # [print(k, v) for k, v in env.default_SSP(SSP_TYPE, parameters['Z'], CP=1490, dC=20, RHO=1000, AP=0).items()]

    # # Define Bottom Boundary ======================================================
    # parameters['BOTOPT'] = "A" # A = Acousto-elastic halfspace
    # parameters['SIGMA_BOT'] = 0 # RMS roughness (m)
    # parameters['CPB'] = 1800 # P-wave speed (m/s)
    # parameters['CSB'] = 400 # S-wave speed (m/s)
    # parameters['RHOB'] = 1.8 # Density (g/cm3)
    # parameters['APB'] = 0.1 # P-wave attenuation (dB/kmHz)
    # parameters['ASB'] = 0.5 # S-wave attenuation (dB/kmHz)

    # # Phase Speed Limits ============================================================
    # parameters['CLOW'] = 0 # Lower phase speed limit (m/s)
    # parameters['CHIGH'] = parameters['CPB']  # Upper phase speed limit (m/s)

    # # Pre-compute values
    # omega = 2 * np.pi * f


    # z = np.random.randn(10,) + 1j * np.random.randn(10,)
    
    # rootz = PekerisRoot(z)
    # print(rootz)
    # print(rootz.T)































# ==========================================================================================
# ==========================================================================================
# ==========================================================================================
# ==========================================================================================
# ==========================================================================================
# ==========================================================================================
# ==========================================================================================

# Input variables (from command line):
# FileRoot

# for iProf in np.arange(0, 9999):
#     NV = np.array([1, 2, 4, 8, 16])

#     Title = 'KRAKEN- '



# def FUNCT(x, Delta, iPower):
#     iPowerR = 50
#     iPowerF = -50
#     Roof = 1.e50
#     Floor = 1.e-50

#     pass





# def bisect(xMin, xMax, xL, xR):

#     MaxBisections = 50

#     CountModes = True

#     xL = xMin # Initial left boundary
#     xR = xMax # Initial right boundary



#     pass






# def BCImpedance(x, BotTop, HS, f, g, iPower, ComplexFlag):

#     iTop = 0
#     iBot = 0
#     rhoInside = 1.
#     cInside = 1500
#     iPower = 0

#     # Get rho, c just inside the boundary
#     # There is at least one acoustic layer in the problem, except
#     # in the case where BOUNCE is used to get the refl. coef. for a purely elastic stack of layers.
#     # These are initialized above just to avoid a compiler warning

#     if BotTop == 'TOP':
#         if FirstAcoustic > 0:
#             iTop = Loc[FirstAcoustic] + N[FirstAcoustic] + 1
#             rhoInside = rho(iTop)
#             cInside = np.sqrt(omega2 * h[FirstAcoustic] ** 2 / (2. + B1[iTop]))
#     elif BotTop == 'BOT':
#         if LastAcoustic > 0:
#             iBot = Loc[LastAcoustic] + N[LastAcoustic] + 1
#             rhoInside = rho[iBot]
#             cInside = np.sqrt(omega2 * h[LastAcoustic] ** 2 / (2. + B1[iBot]))

#     # Return the impedance, depending on the type of boundary condition

#     if HS.BC == 'V': # Vacuum
#         f = 1.
#         g = 0.
#         yV = np.array([f, g, 0., 0., 0.], type=double)
#     elif HS.BC == 'R': # Rigid
#         f = 0.
#         g = 1.
#         yV = np.array([f, g, 0., 0., 0.])
#     elif HS.BC == 'A': # Acousto-elastic half-space
#         if np.real(HS.cS) > 0.:
#             gammaS2 = x - omega2 / (HS.cS) ** 2
#             gammaP2 = x - omega2 / (HS.cP) ** 2
#             gammaS = np.sqrt(gammaS2)
#             gammaP = np.sqrt(gammaP2)
#             mu = HS.rho * HS.cS ** 2

#             yV[0] = np.real((gammaS * gammaP - x) / mu)
#             yV[1] = np.real(((gammaS2 + x) ** 2 - 4. * gammaS * gammaP * x) * mu)
#             yV[2] = np.real(2. * gammaS * gammaP - gammaS2 - x)
#             yV[3] = np.real(gammaP * (x - gammaS2))
#             yv[4] = np.real(gammaS * (gammaS2 - x))

#             f = omega2 * yV[3]
#             g = yV[1]
#             if g > 0.:
#                 ModeCount += 1
#         else:
#             gammaP = np.sqrt(x - omega2 / HS.cP ** 2)
#             f = gammaP
#             g = HS.rho
#             if not ComplexFlag:
#                 f = f.astype(float)
#                 g = g.astype(float)
#     elif HS.BC == 'F': # Tabulated reflection coefficient
#         # Compute the grazing angle, theta
#         kx = np.sqrt(x)
#         kz = np.sqrt(omega2 / cInside ** 2 - x)
#         RInt.theta = RadDeg * np.arctan2(kz, kx)

#         # Evaluate R(ThetaInt)
#         if BotTop == 'TOP':
#             # call InterpolateReflectionCoefficient(RInt, RTop, NTopPts, PRTFile)
#             pass
#         else:
#             # call InterpolateReflectionCoefficient(RInt, RBot, NBotPts, PRTFile)
#             pass
        
#         # Convert R(theta) to (f,g) in Robin BC
#         RCmplx = RInt.R * np.exp(i * RInt.phi)
#         f = i * kz * (1. - RCmplx)
#         g = rhoInside * (1. + RCmplx)

#         f = i * kz * (1. - RCmplx) / (rhoInside * (1. + RCmplx))
#         g = 1.

#         if not ComplexFlag:
#             f = 0.
#             g = 1.
#             iPower = 0
#     elif HS.BC == 'P': # Precalculated reflection coef
#         # CALL InterpolateIRC( CMPLX( x, KIND=8 ), f, g, iPower, xTab, fTab, gTab, iTab, NkTab )

#         if not ComplexFlag:
#             f = 0.
#             g = 1.
#             iPower = 0
        
#     if BotTop == 'TOP':
#         g = -g
#         pass
    
#     if BotTop == 'TOP':
#         if FirstAcoustic > 1:
#             for Medium in np.arange(0, FirstAcoustic - 1):
#                 _, yV, iPower, _ = ElasticDN(x, yV, iPower, Medium)
            
#             f = omega2 * yV[3]
#             g = yV[1]
    
#     elif BotTop == 'BOT':
#         if LastAcoustic < SSP.NMedia:
#             for Medium in np.arange(0, LastAcoustic + 1):
#                 _, yV, iPower, _ = ElasticDN(x, yV, iPower, Medium)
            
#             f = omega2 * yV[3]
#             g = yV[1]
        
#     return







# def ElasticUP(x, yV, iPower, Medium):
#     '''Propagates through an elastic layer using compound matrix formulation'''

#     # Euler's method for first step
#     two_x = 2. * x
#     two_h = 2. * h[Medium]
#     four_h_x = 4. * h[Medium] * x
#     j = Loc[Medium] + N[Medium] + 1
#     xB3 = x * B3[j] - rho[j]

#     zV[0] = yV[0] - 0.5 * (  B1[j] * yV[3] - B2[j] * yV[4])
#     zV[1] = yV[1] - 0.5 * (-rho[j] * yV[3] -   xB3 * yV[4])
#     zV[2] = yV[2] - 0.5 * (  two_h * yV[3] + B4[j] * yV[4])
#     zV[3] = yV[3] - 0.5 * (    xB3 * yV[0] + B2[j] * yV[1] - two_x * B4[j] * yV[2])
#     zv[4] = yv[4] - 0.5 * ( rho[j] * yV[0] - B1[j] * yV[1] -      four_h_x * yV[3])

#     # Modified midpoint method
#     for ii in np.arange(0, N[Medium]):
#         j -= 1

#         xV = yV
#         yV = zV

#         xB3 = x * B3[j] - rho[j]

#         zV[0] = xV[0] - (  B1[j] * yV[3] - B2[j] * yV[4])
#         zV[1] = xV[1] - (-rho[j] * yV[3] -   xB3 * yV[4])
#         zV[2] = xV[2] - (  two_h * yV[3] + B4[j] * yV[4])
#         zV[3] = xV[3] - (    xB3 * yV[0] + B2[j] * yV[1] - two_x * B4[j] * yV[2])
#         zv[4] = xv[4] - ( rho[j] * yV[0] - B1[j] * yV[1] -      four_h_x * yV[3])

#         # Scale if necessary
#         if ii != 0:
#             if abs(zV[1]) < Floor:
#                 zV = Roof * zV
#                 yV = Roof * yV
#                 iPower = iPower - iPowerR
#             if abs(zV[1]) > Roof:
#                 zV = Floor * zV
#                 yV = Floor * yV
#                 iPower = iPower - iPowerF

#     return x, yV, iPower, Medium


# def ElasticDN(x, yV, iPower, Medium):
#     '''Propagates through an elastic layer using compound matrix formulation'''

#     # Euler's method for first step
#     two_x = 2. * x
#     two_h = 2. * h[Medium]
#     four_h_x = 4. * h[Medium] * x
#     j = Loc[Medium] + 1
#     xB3 = x * B3[j] - rho[j]

#     zV[0] = yV[0] + 0.5 * (  B1[j] * yV[3] - B2[j] * yV[4])
#     zV[1] = yV[1] + 0.5 * (-rho[j] * yV[3] -   xB3 * yV[4])
#     zV[2] = yV[2] + 0.5 * (  two_h * yV[3] + B4[j] * yV[4])
#     zV[3] = yV[3] + 0.5 * (    xB3 * yV[0] + B2[j] * yV[1] - two_x * B4[j] * yV[2])
#     zv[4] = yv[4] + 0.5 * ( rho[j] * yV[0] - B1[j] * yV[1] -      four_h_x * yV[3])

#     # Modified midpoint method
#     for ii in np.arange(0, N[Medium]):
#         j += 1

#         xV = yV
#         yV = zV

#         xB3 = x * B3[j] - rho[j]

#         zV[0] = xV[0] + (  B1[j] * yV[3] - B2[j] * yV[4])
#         zV[1] = xV[1] + (-rho[j] * yV[3] -   xB3 * yV[4])
#         zV[2] = xV[2] + (  two_h * yV[3] + B4[j] * yV[4])
#         zV[3] = xV[3] + (    xB3 * yV[0] + B2[j] * yV[1] - two_x * B4[j] * yV[2])
#         zv[4] = xv[4] + ( rho[j] * yV[0] - B1[j] * yV[1] -      four_h_x * yV[3])

#         # Scale if necessary
#         if ii != N[Medium]:
#             if abs(zV[1]) < Floor:
#                 zV = Roof * zV
#                 yV = Roof * yV
#                 iPower = iPower - iPowerR
#             if abs(zV[1]) > Roof:
#                 zV = Floor * zV
#                 yV = Floor * yV
#                 iPower = iPower - iPowerF
        
#     yV = (xV + 2. * yV + zV) / 4. # Apply the standard filter at the terminal point

#     return x, yV, iPower, Medium