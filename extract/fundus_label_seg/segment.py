# segmentation based on nearest labels for fundus vertexes


def load_fundus(VTKFile):
    '''Load fundus vertex from a VTK file
    
    Notes 
    ==========
    
    My current fundi vtk file has the following LUTs in order:
    curvature, travel depth, thickness, sulc, fundus length
    
    '''
    import pyvtk
    Data = pyvtk.VtkData(VTKFile)
    Vertexes = Data.structure.points
    Fundus = Data.structure.lines
    LUTs = [Data.point_data.data[i].scalars for i in xrange(5)]
    
#    Depth =     VTKReader.point_data.data[1].scalars
    
#    print len(Fundus), "Fundus lines loaded"

    Fundus_Vertexes = []
    for Pair in Fundus:
        Fundus_Vertexes += Pair
    
    Fundus_Vertexes = list(set(Fundus_Vertexes)) # 

#    print len(Fundus_Vertexes), "Fundux vertexes loaded" 
        
    return Fundus_Vertexes, len(Vertexes), LUTs

def load_labels(VTKFile):
    '''Load voted labels of a mesh 
    '''
    import pyvtk
    Labels = pyvtk.VtkData(VTKFile).point_data.data[0].scalars
    return Labels

def load_nbr(PickleFile):
    '''Load the Vertex Neighbor list of a mesh
    '''
    import cPickle
    Fp = open(PickleFile, 'r')
    NbrLst = cPickle.load(Fp)
    Fp.close()
    return NbrLst

def label_vertex(Vrtx, NbrLst, Labels):
    '''Give a vertex two labels from its nearest labeled neighbors, using BFS
    
    Parameters
    ===========
    
    Vrtx : integer
        The ID of a vertex
        
    NbrLst: List of lists of integers
        the i-th element is the neighbors of vertex i 
        
    Labels: list of integers
        Labels assigned for vertexes from 21 atlases, unlabeled vertexes have value -1, and 1-35 otherwise.
        
    Visited: list of integers
        IDs of vertexes whose labels have been checked
        
    Ring: integer
        the hop from Vrtx to the search fringe
        
    Nbrs: list of integers
        all neighbors on a ring to Vrtx
    
    Returns
    ========
    
    TwoLabels: list of two integers
        the two most comment labels from Vrtx's nearest at least 2 labeled neighbors
        
    TwoLabels: list of two floats
        the two Euclidean distances from Vrtx's nearest two labeled neighbors
        
    Notes
    ========
    
    The code used to assign label was different from what Arno expects. 
    Now it is updated to assign two nearest DIFFERENT labels to each fundus vertex. 
    - Forrest, 2012-02-21
    
    For labels on a ring, do we assign the closest or the most common label?
    - Forrest, 2012-02-21
    
    Always return the smaller label first. So (12,32) and (32,12) are the same, (12.32). 
     
    ''' 

    from collections import Counter
    
    TwoLabels, TwoDists = [], []
    Visited = []
    
    if Labels[Vrtx] > 0:
        TwoLabels.append(Labels[Vrtx])
        TwoDists.append(0)
        Visited = [Vrtx]
    
    Fringe  = [Vrtx]
    Ring = 1
    while len(TwoLabels) < 2:
        # step 1: check labels in fringe
        for V in Fringe:
            Visited.append(V)
            if Labels[V] > 0 and not Labels[V] in TwoLabels: 
            # added the AND condition to ensure two different labels, F 2012-02-21
                    TwoLabels.append(Labels[V])
                    TwoDists.append(Ring)
                
        # step 2: search fringe propagation
        Nbrs = []
        for V in Fringe:
            for Nbr in NbrLst[V]:
                if not Nbr in Visited and not Nbr in Nbrs:
                    Nbrs.append(Nbr)
                    
        Fringe = Nbrs
        Ring += 1

        if Ring > 500: # something may go wrong
            print "Taking too long to find nearest two labeled neighbors"
            print "Vrtx is:", Vrtx
            return [-1, -1], [-1, -1]

    if TwoLabels[0] > TwoLabels[1]:
        return TwoLabels[::-1], TwoDists[::-1] # Always smaller label first 
    else:
        return TwoLabels, TwoDists
    
#    Top2Labels = Counter(TwoLabels).most_common(2)  
   
#    if len(Top2Labels) < 2:
#        return TwoLabels[:2], TwoDists[:2]
#    else: 
#        return [Top2Labels[0][0], Top2Labels[1][0]], [TwoDists[TwoLabels.index(Top2Labels[0][0])], TwoDists[TwoLabels.index(Top2Labels[1][0])]] 
    
#    return TwoLabels[:2], TwoDists[:2] # let's say randomly pick the first two for fast prototyping 

def label_fundi(Fundus_Vertexes, NbrLst, Labels):
    '''Label many fundus vertexes
    
    
    Returns 
    ========
    
    Fundus_Labels: a dictionary
        key is the ID of a vertex on a fundus; value are 2-tuples,
        which are the two nearest labels for the vertex,
        
    Fundus_Dists: a dictionary 
        key is the ID of a vertex on fundu; value are 2-tuples,
        which are distances from the vertex to two nearest labeled vertexes
        
    
    '''
