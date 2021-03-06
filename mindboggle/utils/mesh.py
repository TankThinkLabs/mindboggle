#!/usr/bin/env python
"""
Operations on surface mesh vertices.

Authors:
    - Forrest Bao, 2012  (forrest.bao@gmail.com)
    - Arno Klein, 2012-2013  (arno@mindboggle.info)  http://binarybottle.com

Copyright 2013,  Mindboggle team (http://mindboggle.info), Apache v2.0 License

"""

#-----------------------------------------------------------------------------
# Find all neighbors from faces in a VTK mesh file
#-----------------------------------------------------------------------------
def find_neighbors_from_file(input_vtk):
    """
    Generate the list of unique, sorted indices of neighboring vertices
    for all vertices in the faces of a triangular mesh in a VTK file.

    Parameters
    ----------
    input_vtk : string
        name of input VTK file containing surface mesh

    Returns
    -------
    neighbor_lists : list of lists of integers
        each list contains indices to neighboring vertices for each vertex

    Examples
    --------
    >>> import os
    >>> import numpy as np
    >>> from mindboggle.utils.mesh import find_neighbors_from_file
    >>> from mindboggle.utils.io_vtk import rewrite_scalars
    >>> from mindboggle.utils.plots import plot_vtk
    >>> path = os.environ['MINDBOGGLE_DATA']
    >>> vtk_file = os.path.join(path, 'arno', 'freesurfer', 'lh.pial.vtk')
    >>> #
    >>> neighbor_lists = find_neighbors_from_file(vtk_file)
    >>> #
    >>> # Write results to vtk file and view:
    >>> index = 0
    >>> IDs = -1 * np.ones(npoints)
    >>> IDs[index] = 1
    >>> IDs[neighbor_lists[index]] = 2
    >>> rewrite_scalars(vtk_file, 'find_neighbors_from_file.vtk', IDs, 'neighbors', IDs)
    >>> plot_vtk('find_neighbors_from_file.vtk')

    """
    from mindboggle.utils.io_vtk import read_faces_points
    from mindboggle.utils.mesh import find_neighbors

    faces, points, npoints = read_faces_points(input_vtk)

    neighbor_lists = find_neighbors(faces, npoints)

    return neighbor_lists

#-----------------------------------------------------------------------------
# Find all neighbors from faces
#-----------------------------------------------------------------------------
def find_neighbors(faces, npoints):
    """
    Generate the list of unique, sorted indices of neighboring vertices
    for all vertices in the faces of a triangular mesh.

    Parameters
    ----------
    faces : list of lists of three integers
        the integers for each face are indices to vertices, starting from zero
    npoints: integer
        number of vertices on the mesh

    Returns
    -------
    neighbor_lists : list of lists of integers
        each list contains indices to neighboring vertices for each vertex

    Examples
    --------
    >>> # Simple example:
    >>> from mindboggle.utils.mesh import find_neighbors
    >>> faces = [[0,1,2],[0,2,3],[0,3,4],[0,1,4],[4,3,1]]
    >>> npoints = 5
    >>> find_neighbors(faces, npoints)
        [[1, 2, 3, 4], [0, 2, 4, 3], [0, 1, 3], [0, 2, 4, 1], [0, 3, 1]]

    >>> # Real example:
    >>> import os
    >>> import numpy as np
    >>> from mindboggle.utils.mesh import find_neighbors
    >>> from mindboggle.utils.io_vtk import read_faces_points, rewrite_scalars
    >>> path = os.environ['MINDBOGGLE_DATA']
    >>> vtk_file = os.path.join(path, 'arno', 'freesurfer', 'lh.pial.vtk')
    >>> faces, points, npoints = read_faces_points(vtk_file)
    >>> #
    >>> neighbor_lists = find_neighbors(faces, npoints)
    >>> #
    >>> # Write results to vtk file and view:
    >>> index = 0
    >>> IDs = -1 * np.ones(npoints)
    >>> IDs[index] = 1
    >>> IDs[neighbor_lists[index]] = 2
    >>> rewrite_scalars(vtk_file, 'find_neighbors.vtk', IDs, 'neighbors', IDs)
    >>> from mindboggle.utils.plots import plot_vtk
    >>> plot_vtk('find_neighbors.vtk')

    """

    neighbor_lists = [[] for x in range(npoints)]

    for face in faces:
        [v0, v1, v2] = face
        if v1 not in neighbor_lists[v0]:
            neighbor_lists[v0].append(v1)
        if v2 not in neighbor_lists[v0]:
            neighbor_lists[v0].append(v2)

        if v0 not in neighbor_lists[v1]:
            neighbor_lists[v1].append(v0)
        if v2 not in neighbor_lists[v1]:
            neighbor_lists[v1].append(v2)

        if v0 not in neighbor_lists[v2]:
            neighbor_lists[v2].append(v0)
        if v1 not in neighbor_lists[v2]:
            neighbor_lists[v2].append(v1)

    return neighbor_lists

