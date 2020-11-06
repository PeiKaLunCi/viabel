import numpy as np

from viabel.approximations import MFGaussian
from viabel.models import Model, StanModel
from viabel.objectives import ExclusiveKL
from viabel.optimization import adagrad_optimize


def bbvi(dimension, n_iters=10000, num_mc_samples=10, log_density=None, approx=None, objective=None, fit=None,  **kwargs):
    """Fit a model using black-box variational inference.

    Currently the objective is optimized using ``viabel.optimization.adagrad_optimize``.

    Parameters
    ----------
    dimension : `int`
        Dimension of the model parameter.
    n_iters : `int`
        Number of iterations of the optimization.
    num_mc_samples : `int`
        Number of Monte Carlo samples to use for estimating the gradient of
        the objective.
    log_density : `function`
        (Unnormalized) log density of the model. Must support automatic
        differentiation with ``autograd``. Either ``log_density`` or ``fit``
        must be provided.
    approx : `ApproximationFamily` object
        The approximation family. The default is to use ``viabel.approximations.MFGaussian``.
    objective : `function`
        Function for constructing the objective and gradient function. The default is
        to use ``viabel.objectives.ExclusiveKL``.
    fit : `StanFit4model` object
        If provided, a ``StanModel`` will be used. Both ``fit`` and
        ``log_density`` cannot be given.
    **kwargs
        Keyword arguments to pass to ``adagrad_optimize``.

    Returns
    -------
    results : `dict`
        Dictionary containing the results.
    """
    if log_density is None:
        if fit is None:
            raise ValueError('either log_density or fit must be specified')
        if objective is not None:
            raise ValueError('objective can only be specified if log_density is too')
        model = StanModel(fit)
    elif fit is None:
        model = Model(log_density)
    else:
        raise ValueError('log_density and fit cannot both be specified')

    if approx is None:
        if objective is not None:
            raise ValueError('objective can only be specified if approx is too')
        approx = MFGaussian(dimension)
    if objective is None:
        objective = ExclusiveKL(approx, log_density, num_mc_samples)
    init_param = np.zeros(approx.var_param_dim)
    var_param, var_param_history, _, _ = adagrad_optimize(n_iters, objective, init_param, **kwargs)
    results = dict(var_param=var_param,
                   var_param_history=var_param_history,
                   objective=objective)
    return results