#rq4:总测试用例池中，随机地选择10%，20%，30%， 40%， 50%规模的测试用例集合。（各100个）
#计算其SC：基于覆盖矩阵
#计算其BC：合并ser文件，GetBranchCov
#计算各个变异得分metric：基于kill矩阵
#计算其ground truth:0未检测到缺陷，1检测到缺陷
#在size control的前提下（例如只比较10%的100个测试用例集合），计算统计学指标，例如MS vs Ground Truth。即两组100长度的list计算相关性。
import glob

import GetBranchCov

import re
import os
import io
import subprocess
import csv
import numpy as np
import scipy as sp
from sklearn import cluster
import random
random.seed(1)
np.random.seed(0)
#pv示例：-p Lang -v 1f
def getfixversion(pv):
    p=subprocess.Popen('defects4j checkout '+pv+' -w /tmp/0926',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    p.communicate()





#1:获得trigg test：
#有多个就一一注释掉
def gettriggertest(cwdpath):
    p=subprocess.Popen('cat defects4j.build.properties',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=cwdpath)
    z=p.stdout.read()
    z=str(z)
    p.communicate()
    lis=z.split('d4j.tests.trigger=')
    triggertest=lis[-1][:-3]
    c=triggertest.count("::")
    if c>1:
        print('more than one triggertests')
    return triggertest




#2：读取覆盖矩阵：
import csv

# 读取 testMap.csv 文件

def getTestMap(mappath):
    test_map = {}
    with open(mappath, 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # 跳过表头行
        for row in csv_reader:
            #第一个test 编号0
            test_no = int(row[0])-1
            test_name = row[1]
            test_map[test_name] = test_no
    return test_map


def getNumberOfM(mutantlogpath,cwdpath="."):
    #统计文件行数即可
    p=subprocess.Popen('wc -l '+mutantlogpath,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=cwdpath)
    z=p.stdout.read()
    z=str(z)[2:].split(" ")[0]
    p.communicate()
    return int(z)

def getLabelArray(workpath):
    # 读取 killMap.csv 文件并生成 labelarray 矩阵
    killmappath=workpath+"/killMap.csv"
    mutantlogpath=workpath+"/mutants.log"
    nm=getNumberOfM(mutantlogpath)
    testmap=getTestMap(workpath+"/testMap.csv")
    labelarray = [[0] * nm for _ in range(len(testmap))]
    with open(killmappath, 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # 跳过表头行
        for row in csv_reader:
            test_no = int(row[0])-1
            mutant_no = int(row[1])-1
            killed = row[2]
            if killed:
                labelarray[test_no][mutant_no]=1
    return testmap,labelarray



#0：测试用例集合中采样：
def Sample(testmap,ratio):
    x=len(testmap)
    n = int(ratio * x)
    sample_list = random.sample(range(x), n)
    return sample_list



#计算变异得分
def computeMS(labelarray,testlist,mutantlist):
    newlabel=[]
    for t in testlist:
        tlabel=[]
        for m in mutantlist:
            tlabel.append(labelarray[t][m])
            #print(tlabel)
        newlabel.append(tlabel)
    killed=0
    for i in range(0,len(mutantlist)):
        x=0
        for j in range(0,len(testlist)):
            x=x+newlabel[j][i]
            if x==1:
                killed=killed+1
                break
    return float(killed)/len(mutantlist)




def copy(path,aimpath,atpath):
    p=subprocess.Popen('\cp -rf '+path+' '+aimpath,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=atpath)
    p.communicate()

#3.3.1SMS
#先把之前写的两个函数拿过来
def getDMSG(coverarray):
    l=np.array(coverarray)
    z=l.T
    ans=[]
    index=[]
    count=0
    for zi in range(0,len(z)):
        if sum(z[zi])==0:
            count=count+1
            continue
        if ans==[]:
            ans.append(z[zi])
            index.append(zi)
            continue
        else:
          for an in range(0,len(ans)):
            tobe=0
            if -1 not in ans[an]-z[zi]:
                ans=[z[zi]]+ans[:an]+ans[an+1:]
                index=[zi]+index[:an]+index[an+1:]
                #ans.remove(ans[an])
                #index.remove(an)
                tobe=1
            if an==len(ans)-1 and tobe==0:
                for bn in range(0,len(ans)):
                    if 1 not in ans[bn]-z[zi]:
                        break
                    if bn==len(ans)-1:
                        ans.append(z[zi])
                        index.append(zi)
                        #print(len(index))
    #过半是0
    if count*2>=len(coverarray[0]):
        print('error')
    return [ans,index]



#于getDMSG发现一个问题，xn中有重复的变异体。
#用于去除getDMSG中重复的输出
def filterxn(xn):
    yn0=[]
    yn1=[]
    for x0 in xn[0]:
        if yn0==[]:
            yn0.append(list(x0))
        elif list(x0) != yn0[-1]:
            yn0.append(list(x0))
    for x1 in xn[1]:
        if x1 not in yn1:
            yn1.append(x1)
    return [yn0,yn1]


#triggerlis=triggertest.split(',')


def getSMSmutantlist(coverarray):
    xn = getDMSG(coverarray)
    xn = filterxn(xn)
    mutantlist = xn[1]
    return mutantlist

#给定测试用例集合，返回SMS：，为了提高效率，把mutantlist作为参数传进去
def getSMS(coverarray,selectedtest,mutantlist):
    #先算coverarray的变异得分
    sms=computeMS(coverarray,selectedtest,mutantlist)
    return sms


#3.3.2CMS






#聚类选择的实现：输入【覆盖矩阵，SMS选择的变异体编号】
#输出CMS选择的变异体编号
def clustermutant(coverarray,mutantlist):
    h=np.array(coverarray).T
    #聚类个数等于SMS选择的变异体个数
    n_clusters=len(mutantlist)
    #初始化聚类中心
    ini=[]
    for i in mutantlist:
        ini.append(h[i])
    ini=np.array(ini)
    k_means = cluster.KMeans(n_clusters=n_clusters,init=ini)
    k_means.fit(h)
    #values = k_means.cluster_centers_.squeeze()
    labels = k_means.labels_
    #按labels每个类取一个
    selected=[]
    ans=[]
    while len(selected)!=len(mutantlist):
        num=random.randint(0,len(labels)-1)
        if labels[num] not in selected:
            selected.append(labels[num])
            ans.append(num)
    return ans






#3.4RMS 选30%
def getRMS(labelarray):
    allmutantlist=[]
    randmutantlist=[]
    for i in range(0,len(labelarray[0])):
        allmutantlist.append(i)
    while int(len(allmutantlist)*0.3)!=len(randmutantlist):
        num=random.randint(0,len(allmutantlist)-1)
        if allmutantlist[num] not in randmutantlist:
            randmutantlist.append(allmutantlist[num])
    return randmutantlist


#3.5COS 麻烦一点，要先把变异体和变异算子映射起来。ROR,AOR,UOI,ABS,LCR
#AOR,ROR,LOR,ORU这四个，其他四个删除。LVR还是算进去，囊括了ABS。
#mutatorpath='/tmp/lang_1_f2/mutants.log'
def getCOS(mutatorpath):
    p=subprocess.Popen('cat '+mutatorpath,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    z=p.stdout.read()
    z=z.decode('utf8','ignore')
    p.communicate()
    lis=z.split('\n')
    ans=[]
    lis=lis[:-1]
    for l in lis:
        x=l.split(':')
        if x[1] in ['LVR','AOR','ROR','LOR','ORU']:
            #为什么要-1：因为在coverarray中，mutant从0开始编号！
            ans.append(int(x[0])-1)
    return ans

#4: SC


#4.1获取covage矩阵，把所有测试用例执行后的txt汇总成一个矩阵。

def dealwithonetest(txtname,labelarray,workpath,testmap):
    with open(workpath+"/"+txtname, "r", encoding="utf-8") as file:
        testname=txtname.split("]_")[0]+"]"
        if testname in testmap:
            linenumber=testmap[testname]
        else:
            return 0,0
        content = file.read()
        if content[:2]=='{"':
            content=content[2:]
        if content[-1]=="}":
            content=content[:-1]
        lis=content.split(', "')
        maxline=int(lis[-1].split('":')[0])-1
        for l in lis:
            if ": 1" in l:
                labelarray[linenumber][int(l.split('":')[0])-1]=1
        return labelarray,maxline


def getCoverArray(workpath,testmap):
    coverarray = [[0] * 10000 for _ in range(len(testmap))]
    m=-1
    for filename in os.listdir(workpath):
        if filename.endswith(".txt") and "[" in filename:
            coverarray,m1=dealwithonetest(filename, coverarray, workpath, testmap)
            m=max(m1,m)
    for i in range(len(coverarray)):
        coverarray[i]=coverarray[i][:m+1]
    return coverarray



#4.SC:
def getSC(coverarray, selectedtest):
    # 先算coverarray的变异得分
    allmutantlist=[]
    for i in range(1,len(coverarray[0])):
        allmutantlist.append(i-1)
    sc = computeMS(coverarray, selectedtest, allmutantlist)
    return sc


#5: BC:
#merge ser.
#需要把serpath放到每个testlist元素前
#serpath=workpath.replace("statement","branch")
#cwdpath="/home/luzeyu/Desktop/mytso3"
def getBC(cwdpath,selectedtest,serpath):
    testlist=[]
    for s in selectedtest:
        testlist.append(serpath+"/"+list(testmap)[s]+".ser")
    GetBranchCov.mergeSER(testlist, cwdpath)
    GetBranchCov.report(cwdpath)
    xmlpath=cwdpath+"/output.xml/coverage.xml"
    return GetBranchCov.XMLparser(xmlpath)



from scipy.stats import kendalltau
from scipy.stats import pearsonr
from scipy.stats import spearmanr
def computeKendall(x,y):
    tau, p = kendalltau(x,y)
    return tau

def computePearsonr(x,y):
    tau, p = pearsonr(x,y)
    return tau

def computeSpearmanr(x,y):
    tau,p=spearmanr(x,y)
    return tau


def computePC(array,triggertestlist):
    #PC的计算需要：一个矩阵，和triggertestlist(e.g.,[3,5])
    #逐列和triggertestlist对比：
    PC=0
    for j in range(len(array[0])):
        denominator=0
        numerator=0
        for i in range(len(array)):
            if array[i][j]==1:
                denominator+=1
                if i in triggertestlist:
                    numerator+=1
        if denominator==0:
            PC=max(PC,0)
        else:
            PC=max(PC,min(1,float(numerator/denominator)))
        if PC==1:
            return 1
    return PC




def computePCbymutantlist(array,triggertestlist,mutantlist):
    #PC的计算需要：一个矩阵，和triggertestlist(e.g.,[3,5])
    #逐列和triggertestlist对比：
    PC=0
    for j in mutantlist:
        denominator=0
        numerator=0
        for i in range(len(array)):
            if array[i][j]==1:
                denominator+=1
                if i in triggertestlist:
                    numerator+=1
        if denominator==0:
            PC=max(PC,0)
        else:
            PC=max(PC,min(1,float(numerator/denominator)))
        if PC==1:
            return 1
    return PC



#main:
#获取全部工作目录
def get_all_folders(directory):
    folders = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            folders.append(item_path)
    return folders


def get_all_workpath(folders):
    ans=[]
    for f in folders:
        ans+=get_all_folders(f)
    return ans


#下面还需要一段计算PC的
cwdpath="."
outputpath="/home/luzeyu/Desktop/ZPtest/RQ4/result"
folders=get_all_folders("/home/luzeyu/Desktop/statement")
all_workpath=get_all_workpath(folders)

out = open(outputpath + '/PC.csv', 'a')
csv_write = csv.writer(out, dialect='excel')
csv_write.writerow(["","MS", "SMS", "RMS", "CMS", "COS", "SC"])


resultlist=[]
resultdic={}
for workpath in all_workpath:
  try:
    pv=workpath.split("/")[-1]
    resultdic[pv]=1
    result=[pv]
    testmap, labelarray = getLabelArray(workpath)
    coverarray=getCoverArray(workpath,testmap)
    #ratiolist=[0.1,0.2,0.3,0.4,0.5]
    #allans=[]
    #for ratio in ratiolist:
    #print(result)
    detected = []
    SMS = []
    SMSmutant = getSMSmutantlist(labelarray)
    MS = []
    allmutant = []
    for i in range(0, len(labelarray[0])):
        allmutant.append(i)
    COS = []
    COSmutant = getCOS(workpath + "/mutants.log")
    RMS = []
    RMSmutant = getRMS(labelarray)
    CMS = []
    CMSmutant = clustermutant(labelarray, SMSmutant)
    BC = []
    SC = []
    tnames = gettriggertest(workpath).split(",")
    tindexs = []
    for t in tnames:
        if t.replace("::", "[") + "]" in testmap:
            tindexs.append(testmap[t.replace("::", "[") + "]"])
            # 不需要采样了，直接拿矩阵过来计算。
    MS.append(computePCbymutantlist(labelarray, tindexs, allmutant))
    SMS.append(computePCbymutantlist(labelarray, tindexs, SMSmutant))
    RMS.append(computePCbymutantlist(labelarray, tindexs, RMSmutant))
    CMS.append(computePCbymutantlist(labelarray, tindexs, CMSmutant))
    COS.append(computePCbymutantlist(labelarray, tindexs, COSmutant))
    SC.append(computePC(coverarray, tindexs))
    print([MS[-1], SMS[-1], RMS[-1], CMS[-1], COS[-1], SC[-1]])
    result += [MS[-1], SMS[-1], RMS[-1], CMS[-1], COS[-1], SC[-1]]
    csv_write.writerow(result)
    out.close()
  except:
    continue