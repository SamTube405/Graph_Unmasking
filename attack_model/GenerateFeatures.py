import snap
import sys
import numpy as np
import itertools as it
import random
import pandas as pd
import os
import errno


class Scoop:

    def __init__(self, fileName1, fileName2, overlap_filename,examples, directed):
        self.rootDir=self.getPairsDir(fileName1)+"pairs"
        self.fileName1 = fileName1
        self.fileName2 = fileName2

        #print os.path.abspath(overlap_filename)
        self.df_overlap=pd.read_csv(os.path.abspath(overlap_filename),index_col=None, header=None)
        self.df_overlap.columns=['node_id','degree']

        self.examples=examples
        self.directed = directed


        self.G1 = self.getGraph(fileName1)
        print "[Load] G1."
        self.G2 = self.getGraph(fileName2)
        print "[Load] G2."


        self.ndd1HG1=snap.TIntStrH()
        self.ndd2HG1=snap.TIntStrH()

        self.ndd1HG2=snap.TIntStrH()
        self.ndd2HG2=snap.TIntStrH()

        self.graph1Name = self.getGraphName(fileName1)
        self.graph2Name = self.getGraphName(fileName2)



    def getGraph(self,fileName):
        return snap.LoadEdgeList(snap.PUNGraph, fileName)

    def getNodeIdLabel(self,G):
        gLH = snap.TIntStrH()
        for EI in G.Edges():
            srcId = EI.GetSrcNId()
            dstId = EI.GetDstNId()

            EI=G.GetEI(srcId, dstId)

            srcAttr="srcLabel"
            srcAttrVal=G.GetStrAttrDatE(EI, srcAttr)

            dstAttr="dstLabel"
            dstAttrVal=G.GetStrAttrDatE(EI, dstAttr)

            gLH[srcId]=srcAttrVal
            gLH[dstId]=dstAttrVal
        return gLH

    def getLblGraph(self,fileName):
        context = snap.TTableContext()

        schema = snap.Schema()
        schema.Add(snap.TStrTAttrPr("srcLabel", snap.atStr))
        schema.Add(snap.TStrTAttrPr("srcId", snap.atInt))
        schema.Add(snap.TStrTAttrPr("dstLabel", snap.atStr))
        schema.Add(snap.TStrTAttrPr("dstId", snap.atInt))

        table = snap.TTable.LoadSS(schema, fileName, context, " ", snap.TBool(False))
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


    def getGraphName(self,fileName):
        tags = fileName.split("/")
        return tags[len(tags) - 1].split(".")[0]


    def random_subset(iterator, K):
        result = []
        N = 0

        for item in iterator:
            N += 1
            if len(result) < K:
                result.append(item)
            else:
                s = int(random.random() * N)
                if s < K:
                    result[s] = item

        return result

    def getPairsDir(self,fileName):
        path=""
        tags = fileName.split("/")
        for i in range(0,len(tags)-1):
            path+=tags[i]+"/"
        return path

    def asString(self,nddV):
        text=""
        for ndd in nddV:
            text+=str(ndd)+","
        return  text;

    def genNDDH(self,G):
        ndd1H=snap.TIntStrH()
        ndd2H = snap.TIntStrH()
        n=G.GetNodes()
        print "# of nodes: %d" % n
        i=0
        for node in G.Nodes():
            nddV=self.get1HNDD(G,node)
            ndd1H[node.GetId()]=self.asString(nddV)
            nddV=self.get2HNDD(G,node)
            ndd2H[node.GetId()]=self.asString(nddV)
            i+=1;
            progress=float(i)/n
            print "[progress] %f\n" % progress
        return ndd1H,ndd2H

    def getNodeIdV(self,G):
        nodeIdV=[]
        for node in G.Nodes():
            nodeIdV.append(node.GetId())
        return nodeIdV


    def mgenNDD(self,G,node,isG1):
        ndd1H=self.ndd1HG2
        ndd2H=self.ndd2HG2
        if(isG1==True):
            ndd1H=self.ndd1HG1
            ndd2H=self.ndd2HG1

        if((node.GetId() in ndd1H) and (node.GetId() in ndd2H)):
            return ndd1H[node.GetId()],ndd2H[node.GetId()]
        else:
            nddV,nldV=self.get1HNDD(G,node)
            ndd1H[node.GetId()]=self.asString(nddV,nldV)
            nddV,nldV=self.get2HNDD(G,node)
            ndd2H[node.GetId()]=self.asString(nddV,nldV)
            return ndd1H[node.GetId()],ndd2H[node.GetId()]


    def chkDir(self,path):
        if not os.path.exists(os.path.dirname(path)):
            try:
                os.makedirs(os.path.dirname(path))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

    def getLabel(self, NId1, NId2):
        label=0
        #print NId1, NId2, N1_Attr, N2_Attr
        if NId1 == NId2:
            label=1
            # if N1_Attr == "C":
            #     label=1
            # else:
            #     label=2
        return label

    def getNodeLabel(self,attribute):
        indexLabel="-1"
        if(attribute in self.lblV):
            if(attribute == self.lblV[0]):
                indexLabel="0";
            else:
                indexLabel="1";
        return indexLabel

    def getLabelId(self,N_Attr):
        # C
        id="0,1"
        if(N_Attr==self.attr2):
            id="1,0"
        return id

    def genNodePairs(self):
        print "[G1] NDD..."
        ndd1HG1,ndd2HG1 = self.genNDDH(self.G1)
        print "[G2] NDD..."
        ndd1HG2,ndd2HG2 = self.genNDDH(self.G2)
        #counter=0
        #identical_nodes=""
        #f = open(self.rootDir+"/"+self.graph1Name+"-identical-nodes.txt","w+")
        total=self.G1.GetNodes()*self.G2.GetNodes()
        text="# possible generated pairs 1M/%d, (%d,%d)" % (total,self.G1.GetNodes(),self.G2.GetNodes())
        print("%s"% text)


        nodeId1V=self.getNodeIdV(self.G1)

        nodeId2V=self.getNodeIdV(self.G2)

        identicalNodeIdV = self.df_overlap['node_id']
        icounter=len(identicalNodeIdV)


        nodeId1VF=list(set(nodeId1V) - set(identicalNodeIdV))
        nodeId2VF=list(set(nodeId2V) - set(identicalNodeIdV))

        print "Identicals: %d" % icounter
        print "N1IdV: %d, Filtered: %d" % (len(nodeId1V),len(nodeId1VF))
        print "N2IdV: %d, Filtered: %d" % (len(nodeId2V),len(nodeId2VF))
        print "Filtered identicals:[] ",list(set(nodeId1VF).intersection(nodeId2VF))
        
        cthreshold=len(nodeId1VF)*len(nodeId2VF)
        threshold=min(cthreshold,1000000)

        df_matrix = []

        counter=0
        while(counter<threshold):

            N1Id=np.random.choice(nodeId1VF)
            N2Id=np.random.choice(nodeId2VF)
            #print N1Id,N2Id

            node1=self.G1.GetNI(N1Id)
            node2=self.G2.GetNI(N2Id)


            # class label
            label=self.getLabel(N1Id,N2Id)

            ndd1N1=ndd1HG1[N1Id]
            ndd2N1=ndd2HG1[N1Id]
            ndd1N2=ndd1HG2[N2Id]
            ndd2N2=ndd2HG2[N2Id]

            row = [ndd1N1, ndd2N1,ndd1N2, ndd2N2, str(label)]
            counter+=1
            print "[non-identical] sampled pair: %d" % counter
            df_matrix.append(row)


        df = pd.DataFrame(df_matrix, columns=('1hop-sig-n1', '2hop-sig-n1','1hop-sig-n2', '2hop-sig-n2', 'label'))



        df_matrix = []

        counter=0

        for identicalNodeId in identicalNodeIdV:
            N1Id=N2Id=identicalNodeId

            node1=self.G1.GetNI(N1Id)
            node2=self.G2.GetNI(N2Id)


            # class label
            label=self.getLabel(N1Id,N2Id)

            ndd1N1=ndd1HG1[N1Id]
            ndd2N1=ndd2HG1[N1Id]

            ndd1N2=ndd1HG2[N2Id]
            ndd2N2=ndd2HG2[N2Id]

            row = [ndd1N1, ndd2N1,ndd1N2, ndd2N2, str(label)]
            counter+=1
            print "[identical] sampled pair: %d" % counter
            df_matrix.append(row)



        idf = pd.DataFrame(df_matrix, columns=('1hop-sig-n1', '2hop-sig-n1','1hop-sig-n2', '2hop-sig-n2', 'label'))


        all_samples = int(icounter * 1.5)
        i_samples = int(icounter * 0.75)

        print("going to sample examples (%d,%d)" % (all_samples, i_samples))
        for i in range(0, self.examples):
            arows = np.random.choice(df.index.values, all_samples)
            irows = np.random.choice(idf.index.values, i_samples)
            print("picked (%d,%d)" % (len(arows), len(irows)))
            asampled_df = df.ix[arows]
            isampled_df = idf.ix[irows]
            sampled_df = asampled_df.append(isampled_df)

            sample_fn = self.rootDir + "/" + self.graph1Name + "_" + str(i + 1) + "-pairs.txt"
            sampled_df.to_csv(sample_fn, sep=' ', encoding='utf-8', mode='w', index=False)


            print("Saved sample %d at %s" % (i + 1, sample_fn))


        print "Graph name: %s identical node pairs: %s" % (self.graph1Name, icounter)


    def getNeighborLabel(self,neighbor):
        nlabel=""
        if(neighbor in self.G1LH):
            nlabel = self.G1LH[neighbor]
        elif(neighbor in self.G2LH):
            nlabel = self.G2LH[neighbor]
        return nlabel


    # get 1-hop neighborhood degree dist
    def get1HNDD(self,G,node, bins=21, bin_size=50,directed=False):
        nddV=np.zeros(bins)
        neighborV=node.GetOutEdges()
        if(directed):
            neighborV.AddV(node.GetInEdges())

        for neighbor in neighborV:
            nIndex=int(round(G.GetNI(neighbor).GetOutDeg()/bin_size))%bin_size
            if(nIndex>bins-1):
                nIndex=bins-1
            nddV[nIndex]+=1


        return nddV;

    # get 2-hop neighborhood degree dist
    def get2HNDD(self, G, node, bins=21, bin_size=50,directed=False):
        nddV = np.zeros(bins)
        neighborV = node.GetOutEdges()
        if (directed):
            neighborV.AddV(node.GetInEdges())
        for neighbor in neighborV:
            for next_neighbor in G.GetNI(neighbor).GetOutEdges():
                nIndex = int(round(G.GetNI(next_neighbor).GetOutDeg() / bin_size)) % bin_size
                if (nIndex > bins - 1):
                    nIndex = bins - 1
                nddV[nIndex] += 1

        return nddV;


if __name__ == '__main__':
    fileName1 = sys.argv[1]
    fileName2 = sys.argv[2]

    overlap_filename = sys.argv[3]

    examples = int(sys.argv[4])

    scoop = Scoop(fileName1, fileName2, overlap_filename, examples, directed=False)

    scoop.genNodePairs()