#-----------------------------------------------------------------------------
# Find neighbors for a given vertex
#-----------------------------------------------------------------------------
def find_neighbors_vertex(faces, index):
    """
    Find neighbors to a surface mesh vertex.

    For a set of surface mesh faces and the index of a surface vertex,
    find unique indices for neighboring vertices.

    Parameters
    ----------
    faces : list of lists of three integers
        the integers for each face are indices to vertices, starting from zero
    index : int
        index of surface vertex

    Returns
    -------
    neighbor_lists : list of lists of integers
        each list contains indices to neighboring vertices for each vertex

    Examples
    --------
    >>> from mindboggle.utils.mesh import find_neighbors_vertex
    >>> faces = [[0,1,2],[0,2,3],[0,3,4],[0,1,4]]
    >>> index = 1
    >>> find_neighbors_vertex(faces, index)
        [0, 2, 4]

    """
    import numpy as np

    # Make sure argument is a numpy array
    if not isinstance(faces, np.ndarray):
        faces = np.array(faces)

    # Create list of vertex indices sharing the same faces as "index"
    I = [faces[np.where(faces[:,i] == index)[0], :] for i in (0,1,2)]

    # Create single list from nested lists
    I = [int(x) for lst in I for sublst in lst for x in sublst]

    # Find unique indices not equal to "index"
    neighbor_list = []; [neighbor_list.append(x)
                         for x in I if x not in neighbor_list if x != index]

    return neighbor_list

#-----------------------------------------------------------------------------
# Find neighborhood for given vertices
#-----------------------------------------------------------------------------
def find_neighborhood(neighbor_lists, indices, nedges=1):
    """
    Find neighbors in the neighborhood of given surface mesh vertices.

    For indices to surface mesh vertices, find unique indices for
    vertices in the neighborhood of the vertices.

    Parameters
    ----------
    neighbor_lists : list of lists of integers
        each list contains indices to neighboring vertices for each vertex
    indices : list of integers
        indices of surface vertices
    nedges : integer
        number of edges to propagate from indices

    Returns
    -------
    neighborhood : list of integers
        indices to vertices in neighborhood

    Examples
    --------
    >>> from mindboggle.utils.mesh import find_neighborhood
    >>> neighbor_lists = [[0,1],[0,2],[1,4,5],[2],[],[0,1,4,5]]
    >>> indices = [1,3,4]
    >>> find_neighborhood(neighbor_lists, indices, 2)
        [0, 2, 5]

    """

    # Initialize seed list with indices
    neighborhood = []
    seed_list = indices[:]
    completed = seed_list[:]

    # Propagate nedges away from indices:
    for iedge in range(nedges):

        # Find neighbors of seeds:
        if seed_list:
            local_neighbors = []
            [local_neighbors.extend(neighbor_lists[x]) for x in seed_list]

            # Select neighbors that have not been previously selected:
            seed_list = list(set(local_neighbors).difference(completed))

            # Add to neighborhood:
            neighborhood.extend(seed_list)
            completed.extend(seed_list)

            neighborhood = [int(x) for x in neighborhood]

    return neighborhood

