---
title: Development of an artificial compressibility methodology using flux vector
  splitting
authors:
- T.I. Pappou
- Sokrates Tsangaris
date: '1997-01-01'
publishDate: '2026-08-30T08:44:56.805700Z'
publication_types:
- article-journal
publication: '*International Journal for Numerical Methods in Fluids*'
hugoblox:
  ids:
    doi: 10.1002/(SICI)1097-0363(19970915)25:5<523::AID-FLD574>3.0.CO;2-E
abstract: An implicit, upwind arithmetic scheme that is efficient for the solution
  of laminar, steady, incompressible, two-dimensional flow fields in a generalised
  co-ordinate system is presented in this paper. The developed algorithm is based
  on the extended flux-vector-splitting (FVS) method for solving incompressible flow
  fields. As in the case of compressible flows, the FVS method consists of the decomposition
  of the convective fluxes into positive and negative parts that transmit information
  from the upstream and downstream flow field respectively. The extension of this
  method to the solution of incompressible flows is achieved by the method of artificial
  compressibility, whereby an artificial time derivative of the pressure is added
  to the continuity equation. In this way the incompressible equations take on a hyperbolic
  character with pseudopressure waves propagating with finite speed. In such problems
  the 'information' inside the field is transmitted along its characteristic curves.
  In this sense, we can use upwind schemes to represent the finite volume scheme of
  the problem's governing equations. For the representation of the problem variables
  at the cell faces, upwind schemes up to third order of accuracy are used, while
  for the development of a time-iterative procedure a first-order-accurate Euler backward-time
  difference scheme is used and a second-order central differencing for the shear
  stresses is presented. The discretized Navier-Stokes equations are solved by an
  implicit unfactored method using Newton iterations and Gauss-Siedel relaxation.
  To validate the derived arithmetical results against experimental data and other
  numerical solutions, various laminar flows with known behaviour from the literature
  are examined. © 1997 by John Wiley & Sons, Ltd.
links:
- name: URL
  url: 
    https://doi.org/10.1002/(SICI)1097-0363(19970915)25:5%3C523::AID-FLD574%3E3.0.CO;2-E
---
