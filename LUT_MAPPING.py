# -*- coding: utf-8 -*-
"""
@author: abhishek konale
"""

import pyeda 
from pyeda.inter import *
import math

from copy import deepcopy

import pydotplus as pydot

#Colors used in visualizing graph partitions
#X11 Color Codes
colors = \
[
    #Aqua               --1
        u'#00FFFF',
    #Blue Violet        --2
        u'#8A2BE2',
    #Burlywood          --3
        u'#DEB887',
    #Chartreuse         --4	
        u'#7FFF00',
    #Crimson            --5
        u'#DC143C',
    #Dark Orange        --6
        u'#FF8C00',
    #Deep Pink          --7
        u'#FF1493',
    #Gold 	         --8
        u'#FFD700',
    #Green 	         --9
        u'#00FF00',
    #Light Blue         --10	
        u'#ADD8E6',
    #Red 	              --11
        u'#FF0000',
    #Yellow 	         --12
        u'#FFFF00',
    #Light Salmon       --13
        u'#FFA07A',
    #Tan                --14	
        u'#D2B48C',
    #Web Purple         --15
        u'#7F007F'
]
 
 
#//////////////////////////////////////////////////////////////////////////////
#supported operators tuple
Operators   = ('or','and','xor','not')

edge_list   = []

#node_list
p_o_list    = []

Fanout      = {}

#Dictionary having optimal costs for each node
Optimal_Costs       = {}
#Dictionary having optimal grouping for each node
Optimal_Partitions  = {}


#Final grouping of two input gates
LUT_Mappings        = []

#Connections,Logic Expression,Bits to be filled for each 6-LUT
LUT_Info            = {}

#//////////////////////////////////////////////////////////////////////////////
#Decomposing AST
index = 0
def postorder(tree):
    global index,p_o_list,Optimal_Costs
      
    if len(tree[1])>2:
        postorder(tree[1])
    else:
        label = str(pyeda.boolalg.expr._LITS[tree[1][1]])+'_'+str(index)
        Optimal_Costs[label] = 0
        p_o_list.append(label)
        index += 1
        
    if len(tree[2])>2:
        postorder(tree[2])
    else:
        label = str(pyeda.boolalg.expr._LITS[tree[2][1]])+'_'+str(index)
        Optimal_Costs[label] = 0
        p_o_list.append(label)
        index += 1
          
    p_o_list.append(tree[0] + str(index))
    index += 1
    
        
#//////////////////////////////////////////////////////////////////////////////     
def Generate_Fanout_List():
    global edge_list,p_o_list
    Stack = []
    
    for i in p_o_list:
        if i[:3] in Operators or i[:2] in Operators:
            temp_R      = Stack.pop()
            temp_L      = Stack.pop()
            Fanout[i]   = [temp_L,temp_R]
            
            edge_list.append([i,temp_L])
            edge_list.append([i,temp_R])
            Stack.append(i)
        else:
            Stack.append(i)
    
   

#//////////////////////////////////////////////////////////////////////////////  
def Get_Cost(temp_grp):
    global Optimal_Costs,Fanout
    cost_temp = 1
    for n in temp_grp:
        if Fanout[n][0] not in temp_grp:
            cost_temp += Optimal_Costs[Fanout[n][0]]
        if Fanout[n][1] not in temp_grp:
            cost_temp += Optimal_Costs[Fanout[n][1]]
    return cost_temp
            


#//////////////////////////////////////////////////////////////////////////////
def Find_Optimal_Partions():
    global Optimal_Costs,Optimal_Partitions,p_o_list,Fanout
          
    for i in p_o_list: 
        
        if i[:3] in Operators or i[:2] in Operators:
            Depth_1_list = []
            Depth_2_list = []
            Depth_3_list = []
            Depth_4_list = []
            cost_min     = math.inf 
            grp          = []
            
            for f in Fanout[i]:
                if f[:3] in Operators or f[:2] in Operators:
                    Depth_1_list.append(f)
                
                        
            for g in Depth_1_list:
                if g!=None:
                    if g[:3] in Operators or g[:2] in Operators:
                        for h in Fanout[g]:
                            if h[:3] in Operators or h[:2] in Operators:
                                Depth_2_list.append(h)
                                        
            for k in Depth_2_list:
                if k!=None:
                    if k[:3] in Operators or k[:2] in Operators:
                        for l in Fanout[k]:
                            if l[:3] in Operators or l[:2] in Operators:
                                Depth_3_list.append(l)
                                        
            for m in Depth_3_list:
                if m!=None:
                    if m[:3] in Operators or m[:2] in Operators:
                        for n in Fanout[m]:
                            if n[:3] in Operators or n[:2] in Operators:
                                Depth_4_list.append(n)
                            


