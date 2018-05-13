"""Scratch file."""

import datetime
import os

import numpy as np
import psutil
import scipy as sp
import scipy.io as sio
import scipy.sparse.linalg as slinalg

import tqdm


class InvalidMatrixFormat(Exception):
    """Exception raised if a matrix is in an invalid format."""
    pass


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
        coefficients matrix, MUST be in csr or csc format, otherwise
        will throw an exception
    
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
    # 1. check if matrix is in right format, else raise exception
    a_format = A.getformat()
    if a_format not in {'csr', 'csc'}:
        raise InvalidMatrixFormat(
            "Matrix is in format '{}', but only 'csr' and 'csc' are supported".
            format(a_format))

    current_process = psutil.Process(os.getpid())

    start_time = datetime.datetime.now()
    start_memory = current_process.memory_info()

    x = slinalg.spsolve(A, b, use_umfpack=umfpack)

    end_memory = current_process.memory_info()
    end_time = datetime.datetime.now()

    solver_library = 'umfpack' if umfpack else 'superlu'

    result = {
        'x': x,
        'elapsed_time': end_time - start_time,
        'memory_physical': end_memory.rss - start_memory.rss,
        'memory_virtual': end_memory.vms - start_memory.vms,
        'solver_library': solver_library,
    }

    return result


def solve_with_profiling(A, b, n_times=1, umfpack=True, progress=True):
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
    
    progress: bool
        if True, show iterations with a progress bar, else only print
    
    Returns
    -------
    result: Dict
        dictionary with these key-value pairs:
            'elapsed_time': List[int], list of elapsed times for each iteration
            'memory_physical': List[int], list of physical memory used per iteration (bytes)
            'memory_virtual': List[int], list of virtual memory used per iteration (bytes)
            'relative_error': List[float], list of relative error computed as norm2(xe - x)/norm2(xe)
    """
    a_format = A.getformat()
    if a_format not in {'csr', 'csc'}:
        print("Matrix is in '{}' format, converting to 'csr'".format(a_format))
        A = A.tocsr()
        print("Matrix format converted")

    if progress:
        results = [solve_system(A, b) for i in tqdm.tqdm(range(n_times))]
    else:
        # define a custom iteration function
        def iter_fun(it, total):
            """Iteration function which prints some useful info."""
            print("iteration {}/{}".format(it, total))
            return solve_system(A, b)

        results = [iter_fun(it + 1, n_times) for it in range(n_times)]

    xe = np.ones((A.shape[1], ))

    elapsed_time = [
        result['elapsed_time'].total_seconds() for result in results
    ]

    physical_memory = [result['memory_physical'] for result in results]
    virtual_memory = [result['memory_virtual'] for result in results]

    relative_error = [
        get_relative_error(xe, result['x']) for result in results
    ]

    return {
        'elapsed_time': elapsed_time,
        'memory_physical': physical_memory,
        'memory_virtual': virtual_memory,
        'relative_error': relative_error,
    }


if __name__ == '__main__':
    A = load_mm_matrix('cfd1.mtx')
    b = create_b(A)

    print("Solving...")
    result = solve_with_profiling(A, b)
    print("Done!")
