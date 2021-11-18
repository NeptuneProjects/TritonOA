import numpy as np
from scipy.special import hankel1

def bartlett(K, r_hat):
    w = r_hat / np.linalg.norm(r_hat)
    B = abs(w.conj().T @ K @ w)

    return B


def pressure_field(phi_src, phi_rec, k, r):
    p = (phi_src * phi_rec) @ hankel1(0, -k * r)
    p = np.pi * 1j / (1.) * p
    p = np.conj(p)
    return p


def mfp():
    pass