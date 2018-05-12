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


def get_relative_error(xe, x):
    """Get the relative error between two solutions, the exact xe
    and the computed x."""
    relative_error = np.linalg.norm(xe - x, ord=2) / np.linalg.norm(xe, ord=2)
    return relative_error


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
    # 1. convert matrix to csr format before solving
    a_format = A.getformat()
    if a_format not in {'csr', 'csc'}:
        A = A.tocsr()
        print("Matrix converted from '{}' format to 'csr' format.".format(
            a_format))

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


def solve_with_profiling(A, b, n_times=1, umfpack=True):
    """Perform a benchmark on the given matrix-rhs for solving A*xe = b,
    where xe is assumed to be a vector of ones [1, 1,..., 1].T

    Parameters
    ----------
    A: scipy.sparse matrix
        the coefficient matrix
    
    b: numpy.array
        right-hand side of A*xe = b, where xe is a vector of ones
        [1, 1, 1,..., 1].T
    
    n_times: int
        number of times that the test will be repeated, default 1
    
    umfpack: bool
        wether to use umfpack as a solver, default True (it's way faster)
    
    Returns
    -------

    """
    results = [solve_system(A, b, umfpack=umfpack) for _ in range(n_times)]

    xe = np.ones((A.shape[1], 1))

    elapsed_time = [
        result['elapsed_time'].total_seconds() for result in results
    ]

    memory_used = [result['memory'] for result in results]

    relative_error = [
        get_relative_error(xe, result['x']) for result in results
    ]

    return {
        'elapsed_time': elapsed_time,
        'memory': memory_used,
        'relative_error': relative_error,
    }