#-----------------------------------------------------------------------------
# find all edges on the mesh
#-----------------------------------------------------------------------------
def find_edges(faces):
    """
    Find all edges on a mesh

   Parameters
    ----------
    faces : list of lists of three integers
        the integers for each face are indices to vertices, starting from zero

    Returns
    --------
    edges : list of lists of integers
        each element is a 2-tuple of vertex ids representing an edge

    Examples
    --------
    >>> # Simple example:
    >>> from mindboggle.utils.mesh import find_edges
    >>> faces=[[0,1,2], [0,1,4], [1,2,3], [0,2,5]]
    >>> find_edges(faces)
    [[0, 1], [1, 2], [0, 2], [1, 4], [0, 4], [2, 3], [1, 3], [2, 5], [0, 5]]

    """
    edges = [ ]
    for face in faces:
        for edge in [face[0:2], face[1:3], [face[0], face[2]] ]:
            if not edge in edges: # I know that this is costly
                edges.append(edge)

    return edges

#-----------------------------------------------------------------------------
# find all triangle faces sharing each edge
#-----------------------------------------------------------------------------
def find_faces_at_edges(faces):
    """
    For each edge on the mesh, find the two faces that share the edge.

   Parameters
    ----------
    faces : list of lists of three integers
        the integers for each face are indices to vertices, starting from zero

    Returns
    --------
    faces_at_edges : dictionary
        keys are tuples of two vertex IDs and values are 2-tuples of face IDs

    Examples
    --------
    >>> # Simple example:
    >>> from mindboggle.utils.mesh import find_faces_at_edges
    >>> faces=[[0,1,2], [0,1,4], [1,2,3], [0,2,5]]
    >>> find_faces_at_edges(faces)
        {(0, 1): [0, 1],
         (0, 2): [0, 3],
         (0, 4): [1],
         (0, 5): [3],
         (1, 0): [0, 1],
         (1, 2): [0, 2],
         (1, 3): [2],
         (1, 4): [1],
         (2, 0): [0, 3],
         (2, 1): [0, 2],
         (2, 3): [2],
         (2, 5): [3],
         (3, 1): [2],
         (3, 2): [2],
         (4, 0): [1],
         (4, 1): [1],
         (5, 0): [3],
         (5, 2): [3]}

    Notes ::
        The faces are assumed to be triangular.

    """

    faces_at_edges = {}
    for face_id, face in enumerate(faces):
        for edge in [face[0:2], face[1:3], [face[0], face[2]] ]:
            faces_at_edges.setdefault((edge[0], edge[1]), []).append(face_id)
            faces_at_edges.setdefault((edge[1], edge[0]), []).append(face_id) # make it symmetric

    return faces_at_edges

#-----------------------------------------------------------------------------
# find all triangle faces centered at each node on the mesh
#-----------------------------------------------------------------------------
def find_faces_at_vertices(faces, npoints):
    """
    For each vertex, find all faces containing this vertex.
    Note: faces do not have to be triangles.

    Parameters
    ----------
    faces : list of lists of three integers
        the integers for each face are indices to vertices, starting from zero

    npoints: integer
        number of vertices on the mesh

    Returns
    --------
    faces_at_vertex : list of lists of integers
        faces_at_vertices[i] is a list of faces that contain the i-th vertex

    Examples
    --------
    >>> # Simple example:
    >>> from mindboggle.utils.mesh import find_faces_at_vertices
    >>> faces = [[0,1,2],[0,2,3],[0,3,4],[0,1,4],[4,3,1]]
    >>> npoints = 5
    >>> find_faces_at_vertices(faces, npoints)
        [[0, 1, 2, 3], [0, 3, 4], [0, 1], [1, 2, 4], [2, 3, 4]]

    """
    faces_at_vertices = [[] for i in range(npoints)]
    for face_id, face in enumerate(faces):
        for vertex in face:
           faces_at_vertices[vertex].append(face_id)

    return faces_at_vertices


