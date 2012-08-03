#!/usr/bin/python

"""
Surface calculations


Authors:  Arno Klein  .  arno@mindboggle.info  .  www.binarybottle.com

(c) 2012  Mindbogglers (www.mindboggle.info), under Apache License Version 2.0

"""

##############################################################################
#   Surface calculations
##############################################################################

def compute_depth(command, surface_file):
    """
    Measure Joachim Giard's "travel depth" for a surface mesh.
    """
    from os import path, getcwd
    from nipype.interfaces.base import CommandLine

    # Check type:
    if type(surface_file) == str:
        pass
    elif type(surface_file) == list:
        surface_file = surface_file[0]
    else:
        import sys
        sys.error("Check format of " + surface_file)

    depth_file = path.splitext(path.basename(surface_file))[0] + '.depth.vtk'
    cli = CommandLine(command = command)
    cli.inputs.args = ' '.join([surface_file, path.join(getcwd(), depth_file)])
    cli.cmdline
    cli.run()

    return depth_file

def compute_curvature(command, surface_file):
    """
    Measure curvatures for a surface mesh.
    """

    from os import path, getcwd
    from nipype.interfaces.base import CommandLine

    # Check type:
    if type(surface_file) == str:
        pass
    elif type(surface_file) == list:
        surface_file = surface_file[0]
    else:
        import sys
        sys.error("Check format of " + surface_file)

    stem = path.join(getcwd(), path.splitext(path.basename(surface_file))[0])
    mean_curvature_file = stem + '.curv.avg.vtk'
    gauss_curvature_file = stem + '.curv.gauss.vtk'
    max_curvature_file = stem + '.curv.max.vtk'
    min_curvature_file = stem + '.curv.min.vtk'
    min_curvature_vector_file = stem + '.curv.min.dir.txt'
    args = ['-g', gauss_curvature_file,
            '-x', max_curvature_file,
            '-i', min_curvature_file,
            '-d', min_curvature_vector_file,
            surface_file, mean_curvature_file]
    cli = CommandLine(command = command)
    cli.inputs.args = ' '.join(args)
    cli.cmdline
    cli.run()

    return mean_curvature_file, gauss_curvature_file,\
           max_curvature_file, min_curvature_file, min_curvature_vector_file