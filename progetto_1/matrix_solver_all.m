%% Creazione del file di log
fileID = fopen('log_file.txt','w');
fprintf(fileID,'%s %s %s %s %s %s %s %s \r\n','matrix,', ...
'dimensions,', 'type,', 'iter,', 'time_mean,', 'time_var,', ...
'rel_error,', 'system');
fclose(fileID);

%% Pulizia workspace
clear all;

%% Parte matrici_def_pos
folder_def_pos = dir('matrici_def_pos\*.mtx');
for i=1:size(folder_def_pos, 1)
    name_def_pos = folder_def_pos(i).name;
    solver_function( name_def_pos, 'def_pos' );
end

%% Parte matrici_non_def_pos
folder_non_def_pos = dir('matrici_non_def_pos\*.mtx');
for i=1:size(folder_non_def_pos, 1)
    name_non_def_pos = folder_non_def_pos(i).name;
    solver_function( name_non_def_pos, 'non_def_pos' );
end
