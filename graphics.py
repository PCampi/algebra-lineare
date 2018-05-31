"""Documento per grafici del progetto 1."""
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

MATRIX_NNZ = {
    'graham1.mtx': 335504,
    'raefsky3.mtx': 1488768,
    'ex15.mtx': 98671,
    'ex19.mtx': 259879,
    'torso1.mtx': 8516500,
    'water_tank.mtx': 2035281,
    'cfd1.mtx': 1828364,
    'PR02R.mtx': 8185136,
    'cfd2.mtx': 3087898,
    'torso3.mtx': 4429042,
    'shallow_water1.mtx': 327680,
    'parabolic_fem.mtx': 3674625,
    'apache2.mtx': 4817870,
    'G3_circuit.mtx': 7660826
}


def calculate_col_v_memory_mean(t_start, t_stop, mem_log):
    mem_mean = 0
    memory_col = mem_log[mem_log['timestamp'] >= t_start]
    memory_col = memory_col[memory_col['timestamp'] <= t_stop]
    mem_mean = memory_col['memory_virtual(kB)'].max(
    ) - memory_col['memory_virtual(kB)'].min()
    return mem_mean


def calculate_col_p_memory_maxmin(t_start, t_stop, mem_log):
    """Calculate the max difference in memory used between timestamps.

    Parameters
    ----------
    t_start: float
        start time
    
    t_stop: float
        end time
    
    mem_log: pandas.DataFrame
        dataframe containing columns 'timestamp' and 'memory_physical(kB)'
    
    Returns
    -------
    used_memory: float
        max(memory) - min(memory) during the time span between start and stop
    """
    m = mem_log.query('timestamp >= @t_start and timestamp <= @t_stop')
    used_memory = m['memory_physical(kB)'].max()\
                - m['memory_physical(kB)'].min()

    return used_memory


def calculate_mem_maxmin(matrix_name, data) -> int:
    memory_col = data[data['matrix'] == matrix_name]['memory']
    used_mem = memory_col.max() - memory_col.min()
    return used_mem


def create_python_dataframe(run_log, memory_log):
    """Create a result DataFrame for Python."""
    columns = [
        'matrix', 'dimensions', 'type', 'iter', 'times_mean', 'times_var',
        'rel_error', 'system', 'memory'
    ]
    new_df = pd.DataFrame(columns=columns)

    matrix_names = np.unique(run_log['matrix'])
    dimensions = [
        run_log[run_log['matrix'] == name]['dimensions'].iloc[0]
        for name in matrix_names
    ]
    types = [
        run_log[run_log['matrix'] == name]['type'].iloc[0]
        for name in matrix_names
    ]
    rel_error = [
        run_log[run_log['matrix'] == name]['rel_error'].iloc[0]
        for name in matrix_names
    ]
    system = [
        'Ubuntu' if run_log['system'].iloc[0] == 'ubuntu' else 'Windows'
    ] * len(matrix_names)
    iters = [30] * len(matrix_names)

    memory_mean = []
    memory_var = []
    times_mean = []
    times_var = []
    for name in matrix_names:
        start_times = run_log[run_log['matrix'] == name]['start_time']
        end_times = run_log[run_log['matrix'] == name]['end_time']
        elapsed = (end_times - start_times).values
        times_mean.append(np.mean(elapsed))
        times_var.append(np.var(elapsed))
        mem = []
        for start_time, end_time in zip(start_times, end_times):
            m = memory_log.query(
                'timestamp >= @start_time and timestamp <= @end_time')
            used_memory = m['memory_physical(kB)'].max()\
                        - m['memory_physical(kB)'].min()
            mem.append(used_memory)
        memory_mean.append(np.mean(mem))
        memory_var.append(np.var(mem))

    new_df.loc[:, 'matrix'] = matrix_names
    new_df.loc[:, 'dimensions'] = dimensions
    new_df.loc[:, 'type'] = types
    new_df.loc[:, 'iter'] = iters
    new_df.loc[:, 'times_mean'] = times_mean
    new_df.loc[:, 'times_var'] = times_var
    new_df.loc[:, 'rel_error'] = rel_error
    new_df.loc[:, 'system'] = system
    new_df.loc[:, 'memory'] = memory_mean

    return new_df


