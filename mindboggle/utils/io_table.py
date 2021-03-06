#!/usr/bin/env python
"""
Functions for writing tables


Authors:
    - Arno Klein, 2012-2013  (arno@mindboggle.info)  http://binarybottle.com
    - Forrest Sheng Bao, 2012  (forrest.bao@gmail.com)  http://fsbao.net

Copyright 2013,  Mindboggle team (http://mindboggle.info), Apache v2.0 License

"""

def read_columns(filename, n_columns=1, trail=False):
    """
    Read n-column text file. Assumes space(s) as delimiter.

    Parameters
    ----------
    filename :  name of text file [string]
    n_columns :  number of columns to extract [integer]
    trail :  combine all remaining columns as a string
             in the final list [Boolean]

    Returns
    -------
    columns :  a list of lists of strings, one list per column of text.

    """
    import re

    Fp = open(filename, 'r')
    lines = Fp.readlines()
    columns = [[] for x in range(n_columns)]
    for line in lines:
        if line:
            row = re.findall(r'\S+', line)
            if len(row) >= n_columns:
                for icolumn in range(n_columns):
                    if trail and icolumn == n_columns - 1:
                        columns[icolumn].append(' '.join(row[icolumn::]))
                    else:
                        columns[icolumn].append(row[icolumn])
            else:
                import os
                os.error('The number of columns in {0} is less than {1}.'.format(
                         filename, n_columns))
    Fp.close()

    return columns

def write_columns(columns, column_names, output_table, delimiter=',',
                  quote=True, input_table=''):
    """
    Write table with columns and column names.  Assumes space(s) as delimiter.

    If there is an input table file to append to, assume a 1-line header.

    Parameters
    ----------
    columns :  list of lists of floats or integers
        values (each list is a column of values)
    column_names :  list of strings
        names of columns
    output_table : string
        name of output table file
    delimiter : string
        delimiter between columns, such as ','
    bracket : string
        string bracketing each element, such as '"'
    input_table : string (default is empty string)
        name of table file to which the columns are to be appended

    Returns
    -------
    output_table : string
        name of output table file

    Examples
    --------
    >>> from mindboggle.utils.io_table import write_columns
    >>> labels = ['category one', 'category two', 'category three', 'category four']
    >>> values = [0.12, 0.36, 0.75, 0.03]
    >>> values2 = [32, 87, 53, 23]
    >>> columns = [labels, values]
    >>> column_names = ['label', 'value']
    >>> output_table = 'write_columns.csv'
    >>> delimiter = ','
    >>> quote = True
    >>> input_table = ''
    >>> write_columns(columns, column_names, output_table, delimiter, quote, input_table)
    >>> write_columns(values2, 'value 2', output_table, delimiter,
    >>>               quote, input_table=output_table)

    """
    import os
    import sys
    from mindboggle.utils.io_table import read_columns

    output_table = os.path.join(os.getcwd(), output_table)
    if quote:
        q = '"'
    else:
        q = ''

    #-----------------------
    # Check format of inputs
    #-----------------------
    # If the list contains integers or floats, put in a list:
    if columns:
        if isinstance(columns[0], int) or isinstance(columns[0], float) or \
           isinstance(columns[0], str):
            columns = [columns]
        # If the list contains all lists, accept format:
        elif all([isinstance(x, list) for x in columns]):
            pass
        else:
            print("Error: columns contains unacceptable elements.")
            print("columns type is: {0}".format(type(columns)))
            print("columns length is: {0}".format(len(columns)))
            print("columns[0] type is: {0}".format(type(columns[0])))
            sys.exit()
        # If column_names is a string, create a list containing
        # as many of this string as there are columns.
        if isinstance(column_names, str):
            column_names = [column_names for x in columns]
        elif isinstance(column_names, list):
            if len(column_names) < len(columns):
                column_names = [column_names[0] for x in columns]
            else:
                pass
        else:
            print("Error: column_names is neither a list nor a string")
            sys.exit()

        #-----------------------------------
        # Read columns from input table file
        #-----------------------------------
        if input_table:
            input_columns = read_columns(input_table, n_columns=1, trail=True)
            input_names = input_columns[0][0]
            input_columns = input_columns[0][1::]
        #else:
        #    input_names = ''
        #    input_columns = ['' for x in columns[0]]

        #--------------
        # Write to file
        #--------------
        Fp = open(output_table, 'wa')
        if column_names:
            column_names = [q+x+q for x in column_names]
            if input_table:
                Fp.write(delimiter.join([input_names,
                                         delimiter.join(column_names) + "\n"]))
            else:
                Fp.write(delimiter.join(column_names) + "\n")
        #else:
        #    Fp.write(input_names + "\n")

        for irow in range(len(columns[0])):
            if input_table:
                Fp.write(input_columns[irow] + delimiter)
            for icolumn, column in enumerate(columns):
                if icolumn < len(columns)-1:
                    Fp.write('{0}{1}{2}{3}'.format(
                        q, column[irow], q, delimiter))
                else:
                    Fp.write('{0}{1}{2}'.format(q, column[irow], q))
            Fp.write("\n")

        Fp.close()

    else:
        print("NOTE: 'columns' is empty. Nothing written.")

    return output_table

