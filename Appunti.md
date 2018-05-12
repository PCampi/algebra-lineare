# Appunti per il progetto

## Matrici

- cfd1: occhio che sono diverse quelle scaricate in formato Matlab e quelle in formato Matrix Market come numero di elementi, però la loro somma è uguale! -> teniamo quelle in formato *Matrix Market*

## Scipy.sparse

Occhio che non supporta le matrici simmetriche in formato Harwell-Boeing.

Usiamo sia SuperLU che UMFPACK con la keyword use_umfpack in `scipy.sparse.linalg.spsolve`

**Attenzione** citando la doc di scipy:

*For solving the matrix expression AX = B, this solver assumes the resulting matrix X is sparse, as is often the case for very sparse inputs. If the resulting X is dense, the construction of this sparse result will be relatively expensive. In that case, consider converting A to a dense matrix and using scipy.linalg.solve or its variants.*

Comunque, con la matrice `cfd1`, se la converto a densa e poi uso `scipy.linalg.solve(A_dense, b, assume_a='pos')` ci mette più di 3 minuti, mentre la sparsa con umfpack impiega circa 6 secondi.
