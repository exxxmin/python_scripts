import re
import requests
import bs4
import pickle

V = {}          
F1 = set()      
T1 = set()      
F2 = set()      
T2 = set()  

Vpool1 = set()  
Vpool2 = set() 

Vqueue1 = []    
Vqueue2 = []   

v1v2path = []
v2v1path = []

#refs and page name
def get_refs_for_page_name(p_name:str):
    req = requests.get("https://en.wikipedia.org/wiki/"+p_name)
    if req.status_code != 200: 
        return []
    soup = bs4.BeautifulSoup(req.text, features="lxml")
    cont = soup.findAll('div', attrs={'class':'mw-parser-output'})
    refs = []
    for div in cont:
        refs += re.findall(r'href="/wiki/([^:]*?)"',str(div))
    return set(refs)
#random wiki page
def get_random_name():
    req = requests.get("https://en.wikipedia.org/wiki/Special:Random")
    if req.status_code != 200: 
        return ''
    return req.url.split('/').pop()

def empty_vertex():
    v = {}
    v['in'] = set()
    v['out'] = set()
    v['loaded'] = False
    return v

def add_vertex_to_F(vname:str, F:set):
    global V
    
    vtoadd = set()
    newvtoadd = set([vname])
    
    contin = True
    while contin:
        contin = False
        vtoadd = newvtoadd
        newvtoadd = set()
        for name in vtoadd:
            if name not in F:
                v = V.get(name)
                if v!=None:
                    newvtoadd.update(v['out'])
                    contin = True
                F.add(name)

def add_vertex_to_T(vname:str, T:set):
    global V
    
    vtoadd = set()
    newvtoadd = set([vname])
    
    contin = True
    while contin:
        contin = False
        vtoadd = newvtoadd
        newvtoadd = set()
        for name in vtoadd:
            if name not in T:
                v = V.get(name)
                if v!=None:
                    newvtoadd.update(v['in'])
                    contin = True  
                T.add(name)
        
def save_state(fname:str):
    global Vpool1
    global Vpool2
    global Vqueue1
    global Vqueue2
    global F1
    global T1
    global F2
    global T2
    global V
    global v1
    global v2
    
    state = {}
    state['v1'] = v1
    state['v2'] = v2
    state['V'] = V
    state['F1'] = F1
    state['F2'] = F2
    state['T1'] = T1
    state['T2'] = T2
    state['Vqueue1'] = Vqueue1
    state['Vqueue2'] = Vqueue2
    state['Vpool1'] = Vpool1
    state['Vpool2'] = Vpool2
    
    file = open(fname,"wb")
    pickle.dump(state,file)
    file.close()
def process_vpool(poolN):
    global Vpool1
    global Vpool2
    global Vqueue1
    global Vqueue2
    global F1
    global T1
    global F2
    global T2
    global V
    global v1
    global v2
    
    if poolN==1:
        mypool = Vpool1
        hispool = Vpool2
        myqueue = Vqueue1
        hisqueue = Vqueue2
        myF = F1
        myT = T1
        hisF = F2
        hisT = T2
        myv = v1
        hisv = v2
    else:
        mypool = Vpool2
        hispool = Vpool1
        myqueue = Vqueue2
        hisqueue = Vqueue1
        myF = F2
        myT = T2
        hisF = F1
        hisT = T1
        myv = v2
        hisv = v1
    
    name = ''
    while len(myqueue)>0 and len(name)==0:
        name = myqueue.pop(0)   
        if name not in mypool:
            name = ''
           
    if len(name)==0:        
        return 0
    
    print(name)
    
    myvertex = V.get(name)
    if myvertex == None:       
        print('Vertex ws in Vpool'+str(poolN)+', but was not in V lol')
        myvertex = empty_vertex()
        V[name] = myvertex
        
    outnames = set()
    outnames = get_refs_for_page_name(name) 
    myvertex['out'] = outnames              
    inmyT = False
    inhisT = False
    for oname in outnames:
        overtx = V.get(oname)       
        if overtx == None:
            overtx = empty_vertex()
            V[oname] = overtx
            mypool.add(oname)
            myqueue.append(oname)
        overtx['in'].add(name)      
       
        if oname == myv or oname in myT:
            inmyT = True  
      
        if oname == hisv or oname in hisT:
            inhisT = True           
    
   
    for oname in outnames:
        add_vertex_to_F(oname,myF)   
    mypool.discard(name)
    if name in hisF:
        for oname in outnames:
            add_vertex_to_F(oname,hisF)
    hispool.discard(name)
    
   
    if inmyT:
        add_vertex_to_T(name,myT)
    if inhisT:
        add_vertex_to_T(name,hisT)
        
def find_path_in_FTset(FTset:set, vf:str, vt:str):
    global V
    
    lengths = {}
    FTset.add(vf)
    FTset.add(vt)
    lengths[-1] = set(FTset)
    lengths[0] = set()
    lengths[0].add(vf)
    lengths[-1].discard(vf)
    i=1
    notfinished = True
    while len(lengths[-1]) and notfinished and i<50:
        lengths[i] = set()
        for vn in lengths[i-1]:
            v = V[vn]
            for vnn in v['out']:
                if vnn in lengths[-1]:
                    lengths[i].add(vnn)
                    lengths[-1].discard(vnn)
                    if vnn == vt:
                        notfinished = False
        i+=1
    
    path = [vt]
    for j in range(2,i):
        v = V[path[0]]
        path.insert(0,(v['in']&lengths[i-j]).pop())
    path.insert(0,vf)
    return path
    

if __name__ == '__main__':

    v1 = get_random_name()
    v2 = get_random_name()
    print("From: " + str(v1))
    print("To: " + str(v2))
    
    if len(Vpool1)==0:
        Vqueue1 = [v1]
        Vpool1 = set(Vqueue1)
    if len(Vpool2)==0:
        Vqueue2 = [v2]
        Vpool2 = set(Vqueue2)
    
  
    for i in range(1000):
        process_vpool(1)
        process_vpool(2)

        if len(v1v2path) == 0:
            int12 = F1&T2
            if len(int12):
                v1v2path = find_path_in_FTset(F1&T2, v1, v2)
                print("F1&T2 = " + str(int12))
            else:
                print("F1&T2 is empty")
        if len(v1v2path) > 0:
            print("v1 -> v2 len: " + str(len(v1v2path)-1) + " path: " + str(v1v2path))
            
        if len(v2v1path) == 0:
            int21 = F2&T1
            if len(int21):
                v2v1path = find_path_in_FTset(F2&T1, v2, v1)
                print("F2&T1 = " + str(int21))
            else:
                print("F2&T1 is empty")
        if len(v2v1path) > 0:
            print("v2 -> v1 len: " + str(len(v2v1path)-1) + " path: " + str(v2v1path))

        print("Iteration "+str(i))

        print("\n")

        if len(v1v2path)>0 and len(v2v1path)>0:
            print("page1 -> page2 len: " + str(len(v1v2path)-1) + " path: " + str(v1v2path))
            print("\npage2 -> page1 len: " + str(len(v2v1path)-1) + " path: " + str(v2v1path))
            print("\ntotal requests made: " + str(i*2))
            break
    save_state("test.pkl")