def write_rows(filename, list_of_lines, header=""):
    """
    Write a list to a file, one line per list element.

    Parameters
    ----------
    filename : string
        name of output file
    list_of_lines :  list
        each element is written to file as a line
    header : string (default is empty string)
        header to write at the top of the file

    Returns
    -------
    filename : string
        name of output file

    """

    Fp = open(filename, 'w')

    if header:
        Fp.write(header + '\n')

    for element in list_of_lines:
        Fp.write(str(element) + '\n')

    Fp.close()

    return filename

def write_shape_stats(labels_or_file, sulci=[], fundi=[],
        affine_transform_file='', transform_format='itk',
        area_file='', mean_curvature_file='', travel_depth_file='',
        geodesic_depth_file='', convexity_file='', thickness_file='',
        labels_spectra=[], labels_spectra_IDs=[],
        sulci_spectra=[], sulci_spectra_IDs=[],
        exclude_labels=[-1], delimiter=','):
    """
    Make tables of shape statistics per label, fundus, and/or sulcus.

    Parameters
    ----------
    labels_or_file : list or string
        label number for each vertex or name of VTK file with index scalars
    sulci :  list of integers
        indices to sulci, one per vertex, with -1 indicating no sulcus
    fundi :  list of integers
        indices to fundi, one per vertex, with -1 indicating no fundus
    affine_transform_file : string
        affine transform file to standard space
    transform_format : string
        format for transform file
        Ex: 'txt' for text, 'itk' for ITK, and 'mat' for Matlab format
    area_file :  string
        name of VTK file with surface area scalar values
    mean_curvature_file :  string
        name of VTK file with mean curvature scalar values
    travel_depth_file :  string
        name of VTK file with travel depth scalar values
    geodesic_depth_file :  string
        name of VTK file with geodesic depth scalar values
    convexity_file :  string
        name of VTK file with convexity scalar values
    thickness_file :  string
        name of VTK file with thickness scalar values
    labels_spectra : list of lists of floats
        Laplace-Beltrami spectra for labeled regions
    labels_spectra_IDs : list of integers
        unique ID numbers (labels) for labels_spectra
    sulci_spectra : list of lists of floats
        Laplace-Beltrami spectra for sulci
    sulci_spectra_IDs : list of integers
        unique ID numbers (labels) for sulci_spectra
    exclude_labels : list of lists of integers
        indices to be excluded (in addition to -1)
    delimiter : string
        delimiter between columns, such as ','

    Returns
    -------
    label_table :  string
        output table filename for label shapes
    sulcus_table :  string
        output table filename for sulcus shapes
    fundus_table :  string
        output table filename for fundus shapes

    Examples
    --------
    >>> import os
    >>> from mindboggle.utils.io_vtk import read_scalars
    >>> from mindboggle.utils.io_table import write_shape_stats
    >>> path = os.environ['MINDBOGGLE_DATA']
    >>> labels_or_file = os.path.join(path, 'arno', 'labels', 'lh.labels.DKT25.manual.vtk')
    >>> sulci_file = os.path.join(path, 'arno', 'features', 'sulci.vtk')
    >>> fundi_file = os.path.join(path, 'arno', 'features', 'fundi.vtk')
    >>> sulci, name = read_scalars(sulci_file)
    >>> fundi, name = read_scalars(fundi_file)
    >>> affine_transform_file = os.path.join(path, 'arno', 'mri',
    >>> #    'affine_to_template.mat')
    >>>     't1weighted_brain.MNI152Affine.txt')
    >>> #transform_format = 'mat'
    >>> transform_format = 'itk'
    >>> area_file = os.path.join(path, 'arno', 'shapes', 'lh.pial.area.vtk')
    >>> mean_curvature_file = os.path.join(path, 'arno', 'shapes', 'lh.pial.mean_curvature.vtk')
    >>> travel_depth_file = os.path.join(path, 'arno', 'shapes', 'lh.pial.travel_depth.vtk')
    >>> geodesic_depth_file = os.path.join(path, 'arno', 'shapes', 'lh.pial.geodesic_depth.vtk')
    >>> convexity_file = ''
    >>> thickness_file = ''
    >>> delimiter = ','
    >>> #
    >>> import numpy as np
    >>> labels, name = read_scalars(labels_or_file)
    >>> labels_spectra = [[1,2,3] for x in labels]
    >>> labels_spectra_IDs = np.unique(labels).tolist()
    >>> sulci_spectra = [[1,2,3] for x in sulci]
    >>> sulci_spectra_IDs = np.unique(sulci).tolist()
    >>> exclude_labels = [-1]
    >>> #
    >>> write_shape_stats(labels_or_file, sulci, fundi,
    >>>     affine_transform_file, transform_format, area_file,
    >>>     mean_curvature_file, travel_depth_file, geodesic_depth_file,
    >>>     convexity_file, thickness_file, labels_spectra,
    >>>     labels_spectra_IDs, sulci_spectra,
    >>>     sulci_spectra_IDs, exclude_labels, delimiter)

    """
    import os
    import numpy as np
    from mindboggle.shapes.measure import means_per_label, stats_per_label, \
        sum_per_label
    from mindboggle.utils.io_vtk import read_scalars, read_vtk, \
        apply_affine_transform
    from mindboggle.utils.io_table import write_columns

    # Make sure inputs are lists:
    if isinstance(labels_or_file, np.ndarray):
        labels = labels_or_file.tolist()
    elif isinstance(labels_or_file, list):
        labels = labels_or_file
    elif isinstance(labels_or_file, str):
        labels, name = read_scalars(labels_or_file)
    if isinstance(sulci, np.ndarray):
        sulci = sulci.tolist()
    if isinstance(fundi, np.ndarray):
        fundi = fundi.tolist()

    #-------------------------------------------------------------------------
    # Feature lists, shape names, and shape files:
    #-------------------------------------------------------------------------
    # Feature lists:
    feature_lists = [labels, sulci, fundi]
    feature_names = ['label', 'sulcus', 'fundus']
    spectra_lists = [labels_spectra, sulci_spectra]
    spectra_ID_lists = [labels_spectra_IDs, sulci_spectra_IDs]
    spectra_names = ['label spectrum', 'sulcus spectrum']
    table_names = ['label_shapes.csv', 'sulcus_shapes.csv', 'fundus_shapes.csv']

    # Shape names corresponding to shape files below:
    shape_names = ['area', 'mean curvature', 'travel depth', 'geodesic depth',
                   'convexity', 'thickness']

    # Load shape files as a list of numpy arrays of per-vertex shape values:
    shape_files = [area_file, mean_curvature_file, travel_depth_file,
                   geodesic_depth_file, convexity_file, thickness_file]
    shape_arrays = []
    column_names = []
    first_pass = True
    area_array = []
    for ishape, shape_file in enumerate(shape_files):
        if os.path.exists(shape_file):
            if first_pass:
                faces, lines, indices, points, npoints, scalars_array, name, \
                    input_vtk = read_vtk(shape_file, True, True)
                points = np.array(points)
                first_pass = False
                if affine_transform_file:
                    affine_points, \
                        foo1 = apply_affine_transform(affine_transform_file,
                                    points, transform_format, save_file=False)
                    affine_points = np.array(affine_points)
            else:
                scalars_array, name = read_scalars(shape_file, True, True)
            if scalars_array.size:
                shape_arrays.append(scalars_array)

                # Store area array:
                if ishape == 0:
                    area_array = scalars_array.copy()

    # Initialize table file names:
    sulcus_table = None
    fundus_table = None

    # Loop through features / tables:
    for itable, feature_list in enumerate(feature_lists):
        table_column_names = []

        #---------------------------------------------------------------------
        # For each feature, construct a table of average shape values:
        #---------------------------------------------------------------------
        table_file = os.path.join(os.getcwd(), table_names[itable])
        if feature_list:
            feature_name = feature_names[itable]
            columns = []

            #-----------------------------------------------------------------
            # Mean positions in the original space:
            #-----------------------------------------------------------------
            # Compute mean position per feature:
            positions, sdevs, label_list, foo = means_per_label(points,
                feature_list, exclude_labels, area_array)

            # Append mean position per feature to columns:
            table_column_names.append('mean position')
            columns.append(positions)

            #-----------------------------------------------------------------
            # Mean positions in standard space:
            #-----------------------------------------------------------------
            if affine_transform_file:
                # Compute standard space mean position per feature:
                standard_positions, sdevs, label_list, foo = means_per_label(affine_points,
                    feature_list, exclude_labels, area_array)

                # Append standard space mean position per feature to columns:
                table_column_names.append('mean position in standard space')
                columns.append(standard_positions)

            #-----------------------------------------------------------------
            # Loop through shape measures:
            #-----------------------------------------------------------------
            table_column_names.extend(column_names[:])
            for ishape, shape_array in enumerate(shape_arrays):
                shape_name = shape_names[ishape]
                print('  Compute statistics on {0} {1}'.
                      format(feature_name, shape_name))

                # Append shape names and values per feature to columns:
                pr = feature_name + ": " + shape_name + ": "
                if np.size(area_array):
                    po = " (weighted)"
                else:
                    po = ""
                #-------------------------------------------------------------
                # Append total feature areas to columns:
                #-------------------------------------------------------------
                if ishape == 0 and np.size(area_array):
                    sums, label_list = sum_per_label(shape_array,
                        feature_list, exclude_labels)
                    table_column_names.append(pr + 'total')
                    columns.append(sums)
                #-------------------------------------------------------------
                # Append feature shape statistics to columns:
                #-------------------------------------------------------------
                else:
                    medians, mads, means, sdevs, skews, kurts, \
                    lower_quarts, upper_quarts, \
                    label_list = stats_per_label(shape_array,
                        feature_list, exclude_labels, area_array, precision=1)

                    table_column_names.append(pr + 'median' + po)
                    table_column_names.append(pr + 'median absolute deviation' + po)
                    table_column_names.append(pr + 'mean' + po)
                    table_column_names.append(pr + 'standard deviation' + po)
                    table_column_names.append(pr + 'skew' + po)
                    table_column_names.append(pr + 'kurtosis' + po)
                    table_column_names.append(pr + 'lower quartile' + po)
                    table_column_names.append(pr + 'upper quartile' + po)
                    columns.append(medians)
                    columns.append(mads)
                    columns.append(means)
                    columns.append(sdevs)
                    columns.append(skews)
                    columns.append(kurts)
                    columns.append(lower_quarts)
                    columns.append(upper_quarts)

            #-----------------------------------------------------------------
            # Laplace-Beltrami spectra:
            #-----------------------------------------------------------------
            if itable in [0,1]:
                spectra = spectra_lists[itable]
                spectra_name = spectra_names[itable]
                spectra_IDs = spectra_ID_lists[itable]

                # Order spectra into a list:
                spectrum_list = []
                for label in label_list:
                    if label in spectra_IDs:
                        spectrum = spectra[spectra_IDs.index(label)]
                        spectrum_list.append(spectrum)
                    else:
                        spectrum_list.append('')

                # Append spectral shape name and values to relevant columns:
                columns.append(spectrum_list)
                table_column_names.append(spectra_name)

            #-----------------------------------------------------------------
            # Write labels/IDs and values to table:
            #-----------------------------------------------------------------
            # Write labels/IDs to table:
            write_columns(label_list, feature_name, table_file, delimiter)

            # Append columns of shape values to table:
            if columns:
                write_columns(columns, table_column_names, table_file,
                              delimiter, quote=True, input_table=table_file)
        else:
            # Write something to table:
            write_columns([], '', table_file, delimiter)

        #---------------------------------------------------------------------
        # Return correct table file name:
        #---------------------------------------------------------------------
        if itable == 0:
            label_table = table_file
        elif itable == 1:
            sulcus_table = table_file
        elif itable == 2:
            fundus_table = table_file

    return label_table, sulcus_table, fundus_table