#//////////////////////////////////LEVEL 6/////////////////////////////////////  
#combination: 1 1 1 1 1
                           
            for p in Depth_1_list:
                for k in Depth_2_list:
                    for l in Depth_3_list:
                        for m in Depth_4_list:
                            if k in Fanout[p] and l in Fanout[k] and m in Fanout[l]:
                                temp_grp    = [i,p,k,l,m]
                                cost_temp   = Get_Cost(temp_grp)                            
                                if cost_temp<cost_min:
                                    cost_min    = cost_temp
                                    grp         = temp_grp  
    
                                
#combination: 1 2 2
                          
            for p in Depth_1_list:
                for k in Depth_1_list:
                    if k!=p:
                        for l in Depth_2_list:
                            for m in Depth_2_list:
                                if m!=l:
                                    temp_grp    = [i,p,k,l,m]
                                    cost_temp   = Get_Cost(temp_grp)
                                    if cost_temp<cost_min:
                                        cost_min    = cost_temp
                                        grp         = temp_grp  
                                        
                                        
#combination: 1 1 1 2
                          
            for p in Depth_1_list:
                for k in Depth_2_list:
                    for l in Depth_3_list:
                        for m in Depth_3_list:
                            if m!=l and k in Fanout[p] and l in Fanout[k] and m in Fanout[k]:
                                temp_grp    = [i,p,k,l,m]
                                cost_temp   = Get_Cost(temp_grp)
                                if cost_temp<cost_min:
                                    cost_min    = cost_temp
                                    grp         = temp_grp  


#combination: 1 2 1 1
                          
            for p in Depth_1_list:
                for k in Depth_1_list:
                    if k!=p:
                        for l in Depth_2_list:
                            for m in Depth_3_list:
                                if m in Fanout[l]:
                                    temp_grp    = [i,p,k,l,m]
                                    cost_temp   = Get_Cost(temp_grp)
                                    if cost_temp<cost_min:
                                        cost_min    = cost_temp
                                        grp         = temp_grp  
                                        
#combination: 1 1 2 1
                         
            for p in Depth_1_list:
                for k in Depth_2_list:
                    for l in Depth_2_list: 
                        if l!=k and k in Fanout[p] and l in Fanout[p]:
                            for m in Depth_3_list:
                                if m in Fanout[k] or m in Fanout[l]:
                                    temp_grp    = [i,p,k,l,m]
                                    cost_temp   = Get_Cost(temp_grp)
                                    if cost_temp<cost_min:
                                        cost_min    = cost_temp
                                        grp         = temp_grp  
                    
            
#//////////////////////////////////LEVEL 5/////////////////////////////////////  
#combination: 1 1 1 1                          
            for p in Depth_1_list:
                for k in Depth_2_list:
                    for l in Depth_3_list:
                        if k in Fanout[p] and l in Fanout[k]:
                            temp_grp    = [i,p,k,l]
                            cost_temp   = Get_Cost(temp_grp)
                            if cost_temp<cost_min:
                                cost_min    = cost_temp
                                grp         = temp_grp     
#combination: 1 1 2
                         
            for p in Depth_1_list:
                for k in Depth_2_list:
                    for l in Depth_2_list:
                        if l!=k and l in Fanout[p] and k in Fanout[p]:
                            temp_grp    = [i,p,k,l]
                            cost_temp   = Get_Cost(temp_grp)
                            if cost_temp<cost_min:
                                cost_min    = cost_temp
                                grp         = temp_grp  
