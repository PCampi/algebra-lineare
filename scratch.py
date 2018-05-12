"""Scratch file."""

import datetime

import numpy as np
import scipy as sp
import scipy.io as sio
import scipy.sparse.linalg as slinalg


def load_mm_matrix(name):
    """Load a matrix in Matrix Market format from the data folder.

    Parameters
    ----------
    name: str
        name of the matrix file
    
    Returns
    -------
    m: scipy.sparse matrix
        the loaded matrix
    """
    return sio.mmread('./data/' + name)


def create_b(matrix):
    """Create the rhs vector for the system A*xe = b where
    xe is a vector of only ones, with shape (A.shape[1], 1).
    """
    xe = np.ones((matrix.shape[1], 1))
    b = matrix @ xe  # use @ because np.dot fails with sparse matrices
    return b


def solve_system(A, b, umfpack=True):
    """Solve a sparse linear system with coefficients matrix A and
    rhs b.

    Parameters
    ----------
    A: scipy.sparse matrix
        coefficients matrix
    
    b: numpy.array of shape(A.shape[1], 1)
        right hand side of the system that should cause the exact solution
        to be all ones
    
    Returns
    -------
    result: Dict
        dictionary with the following key-value pairs:
            'x': result of the computation
            'elapsed_time': time spent during computation
            'memory': memory used during computation
            'solver_library': 'umfpack' or 'superlu'
    """
    # 1. converto la matrice in formato csr o csc prima di lanciare l'esecuzione
    if A.getformat() not in {'csr', 'csc'}:
        A = A.tocsr()

    # TODO: insert memory profiling here and after solving the system
    start_time = datetime.datetime.now()
    x = slinalg.spsolve(A, b, use_umfpack=umfpack)
    end_time = datetime.datetime.now()

    if umfpack:
        solver_library = 'umfpack'
    else:
        solver_library = 'superlu'

    result = {
        'x': x,
        'elapsed_time': end_time - start_time,
        'memory': 1,
        'solver_library': solver_library,
    }

    return result