def write_vertex_measures(table_file, labels_or_file, sulci=[], fundi=[],
        affine_transform_file='', transform_format='itk',
        area_file='', mean_curvature_file='', travel_depth_file='',
        geodesic_depth_file='', convexity_file='', thickness_file='',
        delimiter=','):
    """
    Make a table of shape values per vertex.

    Parameters
    ----------
    table_file : output filename (without path)
    labels_or_file : list or string
        label number for each vertex or name of VTK file with index scalars
    sulci :  list of integers
        indices to sulci, one per vertex, with -1 indicating no sulcus
    fundi :  list of integers
        indices to fundi, one per vertex, with -1 indicating no fundus
    affine_transform_file : string
        affine transform file to standard space
    transform_format : string
        format for transform file
        Ex: 'txt' for text, 'itk' for ITK, and 'mat' for Matlab format
    area_file :  string
        name of VTK file with surface area scalar values
    mean_curvature_file :  string
        name of VTK file with mean curvature scalar values
    travel_depth_file :  string
        name of VTK file with travel depth scalar values
    geodesic_depth_file :  string
        name of VTK file with geodesic depth scalar values
    convexity_file :  string
        name of VTK file with convexity scalar values
    thickness_file :  string
        name of VTK file with thickness scalar values
    delimiter : string
        delimiter between columns, such as ','

    Returns
    -------
    shape_table : table file name for vertex shape values

    Examples
    --------
    >>> import os
    >>> from mindboggle.utils.io_vtk import read_scalars
    >>> from mindboggle.tables.all_shapes import write_vertex_measures
    >>> #
    >>> table_file = 'vertex_shapes.csv'
    >>> path = os.environ['MINDBOGGLE_DATA']
    >>> labels_or_file = os.path.join(path, 'arno', 'labels', 'lh.labels.DKT25.manual.vtk')
    >>> sulci_file = os.path.join(path, 'arno', 'features', 'sulci.vtk')
    >>> fundi_file = os.path.join(path, 'arno', 'features', 'fundi.vtk')
    >>> sulci, name = read_scalars(sulci_file)
    >>> fundi, name = read_scalars(fundi_file)
    >>> affine_transform_file = os.path.join(path, 'arno', 'mri',
    >>>     't1weighted_brain.MNI152Affine.txt')
    >>> transform_format = 'itk'
    >>> area_file = os.path.join(path, 'arno', 'shapes', 'lh.pial.area.vtk')
    >>> mean_curvature_file = os.path.join(path, 'arno', 'shapes', 'lh.pial.mean_curvature.vtk')
    >>> travel_depth_file = os.path.join(path, 'arno', 'shapes', 'lh.pial.travel_depth.vtk')
    >>> geodesic_depth_file = os.path.join(path, 'arno', 'shapes', 'lh.pial.geodesic_depth.vtk')
    >>> convexity_file = ''
    >>> thickness_file = ''
    >>> delimiter = ','
    >>> #
    >>> write_vertex_measures(table_file, labels_or_file, sulci, fundi,
    >>>     affine_transform_file, transform_format, area_file,
    >>>     mean_curvature_file, travel_depth_file, geodesic_depth_file,
    >>>     convexity_file, thickness_file, delimiter)

    """
    import os
    import numpy as np
    from mindboggle.utils.io_vtk import read_scalars, read_vtk, apply_affine_transform
    from mindboggle.utils.io_table import write_columns

    # Make sure inputs are lists:
    if isinstance(labels_or_file, np.ndarray):
        labels = labels_or_file.tolist()
    elif isinstance(labels_or_file, list):
        labels = labels_or_file
    elif isinstance(labels_or_file, str):
        labels, name = read_scalars(labels_or_file)
    if isinstance(sulci, np.ndarray):
        sulci = sulci.tolist()
    if isinstance(fundi, np.ndarray):
        fundi = fundi.tolist()

    # Feature names and corresponding feature lists:
    feature_names = ['label', 'sulcus', 'fundus']
    feature_lists = [labels, sulci, fundi]

    # Shape names corresponding to shape files below:
    shape_names = ['area', 'mean curvature', 'travel depth', 'geodesic depth',
                   'convexity', 'thickness']

    # Load shape files as a list of numpy arrays of per-vertex shape values:
    shape_files = [area_file, mean_curvature_file, travel_depth_file,
                   geodesic_depth_file, convexity_file, thickness_file]

    # Append columns of per-vertex scalar values:
    columns = []
    column_names = []
    for ifeature, values in enumerate(feature_lists):
        if values:
            columns.append(values)
            column_names.append(feature_names[ifeature])

    first_pass = True
    for ishape, shape_file in enumerate(shape_files):
        if os.path.exists(shape_file):
            if first_pass:
                u1, u2, u3, points, u4, scalars, u5, u6 = read_vtk(shape_file)
                columns.append(points)
                column_names.append('coordinates')
                first_pass = False
                if affine_transform_file:
                    affine_points, \
                        foo1 = apply_affine_transform(affine_transform_file,
                                    points, transform_format)
                    columns.append(affine_points)
                    column_names.append('coordinates in standard space')
            else:
                scalars, name = read_scalars(shape_file)
            if len(scalars):
                columns.append(scalars)
                column_names.append(shape_names[ishape])

    # Prepend with column of indices and write table
    shapes_table = os.path.join(os.getcwd(), table_file)
    write_columns(range(len(columns[0])), 'index', shapes_table, delimiter)
    write_columns(columns, column_names, shapes_table, delimiter, quote=True,
                  input_table=shapes_table)

    return shapes_table


