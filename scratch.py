"""Scratch file."""

import datetime
import glob
import os
import gc

import numpy as np
import psutil
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
        the loaded matrix
    """
    return sio.mmread(path)


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
    current_process = psutil.Process(os.getpid())

    start_time = datetime.datetime.now()
    start_memory = current_process.memory_info()

    x = slinalg.spsolve(A, b, use_umfpack=umfpack)

    end_time = datetime.datetime.now()
    end_memory = current_process.memory_info()

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
        raise InvalidMatrixFormat(
            "Matrix is in format '{}', but only 'csr' and 'csc' are supported".
            format(a_format))

    print("Starting benchmark with {} runs using {}".format(
        n_times, 'umfpack' if umfpack else 'superlu'))

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

    del xe
    print("Collecting memory...")
    gc.collect()
    print("GC collection finished")

    return {
        'elapsed_time': elapsed_time,
        'memory_physical': physical_memory,
        'memory_virtual': virtual_memory,
        'relative_error': relative_error,
    }


def main_sdf():
    """Main function for benchmark with symmetric positive definite matrices."""
    print("Launching benchmark for symmetric positive definite matrices")
    matrices_sdf = sorted(glob.glob('./data/sym-def-pos/*.mtx'))
    print("Found these matrices:")
    for m in matrices_sdf:
        print("{}".format(m))

    # for each matrix, launch analysis
    results = dict()
    for index, path in enumerate(matrices_sdf):
        matrix_name = path.split('/')[-1][:-4]
        A = load_matrix(path)
        b = create_b(A)
        print("\n\n## ---------------------- ##")
        print("Solving for matrix {}/{}: {}".format(index, len(matrices_sdf),
                                                    matrix_name))
        print("Matrix dimension: {}".format(A.shape))

        a_format = A.getformat()
        # convert but try to save some memory
        if a_format not in {'csr', 'csc'}:
            print("Matrix is in '{}' format, converting to 'csr'".format(
                a_format))
            Mat = A.tocsr()
            print("Matrix format converted")

            del A
            print("Collecting old matrix...")
            gc.collect()
            print("GC collection finished")

            result = solve_with_profiling(Mat, b)

            del b
            print("Collecting old b...")
            gc.collect()
            print("GC collection finished")
        else:
            result = solve_with_profiling(A, b)
            del A, b
            print("Collecting old A and b...")
            gc.collect()
            print("GC collection finished")

        results[matrix_name] = result
        print("Done with matrix {}".format(matrix_name))

    print("Done!")


if __name__ == '__main__':
    main_sdf()