#combination: 1 2 1
                        
            for p in Depth_1_list:
                for k in Depth_1_list:
                    if k!=p:
                        for l in Depth_2_list:  
                            temp_grp    = [i,p,k,l]
                            cost_temp   = Get_Cost(temp_grp)
                            if cost_temp<cost_min:
                                cost_min    = cost_temp
                                grp         = temp_grp 


#//////////////////////////////////LEVEL 4/////////////////////////////////////  
#combination: 1 1 1
                         
            for p in Depth_1_list:
                for k in Depth_2_list:
                    if k in Fanout[p]:
                        temp_grp    = [i,p,k]
                        cost_temp   = Get_Cost(temp_grp)                    
                        if cost_temp<cost_min:
                            cost_min    = cost_temp
                            grp         = temp_grp
                        
#combination: 1 2
                         
            for p in Depth_1_list:
                for k in Depth_1_list:
                        if k!=p:                           
                            temp_grp    = [i,p,k]
                            cost_temp   = Get_Cost(temp_grp)
                            if cost_temp<cost_min:
                                cost_min    = cost_temp
                                grp         = temp_grp
 
#//////////////////////////////////LEVEL 3/////////////////////////////////////  
#combination: 1 1  
                    
            for p in Depth_1_list: 
                temp_grp    = [i,p]
                cost_temp   = Get_Cost(temp_grp)
                if cost_temp<cost_min:
                    cost_min    = cost_temp
                    grp         = temp_grp
                         
#//////////////////////////////////LEVEL 2///////////////////////////////////// 
#combination: 1

            temp_grp    = [i]                        
            cost_temp   = Get_Cost(temp_grp)
            if cost_temp<cost_min:
                cost_min    = cost_temp
                grp         = temp_grp
                

                
            Optimal_Costs[i]        = cost_min
            Optimal_Partitions[i]   = grp
  

                                           
#////////////////////////////////////////////////////////////////////////////// 
def Map_To_LUTs():
    global LUT_Mappings,Operators,p_o_list
    
    Covered_List        = []
    Traversal_List      = deepcopy(p_o_list)
    Traversal_List.reverse()
    
    for i in Traversal_List:
        if (i[:3] in Operators or i[:2] in Operators) and i not in Covered_List :
            LUT_Mappings.append(Optimal_Partitions[i])
            for j in Optimal_Partitions[i]:
                Covered_List.append(j)
        
      
      
#//////////////////////////////////////////////////////////////////////////////       
def Visualize_Optimal_Partitions(Partitions,edge_list,node_list):
    global colors
    graph = pydot.Dot(graph_type = 'digraph', nodesep = .5)
    graph.set_node_defaults(style = "filled",shape = "rect",fontsize = "20.0")
    graph.set_edge_defaults(color = 'blue', arrowhead = "vee")
    
    temp_dict = {}
    count = 0
    
    #Highlight Groups of Two Input Gates mapped to same LUT
    for i in Partitions:
        for j in i:            
            temp_dict[j] = pydot.Node(j, color = colors[count])
            graph.add_node(temp_dict[j])
        count+= 1          
            
    #base/input nodes highlighted in grey color
    for i in node_list:
        if i[:3] not in Operators and i[:2] not in Operators:
            temp_dict[i] = pydot.Node(i, color= u'#DCDCDC')
            graph.add_node(temp_dict[i])
          
    #Add edges
    for i in edge_list:
        graph.add_edge(pydot.Edge(temp_dict[i[0]],temp_dict[i[1]]))
        
    #Store result in a file
    graph.write_png('partion_graph.png')
    
    
