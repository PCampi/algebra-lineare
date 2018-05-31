function [ ] = solver_function( matrix, type )
%Funzione per la risoluzione di una matrice

    system = 'Windows';

    fprintf("Caricamento matrice: " + matrix + "... \n");
    [ A, rows, cols, entries, rep, field, symm ] = mm_to_msm("matrici_" + type + "\" + matrix);
    fprintf("Caricamento matrice: " + matrix + " completato! \n");

    times = [];
    errors = [];

    [m, n] = size(A);
    dimensions = m + "x" + n;
    xe = ones(m, 1);
    b = A*xe;

    x = 0;
    t = 0;
    
    for i = 1:30
        
        pid = feature('getpid');
        fprintf("Inizio risoluzione matrice: " + matrix + " " + i + "\n")

        tic;
        x = A\b;
        t = toc;

        fprintf("Fine risoluzione matrice: " + matrix + " " + i + "\n")
        times = [times t];

        abs_error = abs(xe-x);
        rel_error = abs_error/abs(x);
        errors = [errors rel_error];

    end
    
    times_mean = mean(times);
    times_var = var(times);
    errors_mean = mean(errors);
    
    fileID = fopen('log_file.txt','a+');
    fprintf(fileID,'%s, %s, %s, %d, %d, %d, %d, %s \r\n', ...
        matrix, dimensions, type, 30, times_mean, times_var, ...
        errors_mean, system);
    fclose(fileID);

end