def write_face_vertex_averages(input_file, area_file='', delimiter=','):
    """
    Make table of average vertex values per face.

    Parameters
    ----------
    input_file : string
        name of VTK file with scalars to average
    area_file :  string
        name of VTK file with surface area scalar values
    delimiter : string
        delimiter between columns, such as ','

    Returns
    -------
    output_table :  string
        output table filename

    Examples
    --------
    >>> import os
    >>> from mindboggle.utils.io_vtk import read_scalars
    >>> from mindboggle.utils.io_table import write_face_vertex_averages
    >>> path = os.environ['MINDBOGGLE_DATA']
    >>> #input_file = os.path.join(path, 'arno', 'shapes', 'lh.pial.mean_curvature.vtk')
    >>> #input_file = os.path.join(path, 'arno', 'shapes', 'lh.pial.travel_depth.vtk')
    >>> input_file = os.path.join(path, 'arno', 'shapes', 'lh.thickness.vtk')
    >>> area_file = os.path.join(path, 'arno', 'shapes', 'lh.pial.area.vtk')
    >>> delimiter = ','
    >>> #
    >>> write_face_vertex_averages(input_file, area_file, delimiter)

    """
    import os
    import numpy as np

    from mindboggle.utils.io_vtk import read_vtk, read_scalars
    from mindboggle.utils.io_table import write_columns

    faces, lines, indices, points, npoints, scalars, name, \
        input_vtk = read_vtk(input_file, True, True)
    if area_file:
        area_scalars, name = read_scalars(area_file, True, True)

    #---------------------------------------------------------------------
    # For each face, average vertex values:
    #---------------------------------------------------------------------
    output_table = os.path.join(os.getcwd(), 'average_face_values.csv')
    columns = []
    for face in faces:
        values = []
        for index in face:
            if area_file:
                values.append(scalars[index] / area_scalars[index])
            else:
                values.append(scalars[index])
        columns.append(np.mean(values))

    #-----------------------------------------------------------------
    # Write to table:
    #-----------------------------------------------------------------
    write_columns(columns, '', output_table, delimiter, quote=False)

    return output_table


