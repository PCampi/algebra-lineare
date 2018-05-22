%% Caricamento e conversione matrice MM
clear all;
matrix = "cfd1.mtx";
type = 'def_pos';
fprintf("Caricamento matrice: " + matrix + "... \n");
[ A, rows, cols, entries, rep, field, symm ] = mm_to_msm("matrici_" + type + "\" + matrix);
fprintf("Caricamento matrice: " + matrix + " completato! \n");
system = "Windows";
language = "Matlab";
library = "Matlab";

%% Calcolo soluzione approssimata
times = [];
memory_used = [];
errors = [];

[m, n] = size(A);
dimensions = m + "x" + n;
xe = ones(m, 1);
b = A*xe;

x = 0;
t = 0;
mem = 0;

for i = 1:30
    
%     pid = feature('getpid');
%     m_tic = py.mem_monitor.mem_mon(int64(pid));
    fprintf("Inizio risoluzione matrice: " + matrix + " " + i + "\n")
    tic;
    x = A\b;
%     m_toc = py.mem_monitor.mem_mon(int64(pid));
    t = toc;
    fprintf("Fine risoluzione matrice: " + matrix + " " + i + "\n")
%     mem = double(m_toc) - double(m_tic);
    times = [times t];
    memory_used = [memory_used mem];

    abs_error = abs(xe-x);
    rel_error = abs(abs_error)\abs(x);
    errors = [errors rel_error];

end

times_mean = mean(times);
times_var = var(times);
memory_mean = mean(memory_used);
errors_mean = mean(errors);

%% Scrittura del log
mem_mean_conv = string(py.number_converter.bytes2human(memory_mean));
fileID = fopen('log_file.txt','a+');
fprintf(fileID,'%s, %s, %s, %d, %d, %d, %s, %d, %s, %s, %s \r\n', ...
    matrix, dimensions, type, 30, times_mean, times_var, mem_mean_conv, ...
    errors_mean, system, language, library);
fclose(fileID);
fprintf("Scrittura log completata! \n")