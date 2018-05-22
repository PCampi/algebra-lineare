"""Main file."""

import csv
import datetime
import gc
import glob
import os
import pathlib
import platform
import sys
from collections import defaultdict
from typing import Dict, Union

import numpy as np
import psutil
import scipy as sp
import scipy.io as sio
import scipy.sparse.linalg

try:
    import pypardiso
except ImportError as e:
    print("Module PyPardiso not available, cannot use Intel MKL.")


class InvalidMatrixFormat(Exception):
    """Exception raised if a matrix is in an invalid format."""
    pass


def load_matrix(path: str, matrix_format: str):
    """Load a matrix in Matrix Market format from the data folder.

    Parameters
    ----------
    path: str
        path of the matrix file
    
    matrix_format: str
        {'csc', 'csr'} should be 'csc' if using UMFPACK of SuperLU,
        or 'csr' if using Intel MKL
    
    Returns
    -------
    m: scipy.sparse matrix
        the loaded matrix in 'csr' or 'csc' format
    """
    if matrix_format == 'csr':
        return sio.mmread(path).tocsr()
    elif matrix_format == 'csc':
        return sio.mmread(path).tocsc()
    else:
        raise ValueError(
            "Invalid argument matrix_format. Should be one of 'csr', 'csc', got {} instead.".
            format(matrix_format))


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
    return float(relative_error)


def solve_with_profiling(A, b, solver_library='umfpack'):
    """Perform a benchmark on the given matrix-rhs for solving A*xe = b,
    where xe is assumed to be a vector of ones [1, 1,..., 1].T

    Parameters
    ----------
    A: scipy.sparse matrix
        the coefficient matrix
    
    b: numpy.array
        right-hand side of A*xe = b, where xe is a vector of ones
        [1, 1, 1,..., 1].T
    
    Returns
    -------
    result: Dict
        dictionary with these key-value pairs:
            'elapsed_time': int, elapsed time
            'memory_physical': int, physical memory used (bytes)
            'memory_virtual': int, virtual memory used (bytes)
            'relative_error': float, relative error computed as norm2(xe - x)/norm2(xe)
            'solver_library': str, value of the solver library
            'matrix_dimensions': str, value of NxM
    """
    current_process = psutil.Process(os.getpid())
    umfpack_mem_error = False

    if solver_library == 'mkl':
        start_time = datetime.datetime.now()
        start_memory = current_process.memory_info()

        x = pypardiso.spsolve(A, b)

        end_time = datetime.datetime.now()
        end_memory = current_process.memory_info()
    elif solver_library == 'superlu':
        start_time = datetime.datetime.now()
        start_memory = current_process.memory_info()

        x = scipy.sparse.linalg.spsolve(A, b, use_umfpack=False)

        end_time = datetime.datetime.now()
        end_memory = current_process.memory_info()
    elif solver_library == 'umfpack':
        start_time = datetime.datetime.now()
        start_memory = current_process.memory_info()

        try:
            x = scipy.sparse.linalg.spsolve(A, b, use_umfpack=True)
        except MemoryError:
            print("Got MemoryError for UMFPACK!")
            umfpack_mem_error = True

        end_time = datetime.datetime.now()
        end_memory = current_process.memory_info()
    else:
        raise ValueError(
            "Wrong value for parameter 'solver_library', shoud be in {'mkl', 'umfpack', 'superlu'}, got {} instead.".
            format(solver_library))

    xe = np.ones((A.shape[1], ))
    elapsed_time = (
        end_time - start_time).total_seconds() if not umfpack_mem_error else -1
    physical_memory = end_memory.rss - start_memory.rss if not umfpack_mem_error else -1
    virtual_memory = end_memory.vms - start_memory.vms if not umfpack_mem_error else -1
    relative_error = get_relative_error(xe, x) if not umfpack_mem_error else -1

    del xe
    gc.collect()

    return {
        'elapsed_time': elapsed_time,
        'memory_physical': physical_memory,
        'memory_virtual': virtual_memory,
        'relative_error': relative_error,
        'solver_library': solver_library,
        'matrix_dimensions': "{}x{}".format(A.shape[0], A.shape[1])
    }