def find_adjacent_faces(faces):
    """
    For each face in a list of faces, find adjacent faces.

    Parameters
    ----------
    faces : list of lists of three integers
        the integers for each face are indices to vertices, starting from zero
        (-1 indicates no result for a given face or vertex)

    Returns
    -------
    adjacent_faces: list of pairs of lists of three integers
        list 1 indexes three faces adjacent to the three face's edges; 
        list 2 indexes three vertices opposite the adjacent faces:
        adjacent_faces[i]: two lists, each of length 3
        adjacent_faces[i][0] = [face0, face1, face2]: 
                                face0 is the neighbor of face i facing vertex0
        adjacent_faces[i][1] = [vertex0, vertex1, vertex2], which is face i:
                                vertex0 is the vertex of face0 not in face i

    Examples
    --------
    >>> # Simple example:
    >>> from mindboggle.utils.mesh import find_adjacent_faces
    >>> faces = [[0,1,2],[0,2,3],[0,3,4],[0,1,4],[4,3,1]]
    >>> find_adjacent_faces(faces)
        [[[-1, 1, 3], [-1, 3, 4]],
         [[-1, 2, 0], [-1, 4, 1]],
         [[4, 3, 1], [1, 1, 2]],
         [[4, 2, 0], [3, 3, 2]],
         [[-1, 3, 2], [-1, 0, 0]]]

    """

    print "Calculating face neighbor list"

    n_faces = len(faces)

    adjacent_faces = []
    [adjacent_faces.append([[-1,-1,-1], [-1,-1,-1]]) for i in range(n_faces)]

    Done =[]
    [Done.append(0) for i in range(n_faces)]

    # Loop through faces:
    for i1, face1 in enumerate(faces):
        # Loop through remaining faces:
        for i2 in range(i1+1, n_faces):
            face2 = faces[i2]

            # Loop through first two vertices of face:
            for ivertex in [0,1]:
                index1 = face1[ivertex]
                # Loop through remaining vertices of face:
                for index2 in face1[ivertex+1:3]:

                    # If pair of vertices in face2:
                    if index1 in face2 and index2 in face2:

                        # Determine if it is face0, face1 or face2:
                        NbrID1 = 3 - face1.index(index1) - face1.index(index2)
                        NbrID2 = 3 - face2.index(index1) - face2.index(index2)

                        adjacent_faces[i1][0][NbrID1] = i2
                        adjacent_faces[i2][0][NbrID2] = i1
                        adjacent_faces[i1][1][NbrID1] = face2[NbrID2]
                        adjacent_faces[i2][1][NbrID2] = face1[NbrID1]

                        Done[i1] += 1
                        Done[i2] += 1

            # Break if all three neighbors of face1 have been found:
            if Done[i] == 3:
                break

    return adjacent_faces

#-----------------------------------------------------------------------------
# Filter faces
#-----------------------------------------------------------------------------
def remove_faces(faces, indices):
    """
    Remove surface mesh faces whose three vertices are not all in "indices".

    Parameters
    ----------
    faces : list of lists of three integers
        the integers for each face are indices to vertices, starting from zero
    indices : integers
        indices to vertices of the surface mesh

    Returns
    -------
    faces : list of lists of three integers
        reduced number of faces

    Examples
    --------
    >>> from mindboggle.utils.mesh import remove_faces
    >>> faces = [[1,2,3], [2,3,7], [4,7,8], [3,2,5]]
    >>> indices = [0,1,2,3,4,5]
    >>> remove_faces(faces, indices)
      Reduced 4 to 2 triangular faces.
      [[1, 2, 3], [3, 2, 5]]

    """
    import numpy as np

    len_faces = len(faces)
    fs = frozenset(indices)
    faces = [lst for lst in faces if len(fs.intersection(lst)) == 3]
    faces = np.reshape(np.ravel(faces), (-1, 3))
    if len(faces) < len_faces:
        print('Reduced {0} to {1} triangular faces'.format(len_faces, len(faces)))

    return faces.tolist()

