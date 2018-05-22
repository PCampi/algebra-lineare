%% Caricamento e Conversione

%Cominciamo con l'importare la matrice da considerare
%NB La matrice è in formato Matrix Market

[ A, rows, cols, entries, rep, field, symm ] = mm_to_msm("cfd1.mtx");

%% Calcolo soluzione approssimata

%Dopo aver letto e convertito la matrice in formato MATLAB procediamo a
%calcolare il vettore b

[m, n] = size(A);
xe = ones(m, 1);
b = A*xe;

%Fatto questo calcoliamo quella che è la soluzione approssimata della 
%matrice sparsa

fprintf("Inizio risoluzione matrice. \n")
tic;
x = A\b;
t = toc;
fprintf("Fine risoluzione matrice. \n")

%% Calcolo errore relativo

%Dopo aver trovato la soluzione approssimata alla matrice, calcoliamo
%l'errore relativo operato dall'algoritmo di MATLAB nel trovare soluzione
%al sistema Ax=b

abs_error = abs(xe-x);
rel_error = abs(abs_error)\abs(x);