def write_average_face_values_per_label(input_indices_vtk,
                    input_values_vtk='', area_file='',
                    output_stem='', exclude_values=[-1], background_value=-1):
    """
    Write out a separate VTK file for each integer (>-1)
    in (the first) scalar list of an input VTK file.
    Optionally write the values drawn from a second VTK file.

    Parameters
    ----------
    input_indices_vtk : string
        path of the input VTK file that contains indices as scalars
    input_values_vtk : string
        path of the input VTK file that contains values as scalars
    output_stem : string
        path and stem of the output VTK file
    exclude_values : list or array
        values to exclude
    background_value : integer or float
        background value in output VTK files
    scalar_name : string
        name of a lookup table of scalars values

    Examples
    --------
    >>> import os
    >>> from mindboggle.utils.io_table import write_average_face_values_per_label
    >>> path = os.environ['MINDBOGGLE_DATA']
    >>> input_indices_vtk = os.path.join(path, 'allen', 'labels', 'lh.DKTatlas100.gcs.vtk')
    >>> input_values_vtk = os.path.join(path, 'allen', 'shapes', 'lh.thickness.vtk')
    >>> area_file = os.path.join(path, 'allen', 'shapes', 'lh.pial.area.vtk')
    >>> output_stem = 'labels_thickness'
    >>> exclude_values = [-1]
    >>> background_value = -1
    >>> #
    >>> write_average_face_values_per_label(input_indices_vtk,
    >>>     input_values_vtk, area_file, output_stem, exclude_values, background_value)
    >>> #
    >>> # View:
    >>> #example_vtk = os.path.join(os.getcwd(), output_stem + '0.vtk')
    >>> #from mindboggle.utils.plots import plot_vtk
    >>> #plot_vtk(example_vtk)

    """
    import os
    import numpy as np
    from mindboggle.utils.io_vtk import read_scalars, read_vtk, write_vtk
    from mindboggle.utils.io_table import write_columns
    from mindboggle.utils.mesh import remove_faces

    # Load VTK file:
    faces, lines, indices, points, npoints, scalars, scalar_names, \
        foo1 = read_vtk(input_indices_vtk, True, True)
    if area_file:
        area_scalars, name = read_scalars(area_file, True, True)
    print("Explode the scalar list in {0}".
          format(os.path.basename(input_indices_vtk)))
    if input_values_vtk != input_indices_vtk:
        values, name = read_scalars(input_values_vtk, True, True)
        print("Explode the scalar list of values in {0} "
              "with the scalar list of indices in {1}".
              format(os.path.basename(input_values_vtk),
                     os.path.basename(input_indices_vtk)))
    else:
        values = np.copy(scalars)

    # Loop through unique (non-excluded) scalar values:
    unique_scalars = [int(x) for x in np.unique(scalars)
                      if x not in exclude_values]
    for scalar in unique_scalars:

        keep_indices = [x for sublst in faces for x in sublst]
        new_faces = remove_faces(faces, keep_indices)

        # Create array and indices for scalar value:
        select_scalars = np.copy(scalars)
        select_scalars[scalars != scalar] = background_value
        scalar_indices = [i for i,x in enumerate(select_scalars) if x == scalar]
        print("  Scalar {0}: {1} vertices".format(scalar, len(scalar_indices)))

        #---------------------------------------------------------------------
        # For each face, average vertex values:
        #---------------------------------------------------------------------
        output_table = os.path.join(os.getcwd(),
                                    output_stem+str(scalar)+'.csv')
        columns = []
        for face in new_faces:
            values = []
            for index in face:
                if area_file:
                    values.append(scalars[index] / area_scalars[index])
                else:
                    values.append(scalars[index])
            columns.append(np.mean(values))

        #-----------------------------------------------------------------
        # Write to table:
        #-----------------------------------------------------------------
        write_columns(columns, '', output_table, delimiter=',', quote=False)

        # Write VTK file with scalar value:
        #output_vtk = os.path.join(os.getcwd(), output_stem + str(scalar) + '.vtk')
        #write_vtk(output_vtk, points, indices, lines, new_faces,
        #          [select_values.tolist()], [output_scalar_name])


