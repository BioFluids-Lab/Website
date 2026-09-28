---
title: Local solution acceleration method for the Euler and Navier-Stokes equations
authors:
- D. Drikakis
- Sokrates Tsangaris
date: '1992-01-01'
publishDate: '2026-08-30T08:44:56.871037Z'
publication_types:
- article-journal
publication: '*AIAA Journal*'
hugoblox:
  ids:
    doi: 10.2514/3.10924
abstract: The solution of the compressible Euler and Navier-Stokes equations via an
  upwind finite volume scheme is obtained. For the inviscid fluxes, the monotone upstream-centered
  scheme for conservation laws (MUSCL) has been incorporated into a Riemann solver.
  The MUSCL scheme is used for the unfactored implicit equations that are solved by
  a Newton form, and relaxation is performed via Gauss-Seidel relaxation technique.
  The solution on the fine grid is obtained by iterating first on a sequence of coarser
  grids and then interpolating the solution up to the next refined grid. Since the
  distribution of the numerical error is nonuniform, the local solution of the equations
  can be obtained in regions where the numerical errors are large. The construction
  of the partial meshes, in which the iterations will be continued, is determined
  by an adaptive procedure taking into account some convergence criteria. Reduction
  of the computational work units for two-dimensional problems is obtained via the
  local adaptive mesh solution which is expected to be more effective in three-dimensional
  complex flow computations. © 1992 American Institute of Aeronautics and Astronautics,
  Inc., All rights reserved.
links:
- name: URL
  url: https://doi.org/10.2514/3.10924
---
