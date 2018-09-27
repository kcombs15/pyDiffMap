# -*- coding: utf-8 -*-
"""
Utilities for constructing diffusion maps.
"""
import numpy as np
import scipy.sparse as sps

def lookup_fxn(x, vals):
    """
    Builds a simple function that acts as a lookup table.  Useful for
    constructing bandwidth and weigth functions from existing values.

    Parameters
    ----------
    x : iterable
        values to input for the function
    vals : iterable
        Output values for the function.  Must be of the same length as x.

    Returns
    -------
    lf : function
        A function that, when input a value in x, outputs the corresponding
        value in vals.
    """
    # Build dictionary
    lookup = {}
    for i in range(len(x)):
        lookup[str(x[i])] = vals[i]

    # Define and return lookup function
    def lf(xi):
        return lookup[str(xi)]

    return lf


def sparse_from_fxn(neighbors, function, Y=None):
    """
    For a function f, constructs a sparse matrix where each element is
    f(Y_i, X_j) if Y_i is a k-nearest neighbor to X_j, and zero otherwise.

    Parameters
    ----------
    neighbors : scikit-learn NearestNeighbors object
        Data structure containing the nearest neighbor information.
        X values are drawn from the data in this object.
    function : function
        Function to apply to the pair Y_i, X_j.  Must take only two arguments
        and return a number.
    Y : iterable or None
        Values corresponding to each column of the matrix.  If None, defaults
        to the data in the neighbors object.

    Returns
    -------
    M : scipy sparse csr matrix
        Matrix with elements f(Y_i, X_j) for nearest neighbors, and zero
        otherwise.  Here Y_i is the i'th datapoint in Y, and X_j is the
        j'th datapoint in the NearestNeighbors object.
    """
    X = neighbors._fit_X
    if Y is None:
        Y = X
    knn_graph = neighbors.kneighbors_graph(Y, mode='connectivity').tocoo()
    row = knn_graph.row
    col = knn_graph.col

    fxn_vals = []
    for i, j in zip(row, col):
        fxn_vals.append(function(Y[i], X[j]))
    fxn_vals = np.array(fxn_vals)

    return sps.csr_matrix((fxn_vals, (row, col)), shape=knn_graph.shape)
