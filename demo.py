"""
Main file to run SUnAA on a basic example (DC1)
"""
import argparse
import os

import scipy.io as sio

from src.noise import AdditiveWhiteGaussianNoise as AWGN
from src.model import SUnAA
from src.metrics import RMSE, SRE

# NOTE Change to use your own data here
DATA_DIR = "./data/"
DATASET = "DC1"
DICTIONARY = "EE.mat"
ABUNDANCES = "XT.mat"
HSI = "Y_clean.mat"


def main(args):
    # Load data
    Y = sio.loadmat(os.path.join(DATA_DIR, DATASET, HSI))["Y_clean"]
    print(f"Y shape => {Y.shape}")
    D = sio.loadmat(os.path.join(DATA_DIR, DATASET, DICTIONARY))["EE"]
    print(f"D shape => {D.shape}")
    A_gt = sio.loadmat(os.path.join(DATA_DIR, DATASET, ABUNDANCES))["XT"]
    print(f"A shape => {A_gt.shape}")

    p = args.num_endmembers
    print(f"Number of endmembers to be found: {p}")

    # Apply noise
    noise = AWGN(args.SNR)
    # Reshape Y
    H, W, L = Y.shape
    N = H * W
    Y = Y.transpose(2, 0, 1).reshape(L, N)
    Y = noise.apply(Y, seed=args.seed)
    # Reshape ground truth abundances
    M, h, w = A_gt.shape
    assert h == H
    assert w == W
    A_gt = A_gt.reshape(M, N)

    # Call model
    model = SUnAA(T=args.iters)
    A, B = model.solve(Y, D, p)

    # NOTE Current A is low rank
    # NOTE Full rank can be obtained as follow
    A_full = B @ A

    # Compute metrics
    sre = SRE()
    rmse = RMSE()

    print(f"SRE => {round(sre(A_full, A_gt), 2)}")
    print(f"RMSE = > {round(rmse(A_full, A_gt), 2)}")


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-N",
        "--SNR",
        help="Signal to Noise Ratio value (SNR)",
        type=float,
        default=None,
    )
    parser.add_argument(
        "-T",
        "--iters",
        help="Outer iterations in SUnAA (T)",
        type=int,
        default=500,
    )
    parser.add_argument(
        "-p",
        "--num_endmembers",
        help="Number of endmembers (p)",
        type=int,
        default=5,
    )
    parser.add_argument(
        "-s",
        "--seed",
        help="Seeding random number generator (needed for reproducibility)",
        type=int,
        default=0,
    )
    args = parser.parse_args()
    main(args)