def reindex_faces_points(faces, points=[]):
    """
    Renumber indices in faces and remove points (coordinates) not in faces.

    Parameters
    ----------
    faces : list of lists of integers
        each sublist contains 3 indices of vertices that form a face
        on a surface mesh
    points : list of lists of floats (optional)
        each sublist contains 3-D coordinates of a vertex on a surface mesh

    Returns
    -------
    new_faces : list of lists of integers
        each sublist contains 3 (renumbered) indices of vertices
        that form a face on a surface mesh
    new_points : list of lists of floats
        each (new) sublist contains 3-D coordinates of a vertex on a surface mesh

    Examples
    --------
    >>> import os
    >>> from mindboggle.utils.io_vtk import read_faces_points
    >>> from mindboggle.utils.mesh import reindex_faces_points
    >>> # Reindex faces:
    >>> faces = [[8,2,3], [2,3,7], [4,7,8], [3,2,5]]
    >>> reindex_faces_points(faces, points=[])
        ([[5, 0, 1], [0, 1, 4], [2, 4, 5], [1, 0, 3]], None)
    >>> # Reindex faces of a single fold of the brain:
    >>> path = os.environ['MINDBOGGLE_DATA']
    >>> fold_file = os.path.join(path, 'arno', 'features', 'fold11.vtk')
    >>> faces, points, npoints = read_faces_points(fold_file)
    >>> new_faces, new_points = reindex_faces_points(faces, points)

    """
    import itertools

    # set() to remove repeated indices and list() to order them for later use:
    indices_to_keep = list(set(itertools.chain(*faces)))
    reindex = dict([(old_index, new_index)
                    for new_index, old_index in enumerate(indices_to_keep)])

    new_faces = [[reindex[old_index] for old_index in face] for face in faces]

    if points:
        new_points = [points[new_index] for new_index in indices_to_keep]
    else:
        new_points = None

    return new_faces, new_points

#-----------------------------------------------------------------------------
# Filter neighbor_lists
#-----------------------------------------------------------------------------
def remove_neighbor_lists(neighbor_lists, indices):
    """
    Remove all but a given set of indices from surface mesh neighbor lists.

    Note :: SLOW!

    Parameters
    ----------
    neighbor_lists : list of lists of integers
        each list contains indices to neighboring vertices for each vertex
    indices : integers
        indices to vertices of the surface mesh

    Returns
    -------
    neighbor_lists : list of lists of integers
        each list has indices to remaining neighboring vertices for each vertex

    Examples
    --------
    >>> from mindboggle.utils.mesh import remove_neighbor_lists
    >>> neighbor_lists = [[1,2,3], [2,3,7], [12,43], [4,7,8], [3,2,5]]
    >>> indices = [0,1,2,3,4,5]
    >>> remove_neighbor_lists(neighbor_lists, indices)
        [[1, 2, 3], [2, 3], [], [4], [2, 3, 5]]

    """

    neighbor_lists = [list(frozenset(indices).intersection(x))
                      for x in neighbor_lists]

    return neighbor_lists

