#!/usr/bin/env python3

'''This module contains tools for defining sound speed profiles using
ocean models as well as measured data.  Conversion of seawater 
properties is performed using the Gibbs SeaWater Oceanographic Toolbox 
of TEOS-10 (https://www.teos-10.org/).

William Jenkins
Scripps Institution of Oceanography
wjenkins |a|t| ucsd |d|o|t| edu

Licensed under GNU GPLv3; see LICENSE in repository for full text.
'''

import gsw
import matplotlib.pyplot as plt
import numpy as np

from tritonoa.core import SoundSpeedProfile

class MunkSSP(SoundSpeedProfile):
    def __init__(self, z_max, dz=1):
        z = np.arange(0, z_max+dz, dz)
        B = 1200.
        Z0 = 1200.
        C0 = 1492.
        EP = 0.006
        eta = 2 * (z - Z0) / B
        c_p = C0 * (1 + EP*(eta + np.exp(-eta) - 1))
        super().__init__(z, c_p)





class SoundSpeedFunctions:
    '''This class of functions and their documentation were obtained
    from the National Physics Laboratory website:
    http://resource.npl.co.uk/acoustics/techguides/soundseawater/underlying-phys.html#up_mackenzie
    '''

    def __init__(self):
        pass


    @staticmethod
    def sos(Z, S, T, model="UNESCO", latitude=45):
        if model == "Coppens":
            return SoundSpeedFunctions.sos_Coppens(Z, S, T)
        elif model == "Mckenzie":
            return SoundSpeedFunctions.sos_Mckenzie(Z, S, T)
        elif model == "NPL":
            return SoundSpeedFunctions.sos_NPL(Z, S, T, latitude)
        elif model == "UNESCO":
            return SoundSpeedFunctions.sos_UNESCO(Z, S, T, latitude)


    @classmethod
    def sos_Coppens(Z, S, T):
        '''Speed of sound in sea-water as a function of temperature, 
        salinity and depth is given by Coppens equation [1].
        
        Parameters
        ----------
        Z : array
            Depth [m]
        S : array
            Salinity [ppt]
        T : array
            Temperature [C]
        
        Returns
        -------
        c : array
            Speed of sound [m/s]
        
        Notes
        -----
        Range of validity: temperature 0 to 35 °C, salinity 0 to 45 
        parts per thousand, depth 0 to 4000 m.

        .. [1] A.B. Coppens, Simple equations for the speed of sound in 
        Neptunian waters (1981) J. Acoust. Soc. Am. 69(3), pp 862-863
        '''

        def _c0ST(S, t):
            c0ST = 1449.05 \
                + 45.7 * t \
                - 5.21 * t**2 \
                + 0.23 * t**3 \
                + (1.333 - 0.126*t + 0.009*t**2) * (S - 35)
            return c0ST
        
        T /= 10
        Z /= 1e3

        return _c0ST(S, T) \
            + (16.23 + 0.253 * T) * Z \
            + (0.213 - 0.1 * T) * Z**2 \
            + (0.016 + 0.0002 * (S - 35)) * (S - 35) * T * Z
    

    @staticmethod
    def sos_DelGrosso(Z, S, T):
        '''Del Grosso equation for sound speed.

        Parameters
        ----------
        Z : array
            Depth [m]
        S : array
            Salinity [ppt]
        T : array
            Temperature [C]
        
        Returns
        -------
        c : array
            Speed of sound [m/s]
        
        Notes
        -----
        An alternative equation to the UNESCO algorithm which has a more 
        restricted range of validity, but which is preferred by some 
        authors, is the Del Grosso equation [1]. Wong and Zhu [2] also
        reformulated this equation for the new 1990 International 
        Temperature Scale and their version is implemented here.

        Range of validity: temperature 0 to 30 °C, salinity 30 to 40 
        parts per thousand, pressure 0 to 1000 kg/cm2, where 
        100 kPa=1.019716 kg/cm2. [2].

        .. [1] V.A. Del Grosso, New equation for the speed of sound in 
            natural waters (with comparisons to other equations) (1974) 
            J. Acoust. Soc. Am 56(4) pp 1084-1091
        .. [2] G.S.K. Wong and S Zhu, Speed of sound in seawater as a 
            function of salinity, temperature and pressure (1995) J. 
            Acoust. Soc. Am. 97(3) pp 1732-1736
        '''

        def _at_each_depth(P, S, T):
            '''Pressure in [kg/cm^2]'''
            nT = np.arange(0, 4)
            nS = np.arange(0, 3)
            nP = np.arange(0, 4)
            
            Tvec = np.power(T * np.ones(len(nT)), nT)
            Svec = np.power(S * np.ones(len(nS)), nS)
            Pvec = np.power(P * np.ones(len(nP)), nP)

            C000 = 1402.392
            CT = np.array([0., 5.012285, -0.551184e-1, 0.221649e-3])
            CS = np.array([0., 1.329530, 0.1288598e-3])
            CP = np.array([0., 0.1560592, 0.2449993e-4, -0.8833959e-8])
            C_ST = -0.1275936e-1
            C_TP = 0.6353509e-2
            C_T2P2 = 0.2656174e-7
            C_TP2 = -0.1593895e-5
            C_TP3 = 0.5222483e-9
            C_T3P = -0.4383615e-6
            C_S2P2 = -0.1616745e-8
            C_ST2 = 0.9688441e-4
            C_S2TP = 0.4857614e-5
            C_STP = -0.3406824e-3

            dCT = CT @ Tvec
            dCS = CS @ Svec
            dCP = CP @ Pvec
            dCSTP = C_TP * T * P \
                + C_T3P * T**3 * P \
                + C_TP2 * T * P**2 \
                + C_T2P2 * T**2 * P**2 \
                + C_TP3 * T * P**3 \
                + C_ST * S * T \
                + C_ST2 * S * T**2 \
                + C_STP * S * T * P \
                + C_S2TP * S**2 * T * P \
                + C_S2P2 * S**2 * P**2
            
            return C000 + dCT + dCS + dCP + dCSTP


        # Pressure in [kg/cm^2]:
        P = 10.1972 * SoundSpeedFunctions.depth_to_pressure(Z)
        vfunc = np.vectorize(_at_each_depth)

        return vfunc(P, S, T)


    @staticmethod
    def sos_Mckenzie(Z, S, T):
        '''Speed of sound in sea-water as a function of temperature, 
        salinity and depth is given by the Mackenzie equation [1].
        
        Parameters
        ----------
        Z : array
            Depth [m]
        S : array
            Salinity [ppt]
        T : array
            Temperature [C]
        
        Returns
        -------
        c : array
            Speed of sound [m/s]

        Notes
        -----
        Range of validity: temperature 2 to 30 °C, salinity 25 to 40 
        parts per thousand, depth 0 to 8000 m.

        .. [1] K.V. Mackenzie, Nine-term equation for the sound speed in 
           the oceans (1981) J. Acoust. Soc. Am. 70(3), pp 807-812
        '''        

        return 1448.96 \
            + 4.591 * T \
            - 5.304e-2 * T**2 \
            + 2.374e-4 * T**3 \
            + 1.340 * (S - 35) \
            + 1.630e-2 * Z \
            + 1.675e-7 * Z**2 \
            - 1.025e-2 * T * (S - 35) \
            - 7.139e-13 * T * Z**3
   

    @staticmethod
    def sos_NPL():
        return
    
    
    @staticmethod
    def sos_UNESCO(Z, S, T):
        '''The international standard algorithm, often known as the 
        UNESCO algorithm, for calculating sound speed.
        
        Parameters
        ----------
        Z : array
            Depth [m]
        S : array
            Salinity [ppt]
        T : array
            Temperature [C]
        
        Returns
        -------
        c : array
            Speed of sound [m/s]

        Notes
        -----
        The international standard algorithm, often known as the 
        UNESCO algorithm, is due to [1], and has a more complicated form 
        than the simple equations above, but uses pressure as a variable 
        rather than depth. For the original UNESCO paper see [2]. Wong 
        and Zhu [3] recalculated the coefficients in this algorithm 
        following the adoption of the International Temperature Scale of 
        1990 and their form of the UNESCO equation is implemented here.

        Range of validity: temperature 0 to 40 °C, salinity 0 to 40 
        parts per thousand, pressure 0 to 1000 bar [3].

        .. [1] C-T. Chen and F.J. Millero, Speed of sound in seawater at 
        high pressures (1977) J. Acoust. Soc. Am. 62(5) pp 1129-1135
        .. [2] N.P. Fofonoff and R.C. Millard Jr. Algorithms for 
        computation of fundamental properties of seawater (1983), UNESCO 
        technical papers in marine science. No. 44, Division of Marine 
        Sciences. UNESCO, Place de Fontenoy, 75700 Paris.
        .. [3] G.S.K. Wong and S Zhu, Speed of sound in seawater as a 
        function of salinity, temperature and pressure (1995) J. Acoust. 
        Soc. Am. 97(3) pp 1732-1736
         '''

        def _at_each_depth(P, S, T):
            """Pressure in [bar]"""
            nP = np.arange(0, 4)
            nT = np.arange(0, 6)
            Pvec = np.power(P * np.ones(len(nP)), nP)
            Tvec = np.power(T * np.ones(len(nT)), nT)

            AMAT = np.array([
                [1.389, -1.262e-2, 7.166e-5, 2.008e-6, -3.21e-8, 0.],
                [9.4742e-5, -1.2583e-5, -6.4928e-8, 1.0515e-8, -2.0142e-10, 0.],
                [-3.9064e-7, 9.1061e-9, -1.6009e-10, 7.994e-12, 0., 0.],
                [1.100e-10, 6.651e-12, -3.391e-13, 0., 0., 0.]
            ])
            BMAT = np.array([
                [-1.922e-2, -4.42e-5, 0., 0., 0., 0.],
                [7.3637e-5, 1.7950e-7, 0., 0., 0., 0.],
                np.zeros(len(nT)),
                np.zeros(len(nT)),
            ])
            CMAT = np.array([
                [1402.388, 5.03830, -5.81090e-2, 3.3432e-4, -1.47797e-6, 3.1419e-9],
                [0.153563, 6.8999e-4, -8.1829e-6, 1.3632e-7, -6.1260e-10, 0.],
                [3.1260e-5, -1.7111e-6, 2.5986e-8, -2.5353e-10, 1.0415e-12, 0.],
                [-9.7729e-9, 3.8513e-10, -2.3654e-12, 0., 0., 0.]
            ])
            DMAT = np.array([1.727e-3, -7.9836e-6, 0., 0.])

            A = AMAT @ Tvec @ Pvec
            B = BMAT @ Tvec @ Pvec
            C = CMAT @ Tvec @ Pvec
            D = DMAT @ Pvec

            return C + A*S + B*S**(3/2) + D*S**2
        
        # Pressure in [bar]
        P = 10 * SoundSpeedFunctions.depth_to_pressure(Z)
        vfunc = np.vectorize(_at_each_depth)

        return vfunc(P, S, T)


    # TODO: Replace this implementation with GSW functions.
    # @staticmethod
    # def depth_to_pressure(Z, latitude=45):
    #     '''Converts depth to pressure.
        
    #     Parameters
    #     ----------
    #     Z : array
    #         Depth [m]
    #     latitude : array
    #         Latitude [deg]

    #     Returns
    #     -------
    #     array
    #         Pressure [mPa]
        
    #     Notes
    #     -----
    #     In this equation, P (=h(Z,lat)) would apply to the 
    #     oceanographers' standard ocean, defined as an ideal medium with 
    #     a temperature of 0 °C and salinity of 35 parts per thousand.

    #     Leroy and Parthiot (1998) give a table of corrections which are 
    #     needed when the standard formula is applied to specific oceans 
    #     and seas. The correction h0Z is the correction applicable to 
    #     common oceans. These are defined as open oceans between the 
    #     latitudes of 60°N and 40°S, and excluding closed ocean basins 
    #     and seas. A full range of corrections may be found in Leroy and 
    #     Parthiot [1].

    #     .. [1] C. C. Leroy and F Parthiot, Depth-pressure relationship 
    #         in the oceans and seas (1998) J. Acoust. Soc. Am. 103(3) pp 
    #         1346-1352
    #     '''
        
    #     def _h(Z, latitude):
    #         return _h45(Z) * _k(Z, latitude)
        
    #     def _h45(Z):
    #         return 1.00818e-2 * Z \
    #             + 2.465e-8 * Z**2 \
    #             - 1.25e-13 * Z**3 \
    #             + 2.8e-19 * Z**4

    #     def _k(Z, latitude):
    #         g = SoundSpeedFunctions.gravity
    #         return (g(latitude) - 2e-5) / (9.80612 - 1e-5 * Z)
        
    #     def _h0Z(Z):
    #         return 1.e-2 * Z / ((Z + 100) + 6.2e-6 * Z)
        
    #     return _h(Z, latitude) - _h0Z(Z)
    

    @staticmethod
    def gravity(latitude):
        '''International Gravity Formula [1].

        Parameters
        ----------
        latitude : array
            Latitude [deg]
        
        Returns
        -------
        g : array
            Gravitational force [m s^-2]
        
        Notes
        -----
        .. [1] ALLABY M, ed. A Dictionary of Earth Sciences. 3 ed. ed. 
            Oxford University Press; 2008. https://www.oxfordreference.com/view/10.1093/acref/9780199211944.001.0001/acref-9780199211944.
        '''

        latitude = np.radians(latitude)
        G1 = 9.7803267714
        G2 = 1.931851381639e-3
        G3 = 6.6943999013e-3
        g = G1*(1 + G2*np.sin(latitude)**2)/np.sqrt(1 - G3*np.sin(latitude)**2)

        return g
    

    
    

if __name__ == "__main__":
    z = np.linspace(0, 8000, 100)
    S = np.ones(len(z)) * 35
    T = np.concatenate((np.linspace(20, 12, 2), np.linspace(12, 1, 10), np.linspace(1, 5, 88)))
    
    c = SoundSpeedFunctions.sos_UNESCO(z, S, T)
    import matplotlib.pyplot as plt
    plt.plot(c, z)
    plt.gca().invert_yaxis()
    plt.show()