def create_graphics():
    # Documenti Ubuntu
    ubuntu_matlab_log = pd.read_csv(
        "./log_finali/ubuntu_matlab_log_file.csv",
        sep=', ',
        encoding="utf-8-sig")
    ubuntu_matlab_times = pd.read_csv(
        "./log_finali/ubuntu_matlab_times_log_file.csv",
        sep=', ',
        encoding="utf-8-sig")
    ubuntu_matlab_memory = pd.read_csv(
        "./log_finali/ubuntu_matlab_memory_log.csv",
        sep=',',
        encoding="utf-8-sig")

    ubuntu_python_all_runs = pd.read_csv(
        "./log_finali/ubuntu_python_result_log.csv",
        sep=',',
        encoding="utf-8-sig")
    ubuntu_python_memory = pd.read_csv(
        "./log_finali/ubuntu_python_memory_log.csv",
        sep=',',
        encoding="utf-8-sig")

    # Documenti Windows
    windows_matlab_log = pd.read_csv(
        "./log_finali/windows_matlab_log_file.csv",
        sep=', ',
        encoding="utf-8-sig")
    windows_matlab_times = pd.read_csv(
        "./log_finali/windows_matlab_times_log_file.csv",
        sep=', ',
        encoding="utf-8-sig")
    windows_matlab_memory = pd.read_csv(
        "./log_finali/windows_matlab_memory_log.csv",
        sep=',',
        encoding="utf-8-sig")

    windows_python_all_runs = pd.read_csv(
        "./log_finali/windows_python_result_log.csv",
        sep=',',
        encoding="utf-8-sig")
    windows_python_memory = pd.read_csv(
        "./log_finali/windows_python_memory_log.csv",
        sep=',',
        encoding="utf-8-sig")

    #Preparazione dati Matlab

    ubuntu_matlab_times['memory'] = [
        calculate_col_p_memory_maxmin(r[4], r[5], ubuntu_matlab_memory)
        for _, r in ubuntu_matlab_times.iterrows()
    ]

    ubuntu_matlab_log['memory'] = [
        calculate_mem_maxmin(matrix_name, ubuntu_matlab_times)
        for matrix_name in ubuntu_matlab_log['matrix']
    ]

    windows_matlab_times['memory'] = [
        calculate_col_p_memory_maxmin(r[4], r[5], windows_matlab_memory)
        for _, r in windows_matlab_times.iterrows()
    ]

    windows_matlab_log['memory'] = [
        calculate_mem_maxmin(matrix_name, windows_matlab_times)
        for matrix_name in windows_matlab_log['matrix']
    ]

    ubuntu_matlab_log.to_csv('./dati_grafici/matlab_ubuntu.csv')
    windows_matlab_log.to_csv('./dati_grafici/matlab_windows.csv')

    print("Aggiunta memoria completata")

    #Preparazione dati Python
    ubuntu_python_final = create_python_dataframe(ubuntu_python_all_runs,
                                                  ubuntu_python_memory)
    windows_python_final = create_python_dataframe(windows_python_all_runs,
                                                   windows_python_memory)

    ubuntu_python_final.to_csv('./dati_grafici/python_ubuntu.csv')
    windows_python_final.to_csv('./dati_grafici/python_windows.csv')

    #Da qui i grafici di matlab possono essere fatti solo con ubuntu_matlab_log e windows_matlab_log
    #PS C'è sempre il problema che alcune matrici sembrano aver girato utilizzando zero memoria
    #quindi è da controllare se le funzioni che ho fatto io sono giuste (sotto è utilizzata quella della memoria fisica)
    #oppure se per sfortuna alcuni processi sembrano usare proprio pochissima memoria

    #Questo codice qui sotto mette tutti insieme i plot per matlab (quindi sia di ubuntu che di windows)
    #Mancano quelli di python per cui non sono riuscita a terminare la funzione per creare un dataset utile
    #Poi vedi tu come è meglio che vengano messi, non ho ricontrollato specificatamente la consegna
    #Magari anche differenziarli di più di quanto non abbia fatto io
    fig, axs = plt.subplots(nrows=1, ncols=1, figsize=(16, 7))
    axs.yaxis.grid(linestyle='--')
    axs.spines["top"].set_visible(False)
    axs.spines["right"].set_visible(False)

    axs.set_xlabel('Matrici utilizzate')

    axs.plot(
        ubuntu_matlab_log['matrix'],
        ubuntu_matlab_log['times_mean'],
        marker='o',
        color='skyblue',
        linewidth=2,
        label='Tempo medio Matlab Ubuntu')
    axs.plot(
        windows_matlab_log['matrix'],
        windows_matlab_log['times_mean'],
        marker='o',
        color='dodgerblue',
        linewidth=2,
        label='Tempo medio Matlab Windows')
    axs.plot(
        ubuntu_matlab_log['matrix'],
        ubuntu_matlab_log['memory'],
        marker='o',
        color='lightcoral',
        linewidth=2,
        label='Memoria usata Matlab Ubuntu')
    axs.plot(
        windows_matlab_log['matrix'],
        windows_matlab_log['memory'],
        marker='o',
        color='tomato',
        linewidth=2,
        label='Memoria usata Matlab Windows')
    axs.plot(
        ubuntu_matlab_log['matrix'],
        ubuntu_matlab_log['rel_error'],
        marker='o',
        color='lightgreen',
        linewidth=2,
        label='Errore relativo Matlab Ubuntu')
    axs.plot(
        windows_matlab_log['matrix'],
        windows_matlab_log['rel_error'],
        marker='o',
        color='forestgreen',
        linewidth=2,
        label='Errore relativo Matlab Windows')

    axs.legend()
    plt.title('Comparazione risoluzione matrici su Matlab')
    plt.yscale('log')
    plt.show()


if __name__ == '__main__':
    create_graphics()
