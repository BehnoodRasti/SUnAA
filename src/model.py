import time
import numpy as np
import spams
from tqdm import tqdm

from src import EPS


class SUnAA:
    def __init__(self, T):
        self.T = T
        self.running_time = -1

    def solve(
        self,
        Y,
        D,
        p,
        *args,
        **kwargs,
    ):
        def loss(a, b):
            return 0.5 * ((Y - (D @ b) @ a) ** 2).sum()

        def updateB(a, b):
            R = Y - (D @ b) @ a
            for jj in range(p):
                z_j = D @ b[:, jj]
                norm_aj = np.linalg.norm(a[jj])
                if norm_aj < EPS:
                    ZZ = z_j
                else:
                    ZZ = (R @ a[jj]) / (norm_aj**2) + z_j
                bb = spams.decompSimplex(np.asfortranarray(ZZ[:, np.newaxis]), DD)
                b[:, jj] = np.squeeze(bb.todense())
                R = R + (z_j - D @ b[:, jj])[:, np.newaxis] @ a[jj][np.newaxis, :]
            return b

        tic = time.time()

        _, N = Y.shape
        _, N_atoms = D.shape

        YY = np.asfortranarray(Y)
        DD = np.asfortranarray(D)

        # Initialization
        B = (1 / N_atoms) * np.ones((N_atoms, p))
        A = (1 / p) * np.ones((p, N))

        print(f"Initial loss => {loss(A, B):.2e}")

        progress = tqdm(range(self.T))
        for pp in progress:
            B = updateB(A, B)
            A = np.array(spams.decompSimplex(YY, np.asfortranarray(D @ B)).todense())
            progress.set_postfix_str(f"loss={loss(A, B):.2e}")
            if np.isnan(loss(A, B)):
                # Restart
                pp = 0
                B = (1 / N_atoms) * np.ones((N_atoms, p))
                A = (1 / p) * np.ones((p, N))

        self.running_time = time.time() - tic

        print(f"SUnAA took {self.running_time:.1f}s")
        print(f"Final loss => {loss(A, B):.2e}")

        return A, B
