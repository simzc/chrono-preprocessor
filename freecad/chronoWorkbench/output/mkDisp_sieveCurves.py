## ================================================================================
## CHRONO WORKBENCH - github.com/Concrete-Chrono-Development/chrono-preprocessor
##
## Copyright (c) 2023 
## All rights reserved. 
##
## Use of this source code is governed by a BSD-style license that can be found
## in the LICENSE file at the top level of the distribution and at
## github.com/Concrete-Chrono-Development/chrono-preprocessor/blob/main/LICENSE
##
## ================================================================================
## Developed by Northwestern University
## For U.S. Army ERDC Contract No. W9132T22C0015
## Primary Authors: Matthew Troemner
## ================================================================================
##
## This file contains the function to generate and display sieve curves for the 
## input sieve curve and generated particle size distribution.
##
## ================================================================================

# pyright: reportMissingImports=false
try:
    from FreeCAD.Plot import Plot
except ImportError:
    from freecad.plot import Plot
import numpy as np
import math


def mkDisp_sieveCurves(volFracPar, tetVolume, minPar, maxPar,fullerCoef,sieveCurveDiameter,sieveCurvePassing,parDiameterList):

    """
    Variable List:
    --------------------------------------------------------------------------
    ### Inputs ###
    volFracPar:              Volume fraction of particles in the geometry
    tetVolume:               Volume of the tetrahedral mesh
    minPar:                  Minimum particle diameter
    maxPar:                  Maximum particle diameter
    fullerCoef:              Fuller coefficient of the input particle size distribution
    sieveCurveDiameter:          List of diameters for the input sieve curve
    sieveCurvePassing:          List of percent passing for the input sieve curve
    parDiameterList:         List of diameters for the generated particle size distribution
    --------------------------------------------------------------------------
    ### Outputs ###
    Display of the input sieve curve and generated particle size distribution
    --------------------------------------------------------------------------
    """

    # Generate plot of sieve curve
    Plot.figure("Particle Sieve Curve")

    # Get volume of small particles and generated particles
    totalVol = sum(4/3*math.pi*(parDiameterList/2)**3)
    volParticles=volFracPar*tetVolume;
    volExtra=volParticles-totalVol;

    # Initialize Diameters
    parDiameterList = np.flip(parDiameterList)
    diameters = np.linspace(0,maxPar,num=1000)
    passingPercent=np.zeros(1000)
    passingPercentTheory=np.zeros(1000)

    # Get Passing Percent of Placed Particles
    for x in range(1000):
        passing=parDiameterList[parDiameterList<diameters[x]]
        vol=sum(4/3*math.pi*(passing/2)**3)+volExtra
        passingPercent[x]=vol/volParticles*100

    # Calculations for sieve curve plotting for shifted generated particle size distribution (for comparison with Fuller Curve)
    if fullerCoef != 0:
        # Generate values for small particles
        diametersTheory = diameters
        passingPercentTheory=100*(diametersTheory/maxPar)**fullerCoef

    else:
        # Reformat sieve curve into numpy arrays for interpolation
        diametersTheory = np.asarray(sieveCurveDiameter, dtype=np.float32)
        passingPercentTheory = np.asarray([x*100 for x in sieveCurvePassing], dtype=np.float32)

        # Get Interpolated passingPercentTheory value for largest diameter in generated particle size distribution
        # This is used to shift the generated particle size distribution to match the input sieve curve
        for x in range(len(diametersTheory)):
            if diametersTheory[x+1] == maxPar:
                shiftValue = passingPercent[999]-passingPercentTheory[x+1]
                break
            elif (diametersTheory[x] <= maxPar) and (diametersTheory[x+1] >= maxPar):
                shiftValue = passingPercent[999]-(passingPercentTheory[x] + (passingPercentTheory[x+1]-passingPercentTheory[x])/(diametersTheory[x+1]-diametersTheory[x])*(maxPar-diametersTheory[x]))
                break
            else:
                shiftValue = 0

        # Shift passingPercent by shiftValue
        passingPercent = passingPercent - shiftValue

    # Plotting
    Plot.plot(diametersTheory, passingPercentTheory, 'Theoretical Curve') 
    Plot.plot(diameters[passingPercent>min(passingPercent)], passingPercent[passingPercent>min(passingPercent)], 'Simulated Data (Shifted Up)') 

    # Plotting Formatting
    Plot.xlabel('Particle Diameter, $d$ (mm)') 
    Plot.ylabel('Percent Passing, $P$ (%)')
    Plot.grid(True)
    Plot.legend() 