#//////////////////////////////////////////////////////////////////////////////   
def LUT_Map(Expr):
    global edge_list,LUT_Mappings,p_o_list
    Result_File = open( 'RESULT.txt', 'w' )

    Input_Expr = expr(Expr,simplify = False)
    BinTree = Input_Expr.to_ast()
    
    postorder(BinTree)
    
    Generate_Fanout_List()
    
    Find_Optimal_Partions()
        
    print('Optimal Costs....')
    print('\n',Optimal_Costs,'\n')    
    print('Total Cost :',Optimal_Costs[p_o_list[-1]],'\n')
    
    Map_To_LUTs()
     
    print('LUT Mappings....\n')
    count = 1
    for i in LUT_Mappings:
        print('LUT'+str(count)+': ',i,'\n')
        
        LUT_Info['LUT'+str(count)] = LUT()
        LUT_Info['LUT'+str(count)].Configure(i)
        
        Result_File.write('LUT'+str(count)+'\n\n')
        Result_File.write('Truth Table\n\n')
        Result_File.write(repr(LUT_Info['LUT'+str(count)].TT ))
        Result_File.write('\n\nExpression\n\n')
        Result_File.write(repr(LUT_Info['LUT'+str(count)].f))
        Result_File.write('\n\nConnections\n\n')
        Result_File.write(repr(LUT_Info['LUT'+str(count)].Connections))
        Result_File.write('\n\n\n\n\n')
        
        count += 1
    Result_File.close()   
    Visualize_Optimal_Partitions(LUT_Mappings,edge_list,p_o_list)
        


#//////////////////////////////////IN- DEVELOPMENT/////////////////////////////

class LUT():        
    def __init__(self):
        self.A  = exprvar('A')
        self.B  = exprvar('B')
        self.C  = exprvar('C')
        self.D  = exprvar('D')
        self.E  = exprvar('E')
        self.F  = exprvar('F')
        self.Connections = {}
        
    #def Configure(self,OP_list,InterConnect):
    def Configure(self,OP_list):
         global Fanout
         Stack  = []
         CHAR   = ord('A')
         L = ''
         R = ''
         
         #self.sig = {'A':None,'B':None,'C':None,'D':None,'E':None,'F':None}
         for i in range(len(OP_list)-1,-1,-1):
             temp = OP_list[i]
             if  Fanout[temp][0] not in OP_list:  
                if Fanout[temp][0][:3] in Operators or Fanout[temp][0][:2] in Operators:
                    for j in range (len(LUT_Mappings)):
                         if Fanout[temp][0] in LUT_Mappings[j]:
                             self.Connections[chr(CHAR)] = 'LUT'+ str(j+1)
                             L = chr(CHAR)
                             
               
                else:              
                     if Fanout[temp][0][0] == '~':
                         L  = '~'+chr(CHAR)
                         self.Connections[chr(CHAR)] =  Fanout[temp][0][1]
                        
                     else:
                         L = chr(CHAR)
                         self.Connections[chr(CHAR)] =  Fanout[temp][0][0]
    
                CHAR += 1
            
             
             else:
                 L = Stack.pop()
                                 
                 
             if Fanout[temp][1] not in OP_list:
                 if Fanout[temp][1][:3] in Operators or Fanout[temp][1][:2] in Operators:
                    for j in range(len(LUT_Mappings)):
                         if Fanout[temp][1] in LUT_Mappings[j]:
                             self.Connections[chr(CHAR)] = 'LUT'+ str(j+1)
                             R = chr(CHAR)
                             
               
                 else:                      
                     if Fanout[temp][1][0] == '~':
                         R = '~'+chr(CHAR)
                         self.Connections[chr(CHAR)] =  Fanout[temp][1][1]
                     else:
                         R = chr(CHAR)
                         self.Connections[chr(CHAR)] =  Fanout[temp][1][0]
                 
                 CHAR += 1
                 
             else:
                 R = Stack.pop()
                 

             if temp[:3]     == 'xor':
                 Stack.append('('+L+'^'+R +')')
             elif temp[:2]   == 'or':
                 Stack.append('('+L+'|'+R+')')
             elif temp[:3]   == 'and':
                 Stack.append('('+L+'&'+R+')')
             
         self.f = expr(Stack.pop(),simplify = False)
         
         #Bits to be filled in 6-LUT
         self.TT = expr2truthtable(self.f) 
         
           
  
#////////////////////////////INSERT EXPRESSION HERE////////////////////////////
#TestCase
#Expr = '(s|m^(g&j|h^y)&u)|j^t&y&(b|(a|n^g&b)|m)^(f|h&j&~i)^t&(a|~f|k)^y|k'
Expr = 'd|(e&f)^(a&s)|(t|e)|(f^g&j)&(h|b|(k^f)^y)&(t&n)^m'

LUT_Map(Expr)
#//////////////////////////////////////////////////////////////////////////////
