import subprocess
import sys

import numpy as np
from tqdm import tqdm

from TritonOA.io import readwrite
from TritonOA.sp import signal


def run_kraken(parameters, fname=None, shdflag=False, model='krakenc'):

    pos, _ = readwrite.build_env(parameters)
    retcode = subprocess.call(
        f'{model}.exe {parameters["TITLE"]}',
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    if shdflag:
        readwrite.write_fieldflp(parameters['TITLE'], 'R', pos)
        retcode = subprocess.call(
            f'field.exe {parameters["TITLE"]}',
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    return pos, retcode


def build_replica_field(parameters, verbose=False):
    SDvec = parameters['Z']

    P = np.zeros((len(SDvec), parameters['NR'], parameters['NRD']), dtype='complex_')

    for idx_SD, SD in tqdm(enumerate(SDvec), file=sys.stderr, total=len(SDvec)):
        parameters['SD'] = SD

        # 1. Calculate modes for this source depth
        pos, _ = run_kraken(parameters)
        phi_src, phi_rec, k, modes = readwrite.format_modes(parameters)

        # 2. For every receiver depth, multiply phi(z=RD) * H(RR) ==> RR x NR matrix (e.g., 5000x16)
        p = signal.pressure_field(phi_src, phi_rec, k, parameters['R'])

        # 3. Store the resulting pressure field into [idx_sd, :, :] = result at this SD
        P[idx_SD, :, :] = np.moveaxis(p, 0, -1)

        if verbose:
            print(f'{idx_SD+1} / {len(SDvec)}', end='\r', flush=True, file=sys.stderr)
    
    return P, (p, phi_src, phi_rec, k, modes)