#-----------------------------------------------------------------------------
# Decimate mesh
#-----------------------------------------------------------------------------
def decimate(points, faces, reduction=0.5, smooth_steps=100, output_vtk=''):
    """
    Decimate vtk triangular mesh with vtk.vtkDecimatePro.

    Parameters
    ----------
    points : list of lists of floats
        each element is a list of 3-D coordinates of a vertex on a surface mesh
    faces : list of lists of integers
        each element is list of 3 indices of vertices that form a face
        on a surface mesh
    reduction : float
        fraction of mesh faces to remove
    smooth_steps : integer
        number of smoothing steps
    output_vtk : string
        output decimated vtk file

    Returns
    -------
    points : list of lists of floats
        decimated points
    faces : list of lists of integers
        decimated faces
    output_vtk : string
        output decimated vtk file

    Examples
    --------
    >>> import os
    >>> from mindboggle.utils.io_vtk import read_vtk, write_vtk
    >>> from mindboggle.utils.mesh import decimate
    >>> path = os.environ['MINDBOGGLE_DATA']
    >>> input_vtk = os.path.join(path, 'arno', 'labels', 'label22.vtk')
    >>> reduction = 0.5
    >>> smooth_steps = 100
    >>> output_vtk = ''
    >>> faces, lines, indices, points, npoints, scalars, scalar_names,
    ...     o2  = read_vtk(input_vtk)
    >>> points, faces, output_vtk = decimate(points, faces, reduction,
    >>>                                      smooth_steps, output_vtk)
    >>> len(points) == 4567
    True
    >>> len(points)
    4567
    >>> # View:
    >>> write_vtk('decimated.vtk', points, indices, lines, faces, scalars,
    >>>           scalar_names) # doctest: +SKIP
    >>> os.system('mayavi2 -d decimated.vtk -m Surface &') # doctest: +SKIP

    """
    import os
    import vtk

    from mindboggle.utils.io_vtk import read_vtk

    # vtk points:
    vtk_points = vtk.vtkPoints()
    [vtk_points.InsertPoint(i, x[0], x[1], x[2]) for i,x in enumerate(points)]

    # vtk faces:
    vtk_faces = vtk.vtkCellArray()
    for face in faces:
        vtk_face = vtk.vtkPolygon()
        vtk_face.GetPointIds().SetNumberOfIds(3)
        vtk_face.GetPointIds().SetId(0, face[0])
        vtk_face.GetPointIds().SetId(1, face[1])
        vtk_face.GetPointIds().SetId(2, face[2])
        vtk_faces.InsertNextCell(vtk_face)

    # vtkPolyData:
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(vtk_points)
    polydata.SetPolys(vtk_faces)

    # We want to preserve topology (not let any cracks form).
    # This may limit the total reduction possible.
    decimate = vtk.vtkDecimatePro()
    decimate.SetInput(polydata)
    decimate.SetTargetReduction(reduction)
    decimate.PreserveTopologyOn()

    # Export output:
    if not output_vtk:
        output_vtk = os.path.join(os.getcwd(), 'decimated_file.vtk')
    #exporter = vtk.vtkPolyDataWriter()
    if smooth_steps > 0:
        smoother = vtk.vtkSmoothPolyDataFilter()
        smoother.SetInput(decimate.GetOutput())
        smoother.SetNumberOfIterations(smooth_steps)
        smoother.Update()
        out = smoother.GetOutput()
        #exporter.SetInput(smoother.GetOutput())
    else:
        decimate.Update()
        out = decimate.GetOutput()
        #exporter.SetInput(decimate.GetOutput())
    #exporter.SetFileName(output_vtk)
    #exporter.Write()
    ## Extract points and faces:
    #faces, u1, u2, points, u4, u5, u6, u7 = read_vtk(output_vtk)

    points = [list(out.GetPoint(point_id))
              for point_id in range(out.GetNumberOfPoints())]

    if out.GetNumberOfPolys() > 0:
        polys = out.GetPolys()
        faces = [[int(polys.GetData().GetValue(j))
                  for j in range(i*4 + 1, i*4 + 4)]
                  for i in range(polys.GetNumberOfCells())]
    else:
        faces = []

    return points, faces, output_vtk


