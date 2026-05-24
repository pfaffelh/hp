# Master thesis: Prior-Data Fitted Networks and Martingale Posteriors (June 2026)

Summary of [arXiv:2505.11325](https://arxiv.org/abs/2505.11325):
Prior-data fitted networks (PFNs) have emerged as promising foundation
models for prediction from tabular datasets, achieving
state-of-the-art performance on small to moderate data sizes without
tuning. While PFNs are motivated by Bayesian ideas, they do not
provide any uncertainty quantification for predictive means,
quantiles, or similar quantities. The paper proposes a principled,
efficient, and tuning-free sampling procedure to construct Bayesian
posteriors for such estimates based on martingale posteriors, and
proves its convergence. Several simulated and real-world data
examples showcase the efficiency and calibration of the method in
inference applications.

The thesis consists of placing martingale posterior distributions in
the framework of theoretical statistics and implementing them.
