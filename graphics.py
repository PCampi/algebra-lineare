"""Documento per grafici del progetto 1."""
import pandas as ps
from matplotlib import pyplot as plt


def calculate_col_v_memory_mean(t_start, t_stop, mem_log):
    mem_mean = 0
    memory_col = mem_log[mem_log['timestamp'] >= t_start]
    memory_col = memory_col[memory_col['timestamp'] <= t_stop]
    mem_mean = memory_col['memory_virtual(kB)'].max(
    ) - memory_col['memory_virtual(kB)'].min()
    return mem_mean


def calculate_col_p_memory_mean(t_start, t_stop, mem_log):
    mem_mean = 0
    memory_col = mem_log[mem_log['timestamp'] >= t_start]
    memory_col = memory_col[memory_col['timestamp'] <= t_stop]
    mem_mean = memory_col['memory_physical(kB)'].max(
    ) - memory_col['memory_physical(kB)'].min()
    return mem_mean


def calculate_mem_mean(matrix, log):
    mem_mean = 0
    memory_col = log[log['matrix'] == matrix]
    mem_mean = memory_col['memory'].max() - memory_col['memory'].min()
    return mem_mean


def create_python_dataframe(log, memory_log):
    python_dataframe = 0  #Da definire!
    current_mem_val = 0

    mem_values = []
    for index, row in log.iterrows():
        current_mem_val = calculate_col_p_memory_mean(row[3], row[4],
                                                      memory_log)
        mem_values.append(current_mem_val)
    log['memory'] = mem_values

    #FUNZIONE NON COMPLETA: manca da riuscire a raggruppare i dati delle matrici, ora sparsi per iterazione, e computare:
    # time_mean, time_var, memory, rel_error
    #Bisogna poi creare il nuovo dataframe completo da poter poi utilizzare per la costruzione dei grafi

    return python_dataframe


def create_graphics():
    #Documenti Ubuntu
    ubuntu_matlab_log = ps.read_csv(
        "./log_finali/ubuntu_matlab_log_file.csv",
        sep=', ',
        encoding="utf-8-sig")
    ubuntu_matlab_times = ps.read_csv(
        "./log_finali/ubuntu_matlab_times_log_file.csv",
        sep=', ',
        encoding="utf-8-sig")
    ubuntu_matlab_memory = ps.read_csv(
        "./log_finali/ubuntu_matlab_memory_log.csv",
        sep=',',
        encoding="utf-8-sig")

    ubuntu_python_log = ps.read_csv(
        "./log_finali/ubuntu_python_result_log.csv",
        sep=',',
        encoding="utf-8-sig")
    ubuntu_python_memory = ps.read_csv(
        "./log_finali/ubuntu_python_memory_log.csv",
        sep=',',
        encoding="utf-8-sig")

    #Documenti Windows
    windows_matlab_log = ps.read_csv(
        "./log_finali/windows_matlab_log_file.csv",
        sep=', ',
        encoding="utf-8-sig")
    windows_matlab_times = ps.read_csv(
        "./log_finali/windows_matlab_times_log_file.csv",
        sep=', ',
        encoding="utf-8-sig")
    windows_matlab_memory = ps.read_csv(
        "./log_finali/windows_matlab_memory_log.csv",
        sep=',',
        encoding="utf-8-sig")

    windows_python_log = ps.read_csv(
        "./log_finali/windows_python_result_log.csv",
        sep=',',
        encoding="utf-8-sig")
    windows_python_memory = ps.read_csv(
        "./log_finali/windows_python_memory_log.csv",
        sep=',',
        encoding="utf-8-sig")

    #Preparazione dati Matlab
    current_mem_val = 0

    ubuntu_first_mem_values = []
    for index, row in ubuntu_matlab_times.iterrows():
        current_mem_val = calculate_col_p_memory_mean(row[4], row[5],
                                                      ubuntu_matlab_memory)
        ubuntu_first_mem_values.append(current_mem_val)
    ubuntu_matlab_times['memory'] = ubuntu_first_mem_values

    ubuntu_final_mem_values = []
    for index, row in ubuntu_matlab_log.iterrows():
        current_mem_val = calculate_mem_mean(row[0], ubuntu_matlab_times)
        ubuntu_final_mem_values.append(current_mem_val)
    ubuntu_matlab_log['memory'] = ubuntu_final_mem_values

    windows_first_mem_values = []
    for index, row in windows_matlab_times.iterrows():
        current_mem_val = calculate_col_p_memory_mean(row[4], row[5],
                                                      windows_matlab_memory)
        windows_first_mem_values.append(current_mem_val)
    windows_matlab_times['memory'] = windows_first_mem_values

    windows_final_mem_values = []
    for index, row in windows_matlab_log.iterrows():
        current_mem_val = calculate_mem_mean(row[0], windows_matlab_times)
        windows_final_mem_values.append(current_mem_val)
    windows_matlab_log['memory'] = windows_final_mem_values

    print("Aggiunta memoria completata")

    #Preparazione dati Python
    ubuntu_python_final = create_python_dataframe(ubuntu_python_log,
                                                  ubuntu_python_memory)
    windows_python_final = create_python_dataframe(windows_python_log,
                                                   windows_python_memory)

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