def decimate_file(input_vtk, reduction=0.5, smooth_steps=100, output_vtk=''):
    """
    Decimate vtk triangular mesh file with vtk.vtkDecimatePro.

    Parameters
    ----------
    input_vtk : string
        input vtk file with triangular surface mesh
    reduction : float
        fraction of mesh faces to remove
    do_smooth : Boolean
        smooth after decimation?
    output_vtk : string
        output decimated vtk file

    Returns
    -------
    output_vtk : string
        output decimated vtk file

    Examples
    --------
    >>> import os
    >>> from mindboggle.utils.mesh import decimate_file
    >>> path = os.environ['MINDBOGGLE_DATA']
    >>> input_vtk = os.path.join(path, 'arno', 'labels', 'label22.vtk')
    >>> output_vtk = 'decimated_file.vtk'
    >>> reduction = 0.9
    >>> smooth_steps = 0
    >>> decimate_file(input_vtk, reduction=reduction,
    >>>               smooth_steps=smooth_steps, output_vtk=output_vtk)
    >>> # View:
    >>> os.system('mayavi2 -d ' + output_vtk + ' -m Surface &')

    """
    import os
    import vtk

    from mindboggle.utils.io_vtk import read_vtk

    # Read VTK surface mesh file:
    faces, u1, u2, points, u4, labels, u5, u6 = read_vtk(input_vtk)

    # vtk points:
    vtk_points = vtk.vtkPoints()
    [vtk_points.InsertPoint(i, x[0], x[1], x[2]) for i,x in enumerate(points)]

    # vtk faces:
    vtk_faces = vtk.vtkCellArray()
    for face in faces:
        vtk_face = vtk.vtkPolygon()
        vtk_face.GetPointIds().SetNumberOfIds(3)
        vtk_face.GetPointIds().SetId(0, face[0])
        vtk_face.GetPointIds().SetId(1, face[1])
        vtk_face.GetPointIds().SetId(2, face[2])
        vtk_faces.InsertNextCell(vtk_face)

    # vtkPolyData:
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(vtk_points)
    polydata.SetPolys(vtk_faces)

    # We want to preserve topology (not let any cracks form).
    # This may limit the total reduction possible.
    decimate = vtk.vtkDecimatePro()
    decimate.SetInput(polydata)
    decimate.SetTargetReduction(reduction)
    decimate.PreserveTopologyOn()

    # Export output:
    if not output_vtk:
        output_vtk = os.path.join(os.getcwd(), 'decimated_file.vtk')
    exporter = vtk.vtkPolyDataWriter()
    if smooth_steps > 0:
        smoother = vtk.vtkSmoothPolyDataFilter()
        smoother.SetInputConnection(decimate.GetOutputPort())
        smoother.SetNumberOfIterations(smooth_steps)
        exporter.SetInput(smoother.GetOutput())
    else:
        exporter.SetInput(decimate.GetOutput())
    exporter.SetFileName(output_vtk)
    exporter.Write()

    return output_vtk


if __name__ == "__main__":

    import os
    from mindboggle.utils.io_vtk import read_vtk, write_vtk
    from mindboggle.utils.mesh import decimate
    path = os.environ['MINDBOGGLE_DATA']
    input_vtk = os.path.join(path, 'arno', 'labels', 'label22.vtk')
    reduction = 0.5
    smooth_steps = 100
    faces, lines, indices, points, npoints, labels, o1, o2  = read_vtk(input_vtk)

    import vtk

    # vtk points:
    vtk_points = vtk.vtkPoints()
    [vtk_points.InsertPoint(i, x[0], x[1], x[2]) for i,x in enumerate(points)]

    # vtk faces:
    vtk_faces = vtk.vtkCellArray()
    for face in faces:
        vtk_face = vtk.vtkPolygon()
        vtk_face.GetPointIds().SetNumberOfIds(3)
        vtk_face.GetPointIds().SetId(0, face[0])
        vtk_face.GetPointIds().SetId(1, face[1])
        vtk_face.GetPointIds().SetId(2, face[2])
        vtk_faces.InsertNextCell(vtk_face)

    # vtkPolyData:
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(vtk_points)
    polydata.SetPolys(vtk_faces)

    # We want to preserve topology (not let any cracks form).
    # This may limit the total reduction possible.
    decimate = vtk.vtkDecimatePro()
    decimate.SetInput(polydata)
    decimate.SetTargetReduction(reduction)
    decimate.PreserveTopologyOn()

    if smooth_steps > 0:
        smoother = vtk.vtkSmoothPolyDataFilter()
        smoother.SetInputConnection(decimate.GetOutputPort())
        smoother.SetNumberOfIterations(smooth_steps)
        output = smoother.GetOutput()
    else:
        output = decimate.GetOutput()