def main(matrices, library='umfpack', num_runs=30):
    """Launch analysis for every matrix.
    Makes num_runs different runs loading each matrix every time to prevent
    smart caching from the solver libraries.

    Parameters
    ----------
    matrices: List[str]
        list of relative paths of matrix files
    
    library: str
        one of {'mkl', 'umfpack', 'superlu'}, defines the solver library
        to be used
    
    num_runs: int
        number of runs
    
    Returns
    -------
    results: Dics[str, List]
        dictionary with matrix names as keys, and list of result for each run
        as values
    """
    print("Discovered these matrices:")
    for m in matrices:
        print("{}".format(m))

    results = {m_path.split('/')[-1]: [] for m_path in matrices}

    for i in range(num_runs):
        print("\n## ------------------------ ##")
        print("Run {}/{} with all matrices".format(i + 1, num_runs))

        for index, path in enumerate(matrices):
            matrix_name = path.split('/')[-1]
            if library == 'mkl':
                A = load_matrix(path, 'csr')
            elif library == 'umfpack' or library == 'superlu':
                A = load_matrix(path, 'csc')

            print("Iter {}, matrix '{}' {}/{}, shape {}".format(
                i + 1, matrix_name, index + 1, len(matrices), A.shape))
            b = create_b(A)

            result = solve_with_profiling(A, b, solver_library=library)
            results[matrix_name].append(result)

            del A, b
            gc.collect()
            print("GC collection finished, next run...")

    print("\nDone!")
    return results


def postprocess(results: Dict[str, Union[str, float]]):
    """Postprocessing."""
    post = {
        matrix_name: {key: []
                      for key in results[matrix_name][0]}
        for matrix_name in results
    }

    for matrix_name in post:
        for run_result in results[matrix_name]:
            for key in run_result:
                post[matrix_name][key].append(run_result[key])

    return post


def log_results(results, num_runs, filepath='./log.csv'):
    """Write the results on a file."""
    if not results:
        return None

    csv_fields = [
        'matrix',
        'dimensions',
        'type',
        'iter',
        'time_mean',
        'time_variance',
        'mem_mean',  # in bytes
        'mem_variance',  # in bytes
        'rel_error',
        'system',
        'language',
        'library',
    ]

    # se non esiste il file, crealo con le colonne giuste
    myfile = pathlib.Path(filepath)
    if not myfile.is_file():
        with open(filepath, 'w') as outfile:
            outfile.write(",".join(csv_fields) + "\n")

    csv_rows = []
    for matrix_name in results_sdf:
        dimensions = results[matrix_name]['matrix_dimensions'][0]
        time = results[matrix_name]['elapsed_time']
        memory = np.array(results[matrix_name]['memory_physical'])
        error = results[matrix_name]['relative_error'][0]
        system = 'Ubuntu' if platform.system() == 'Linux' else 'Windows'
        language = 'Python'
        library = results[matrix_name]['solver_library'][0]

        csv_row = {
            'matrix': matrix_name,
            'dimensions': dimensions,
            'type': 'def_pos',
            'iter': num_runs,
            'time_mean': np.mean(time),
            'time_variance': np.var(time),
            'mem_mean': np.mean(memory[memory > 0]),
            'mem_variance': np.var(memory[memory > 0]),
            'rel_error': error,
            'system': system,
            'language': language,
            'library': library,
        }
        csv_rows.append(csv_row)

    with open(filepath, 'a') as outfile:
        print("Saving to {}".format(filepath))
        w = csv.DictWriter(outfile, delimiter=',', fieldnames=csv_fields)
        for row in csv_rows:
            w.writerow(row)
        print("Saved!")


if __name__ == '__main__':
    if len(sys.argv) == 3:
        library = sys.argv[1]
        n_runs = int(sys.argv[2])
    else:
        raise ValueError(
            "Please, provide a choice for the solver library an run number:" +
            "you should call this script as 'python scratch.py solver runs' where solver is {'mkl', 'superlu', 'umfpack'} and runs an integer > 0."
        )

    library = sys.argv[1]
    if library not in {'umfpack', 'superlu', 'mkl'}:
        raise ValueError(
            "Accepted values for library are: 'mkl', 'superlu', 'umfpack', got {} instead.".
            format(library))

    symmetric_matrices = sorted(glob.glob('./data/matrici_def_pos/*.mtx'))
    sdf = main(symmetric_matrices, library=library, num_runs=n_runs)
    results_sdf = postprocess(sdf)

    unsymmetric_matrices = sorted(
        glob.glob('./data/matrici_non_def_pos/*.mtx'))
    results_unsym = main(
        unsymmetric_matrices, library=library, num_runs=n_runs)

    log_results(results_sdf, n_runs)
    log_results(results_unsym, n_runs)
