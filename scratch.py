"""Scratch file."""

import datetime
import glob
import os
import gc

import numpy as np
import psutil
from pypardiso import spsolve as mkl_spsolve
import scipy as sp
import scipy.io as sio
import scipy.sparse.linalg as slinalg

import tqdm


class InvalidMatrixFormat(Exception):
    """Exception raised if a matrix is in an invalid format."""
    pass


def load_matrix(path):
    """Load a matrix in Matrix Market format from the data folder.

    Parameters
    ----------
    path: str
        path of the matrix file
    
    Returns
    -------
    m: scipy.sparse matrix
        the loaded matrix in 'csr' format
    """
    return sio.mmread(path).tocsr()


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


def solve_system(A, b, mkl=True):
    """Solve a sparse linear system with coefficients matrix A and
    rhs b.

    Parameters
    ----------
    A: scipy.sparse matrix
        coefficients matrix, for best performance must be in csr format
    
    b: numpy.array of shape(A.shape[1], 1)
        right hand side of the system that should cause the exact solution
        to be all ones
    
    mkl: boolean
        if True, use the Pardiso solver from the Intel MKL library to speedup
        computation, otherwise try with umfpack/superLU
    
    Returns
    -------
    result: Dict
        dictionary with the following key-value pairs:
            'x': result of the computation
            'elapsed_time': time spent during computation
            'memory': memory used during computation
            'solver_library': 'mkl' or 'superlu'
    """
    current_process = psutil.Process(os.getpid())

    if mkl:
        solve_function = mkl_spsolve
    else:
        solve_function = slinalg.spsolve

    start_time = datetime.datetime.now()
    start_memory = current_process.memory_info()

    x = solve_function(A, b)

    end_time = datetime.datetime.now()
    end_memory = current_process.memory_info()

    solver_library = 'mkl' if mkl else 'superlu'

    result = {
        'x': x,
        'elapsed_time': end_time - start_time,
        'memory_physical': end_memory.rss - start_memory.rss,
        'memory_virtual': end_memory.vms - start_memory.vms,
        'solver_library': solver_library,
    }

    return result


def solve_with_profiling(A, b, n_times=1, mkl=True, progress=True):
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
    
    mkl: bool
        if True use Intel MKL Pardiso solver, otherwise SuperLU (waaaay slower...)
    
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
            'solver_library': List[str], list of values of the solver library
    """
    print("Starting benchmark with {} runs using {}:".format(
        n_times, 'Intel MKL' if mkl else 'SuperLU'))

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

    solver = [result['solver_library'] for result in results]

    del xe
    print("Collecting old xe...")
    gc.collect()
    print("GC collection finished")

    return {
        'elapsed_time': elapsed_time,
        'memory_physical': physical_memory,
        'memory_virtual': virtual_memory,
        'relative_error': relative_error,
        'solver_library': solver,
    }


def main_sdf():
    """Main function for benchmark with symmetric positive definite matrices."""
    print("Launching benchmark for symmetric positive definite matrices")
    matrices_sdf = sorted(glob.glob(
        './data/sym-def-pos/*.mtx'))[:-1]  # don't use the last big one
    print("Will use these matrices:")
    for m in matrices_sdf:
        print("{}".format(m))

    # for each matrix, launch analysis
    results = dict()
    for index, path in enumerate(matrices_sdf):
        matrix_name = path.split('/')[-1][:-4]
        A = load_matrix(path)

        if A.getformat() != 'csr':
            raise InvalidMatrixFormat(
                "Matrix is in format '{}', but only 'csr' is supported".format(
                    A.getformat()))

        print("\n\n## ---------------------- ##")
        print("Solving for matrix {} ({}/{})".format(matrix_name, index + 1,
                                                     len(matrices_sdf)))
        print("Matrix dimension: {}".format(A.shape))

        b = create_b(A)
        result = solve_with_profiling(A, b, n_times=30)

        del A, b
        print("Collecting old A and b...")
        gc.collect()
        print("GC collection finished")

        results[matrix_name] = result
        print("Done with matrix {}".format(matrix_name))

    print("Done!")
    return results


if __name__ == '__main__':
    main_sdf()
