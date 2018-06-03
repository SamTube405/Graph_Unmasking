import snap
import sys
import numpy as np
import os
import errno

## Graph Sampling to generate Edge-correlated subgraphs
## Author: Sameera Horawalavithana
class Sampling:

    def __init__(self, fileName, stage, overlap, overlap_choice):
        self.fileName = fileName
        print self.fileName
        self.rootDir=os.path.abspath(self.getPairsDir(fileName))
        #self.G = self.getGraph(snap.PUNGraph)
        self.G = self.getGraph()

        self.graphName = self.getGraphName()
        self.graph_size = self.G.GetNodes()
        print self.graph_size
        self.stage=stage

        self.overlap = overlap
        self.overlap_size = int(round(self.overlap * self.graph_size))
        self.overlap_choice=overlap_choice



        self.targetDir = self.stage+"/"+str(overlap)+"/"+str(overlap_choice)

        #self.chkDir(self.rootDir+"/"+self.targetDir)
        #print self.targetDir
        print "Network %s: (%d,%d)" % (self.graphName, self.graph_size,self.G.GetEdges())
        #snap.PrintInfo(self.G, self.graphName, self.rootDir + self.graphName + "-info.txt", False)

    def getGraph(self):
        return snap.LoadEdgeList(snap.PUNGraph, self.fileName)

    def getPairsDir(self,fileName):
        path=""
        tags = fileName.split("/")
        for i in range(0,len(tags)-1):
            path+=tags[i]+"/"
        return path

    def getLblGraph(self):
        context = snap.TTableContext()

        schema = snap.Schema()
        schema.Add(snap.TStrTAttrPr("srcLabel", snap.atStr))
        schema.Add(snap.TStrTAttrPr("srcId", snap.atInt))
        schema.Add(snap.TStrTAttrPr("dstLabel", snap.atStr))
        schema.Add(snap.TStrTAttrPr("dstId", snap.atInt))

        # schema.Add(snap.TStrTAttrPr("srcID", snap.atStr))
        # schema.Add(snap.TStrTAttrPr("dstID", snap.atStr))
        # schema.Add(snap.TStrTAttrPr("timestamp", snap.atInt))

        table = snap.TTable.LoadSS(schema, self.fileName, context, " ", snap.TBool(False))
        #print table

        edgeattrv = snap.TStrV()
        edgeattrv.Add("srcLabel")
        edgeattrv.Add("dstLabel")
        # edgeattrv.Add("edgeattr2")

        srcnodeattrv = snap.TStrV()
        # srcnodeattrv.Add("srcLabel")

        dstnodeattrv = snap.TStrV()
        # srcnodeattrv.Add("dstLabel")

        # net will be an object of type snap.PNEANet
        return snap.ToNetwork(snap.PNEANet, table, "srcId", "dstId", srcnodeattrv, dstnodeattrv, edgeattrv, snap.aaFirst)

    def getGraphName(self):
        tags = self.fileName.split("/")
        return tags[len(tags) - 1].split(".")[0]

    def getNodeDegVector(self):
        nodeIdV = snap.TIntV()
        nodeDegH = snap.TIntH()
        for node in self.G.Nodes():
            nodeIdV.Add(node.GetId())
            nodeDegH[node.GetId()]=node.GetOutDeg()

        nodeDegH.SortByDat(False) # sorted desc
        return nodeIdV,nodeDegH

    def saveGraph(self,G,fileName):
        snap.SaveEdgeList(G, fileName)

    def saveLblGraph(self,G,fileName):
        text=""

        for EI in G.Edges():
            srcId = EI.GetSrcNId()
            dstId = EI.GetDstNId()

            EI=self.G.GetEI(srcId, dstId)

            srcAttr="srcLabel"
            srcAttrVal=self.G.GetStrAttrDatE(EI, srcAttr)

            dstAttr="dstLabel"
            dstAttrVal = self.G.GetStrAttrDatE(EI, dstAttr)

            text += srcAttrVal + " " + str(srcId) + " " + dstAttrVal + " " + str(dstId) + "\n";



        self.writeFile(text,fileName)

    def chkDir(self,path):
        if not os.path.exists(os.path.dirname(path)):
            try:
                os.makedirs(os.path.dirname(path))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

    def writeFile(self,text,fileName):
        self.chkDir(fileName)
        f = open(fileName, "w")
        f.write(text)

    def getSubgraph(self,subgraphNodeIdHV):
        lblFiles=[]
        walker = subgraphNodeIdHV.BegI()

        while not walker.IsEnd():
            graphId=walker.GetKey()
            subgraphNodeIdV=walker.GetDat()
            subG = snap.GetSubGraph(self.G, subgraphNodeIdV)
            print "Network %s: (%d,%d)" % ("induced subgraph " + str(graphId), subG.GetNodes(), subG.GetEdges())
            subgraph1Name = self.graphName + "_" + str(graphId)
            snap.SaveEdgeList(subG, self.targetDir + "/" + subgraph1Name + ".txt")
            lblFile=self.targetDir + "/" + subgraph1Name + ".txt"
            #self.saveLblGraph(subG, lblFile)
            lblFiles.append(lblFile)
            walker.Next()
        return lblFiles;

    def getOverlapSet(self, nodeDegH):
        nodeIdV = snap.TIntV()
        dnodeIdV = snap.TIntV()
        nodeDegH.GetKeyV(nodeIdV)
        randNodeIdV=snap.TIntV()
        # random choice
        if self.overlap_choice == 1:
            randNodeIdV=np.random.choice(nodeIdV, self.overlap_size, replace=False)
        # random choice over the higher degree nodes
        elif self.overlap_choice == 2:
            nodeDegH_walker = nodeDegH.BegI()
            counter=0
            while not nodeDegH_walker.IsEnd():
                if (counter>self.overlap_size*2):
                    break;
                dnodeIdV.Add(nodeDegH_walker.GetKey())
                nodeDegH_walker.Next()
            randNodeIdV = np.random.choice(dnodeIdV, self.overlap_size, replace=False)
        # bsf tree nodes from the highest degree node
        elif self.overlap_choice == 3:
            startNodeId=nodeDegH.BegI().GetKey()
            BfsTree = snap.GetBfsTree(self.G, startNodeId, True, False)
            for EI in BfsTree.Edges():
                sourceNodeId=EI.GetSrcNId()
                if(sourceNodeId not in randNodeIdV):
                    randNodeIdV.Add(sourceNodeId)
                destNodeId = EI.GetDstNId()
                if (destNodeId not in randNodeIdV):
                    randNodeIdV.Add(destNodeId)
                if(randNodeIdV.Len()==self.overlap_size):
                    break;
        # bsf tree nodes from random node
        elif self.overlap_choice == 4:
            startNodeId = np.random.choice(nodeIdV, 1, replace=False)
            #print startNodeId
            BfsTree = snap.GetBfsTree(self.G, startNodeId[0], True, False)
            for EI in BfsTree.Edges():
                sourceNodeId = EI.GetSrcNId()
                #print sourceNodeId
                if (sourceNodeId not in randNodeIdV):
                    randNodeIdV.Add(sourceNodeId)
                destNodeId = EI.GetDstNId()
                #print destNodeId
                if (destNodeId not in randNodeIdV):
                    randNodeIdV.Add(destNodeId)
                if (randNodeIdV.Len() == self.overlap_size):
                    break;



        return randNodeIdV

    def getNodeInducedSubgraphs(self):


        info = ""

        print "Size of the overlap %d" % (self.overlap_size)

        nodeIdV,nodeDegH=self.getNodeDegVector()


        # nodeDegH_walker = nodeDegH.BegI()
        # while not nodeDegH_walker.IsEnd():
        #     overlap_info += "%d,%d\n" % (nodeDegH_walker.GetKey(),nodeDegH_walker.GetDat())
        #     #print "Node Id: %d, degree: %d" % (nodeDegH_walker.GetKey(), nodeDegH_walker.GetDat())
        #     nodeDegH_walker.Next()

        #info+="# overlap_size:%d\n" % (self.overlap_size)


        # Random choice for overlap, better to replace with heuristic
        #randNodeIdV=np.random.choice(nodeIdV, overlap_size, replace=False)
        randNodeIdV=self.getOverlapSet(nodeDegH)

        overlapNodeIdV=snap.TIntV();
        subgraph1NodeIdV = snap.TIntV();
        subgraph2NodeIdV = snap.TIntV();

        #info+="# Node Id,Degree\n"
        for randNodeId in randNodeIdV:
            overlapNodeIdV.Add(randNodeId)
            #print randNodeId, nodeDegH[randNodeId]
            info += "%d,%d\n" % (randNodeId,nodeDegH[randNodeId])
            nodeIdV.DelIfIn(randNodeId)

        #overlapG = snap.TUNGraph.New()
        overlapG = snap.GetSubGraph(self.G, overlapNodeIdV)
        #print "Overlap: ", overlapG.GetNodes()
        #print self.targetDir + "/" + self.graphName+ "-overlap-edges.txt"


        self.writeFile(info,self.targetDir+"/"+self.graphName+"-overlap.txt")

        self.saveGraph(overlapG,self.targetDir + "/" + self.graphName+ "-overlap-edges.txt")
        #self.saveLblGraph(overlapG, self.targetDir + "/" + self.graphName + "-overlap-edges-Lbl.txt")

        non_overlap_size=self.graph_size-self.overlap_size
        subgraph_size=int(non_overlap_size/2)

        randNodeIdV = np.random.choice(nodeIdV, non_overlap_size, replace=False)

        node_count=0
        for randNodeId in randNodeIdV:
            node_count+=1
            if(node_count<=subgraph_size):
                subgraph1NodeIdV.Add(randNodeId)
            else:
                subgraph2NodeIdV.Add(randNodeId)

        subgraph1NodeIdV.AddV(overlapNodeIdV)
        subgraph2NodeIdV.AddV(overlapNodeIdV)

        subgraphNodeIdHV=snap.TIntIntVH(2)
        subgraphNodeIdHV[1]=subgraph1NodeIdV
        subgraphNodeIdHV[2]=subgraph2NodeIdV

        # save unlabeled graph
        #snap.SaveEdgeList(self.G, self.targetDir + "/" + self.graphName + ".txt")
        return self.getSubgraph(subgraphNodeIdHV)




def recursive_split(fn,i):
    if(i>=depth):
        return
    sampling = Sampling(fn, stage, overlap,overlap_choice)
    lblFiles=sampling.getNodeInducedSubgraphs()
    i+=1
    for lblFile in lblFiles:
        recursive_split(lblFile,i)

fileName = sys.argv[1]
stage = sys.argv[2]
overlap = float(sys.argv[3])
overlap_choice = int(sys.argv[4])
depth = int(sys.argv[5])

recursive_split(fileName,0)











                    