#    Count = 0
    Fundus_Labels, Fundus_Dists = {}, {}  
    for ID, Vrtx in enumerate(Fundus_Vertexes):
        TwoLbs, TwoDists = label_vertex(Vrtx, NbrLst, Labels)
        Fundus_Labels[Vrtx] = TwoLbs
        Fundus_Dists[Vrtx]   = TwoDists
        
#        print ID,"-th fundus vertex:", Vrtx
        
#        Count += 1 
#        if Count > 10:
#            break 
    
    return Fundus_Labels, Fundus_Dists

def write_seg(Fundus_Labels, Fundus_Dists, Num_Vrtx, FundiFile, FundiFile2):
    '''Write the segmentation result into VTK
    
    To make things easier, this function copies everything from FundiFile and FundiFiles2 
    as the beginning part of outputting files 
    
    Parameters
    ===========
    
    Num_Vrtx: integer
        Number of vertexes on original mesh 
    
    Notes
    =======
    
    1. Please note the way we represent two labels, it's 4 digits. 
    
    2. Distances are not dumped yet. 
    
    '''

    Segment = [-1 for i in xrange(Num_Vrtx)] # -1 means this not a fundus vertex
    
#    Pair_Index, Num_Diff_Labels = {}, 0
#    for Label_Pair in Fundus_Labels.values():
#        if not Label_Pair in Pair_Index.keys():
#            Pair_Index[(Label_Pair[0],Label_Pair[1])] = Num_Diff_Labels
#            Num_Diff_Labels += 1
    All_Pairs = []
    for LabelPair in Fundus_Labels.values():
        if not LabelPair[0]*100 + LabelPair[1] in All_Pairs:
            All_Pairs.append(LabelPair[0]*100 + LabelPair[1]) 
              
    for Vrtx, LabelPair in Fundus_Labels.iteritems():
        Segment[Vrtx] = LabelPair[0]*100 + LabelPair[1]# for absolute labels, use this line
#        Segment[Vrtx] = All_Pairs.index(LabelPair[0]*100 + LabelPair[1]) # for better visualization, use this line
                
    Distance = [-1 for i in xrange(Num_Vrtx)] # -1 means this not a fundus vertex
    for Vrtx, DistPair in Fundus_Dists.iteritems():
#        Distance[Vrtx] = DistPair[0] + DistPair[1]
        Distance[Vrtx] = DistPair[0]*100 + DistPair[1]
    
    SegFile = FundiFile[:-4] + '.seg.vtk'  # drop .vtk suffix
    SegFP = open(SegFile, 'w')
    
    FundiFP = open(FundiFile,'r')  
    while True:
        Line = FundiFP.readline()
        if len(Line) < 1 : 
            break 
        else:
            SegFP.write(Line)
    FundiFP.close()        
    
    SegFP.write('\nSCALARS Segment int \n')
    SegFP.write('LOOKUP_TABLE default\n')
    
    for Seg in Segment: 
        SegFP.write(str(Seg)+'\n')

    SegFP.write('\nSCALARS To_Nearest int \n')
    SegFP.write('LOOKUP_TABLE default\n')
    
    for Dist in Distance: 
        SegFP.write(str(Dist)+'\n')
    
    SegFP.close()

    if FundiFile2 != '':
        SegFile = FundiFile2[:-8] + '.seg.2nd.vtk'  # drop .2nd.vtk suffix
        SegFP = open(SegFile, 'w')
        
        FundiFP = open(FundiFile2,'r')  
        while True:
            Line = FundiFP.readline()
            if len(Line) < 1 : 
                break 
            else:
                SegFP.write(Line)
        FundiFP.close()        
        
        SegFP.write('\nSCALARS Segment int \n')
        SegFP.write('LOOKUP_TABLE default\n')
        
        for Seg in Segment: 
            SegFP.write(str(Seg)+'\n')

        SegFP.write('\nSCALARS To_Nearest int \n')
        SegFP.write('LOOKUP_TABLE default\n')
        
        for Dist in Distance: 
            SegFP.write(str(Dist)+'\n')
            
        SegFP.close()

    return 0
    
def seg_main(FundiFile, NbrLstFile, LabelFile):
    
    Fundus_Vertexes, Num_Vrtx, LUTs = load_fundus(FundiFile)
    NbrLst = load_nbr(NbrLstFile)
    Labels = load_labels(LabelFile)
    
    Fundus_Labels, Fundus_Dists = label_fundi(Fundus_Vertexes, NbrLst, Labels)
    write_seg(Fundus_Labels, Fundus_Dists, Num_Vrtx, FundiFile, FundiFile[:-4]+'.2nd.vtk')


seg_main('/forrest/data/MRI/MDD/50014/surf/lh.travel.depth.depth.fundi.vtk',\
                             '/forrest/data/MRI/MDD/50014/surf/lh.vrtx.nbr',\
                             '/forrest/data/MRI/MDD/50014/surf/lh.assign.pial.vtk')

 