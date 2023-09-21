#这是一个总的流程框架：
#把最大的项目先搞起来
#有的项目变异测试会fail掉。我们去除他。
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
#1:pv示例：-p Lang -v 1f
def getfixversion(pv):
    p=subprocess.Popen('defects4j checkout '+pv+' -w /tmp/0926',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    p.communicate()



#2:获得trigg test：
#有多个就一一注释掉
def gettriggertest():
    p=subprocess.Popen('cat defects4j.build.properties',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd='/tmp/0926')
    z=p.stdout.read()
    z=str(z)
    p.communicate()
    lis=z.split('d4j.tests.trigger=')
    triggertest=lis[-1][:-3]
    c=triggertest.count("::")
    if c>1:
        print('more than one triggertests')
    return triggertest





def deletemethod(txt,name):
    #从方法名前面的一个大括号开始删除
    listofstr=txt.split(' '+name+'(')
    #如果这个类只有一个测试方法，就要把这个类直接删除掉
    #我真你妈服了，把方法名写在开头注释里真的牛批。
    while len(listofstr)>2:
        newlisofstr=[]
        stri=listofstr[0]
        for i in range(0,len(listofstr)-1):
            stri=stri+' '+name+'('+listofstr[i]
        newlisofstr=[stri,listofstr[-1]]
        listofstr=newlisofstr
    for i in range(0,len(listofstr[0])):
        if listofstr[0][-i-1]=='}':
            listofstr[0]=listofstr[0][:-i]
            break
    count=0
    start=1
    if len(listofstr)==1:
        return listofstr[0]
    for i in range(0,len(listofstr[1])):
        if listofstr[1][i]=='{':
            count=count+1
            start=0
        if listofstr[1][i]=='}':
            count=count-1
        if start==0 and count==0:
            break
    listofstr[1]=listofstr[1][i+1:]
    return listofstr[0]+listofstr[1]
    #return tore




#注释掉全部triggertest
def clearalltt(triggertest,atpath):
    lis=triggertest.split(',')
    for l in lis:
        cleartt(l,atpath)



def copy(path,aimpath,atpath):
    p=subprocess.Popen('\cp -rf '+path+' '+aimpath,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=atpath)
    p.communicate()






#3.0:注释掉单个triggertest：离方法名称最近的@T改为//T
def cleartt(triggertes,atpath):
    lis=triggertes.split('::')
    ttpath=atpath+'/src/test/java/'+lis[0].replace('.','/')+'.java'
    if os.path.exists(ttpath)==False:
        ttpath=atpath+'/tests/'+lis[0].replace('.','/')+'.java'
    if os.path.exists(ttpath)==False:
        ttpath=atpath+'/src/test/'+lis[0].replace('.','/')+'.java'
    if os.path.exists(ttpath)==False:
        ttpath=atpath+'/gson/src/test/java/'+lis[0].replace('.','/')+'.java'
    if os.path.exists(ttpath)==False:
        ttpath=atpath+'/test/'+lis[0].replace('.','/')+'.java'
    #copy(ttpath,'/tmp/'+lis[0].replace('.','/')+'.java',atpath)
    f=open(ttpath,"rb")
    txt=f.read()
    txt=txt.decode('utf8','ignore')
    #如果.java中不写@test，就需要找到该方法，按括号匹配删除掉。
    lis2=txt.split("@Test")
    if len(lis2)==1:
        newtxt=deletemethod(txt,lis[1])
    else:
        newtxt=lis2[0]
        for i in range(1,len(lis2)):
            if lis[1]+'(' in lis2[i]:
                newtxt=newtxt+"//Test"+lis2[i]
            else:
                newtxt=newtxt+"@Test"+lis2[i]
    f.close()
    f=open(ttpath,'w')
    f.write(newtxt)
    f.close()


def getback(triggertest,atpath):
    lis=triggertest.split('::')
    ttpath=atpath+'/src/test/java/'+lis[0].replace('.','/')+'.java'
    if os.path.exists(ttpath)==False:
        ttpath=atpath+'/tests/'+lis[0].replace('.','/')+'.java'
    move('/tmp/'+lis[0].replace('.','/')+'.java',ttpath,atpath)




#3.1语句覆盖：
def getc():
    p=subprocess.Popen('defects4j coverage',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd='/tmp/0926')
    z=p.stdout.read()
    z=z.decode('utf8','ignore')
    p.communicate()
    lis=z.split('\n')
    sc=0
    bc=0
    for l in lis:
        #最后的【：-1】是为了去除%
        if 'Line coverage: ' in l:
            sc=l.split('Line coverage: ')[-1][:-1]
        if 'Condition coverage: ' in l:
            bc=l.split('Condition coverage: ')[-1][:-1]
    return [sc,bc]



def removetestclass(toremove):
    l=toremove
    atpath='/tmp/0926/'
    ttpath=atpath+'/src/test/java/'+l.replace('.','/')+'.java'
    if os.path.exists(ttpath)==False:
        ttpath=atpath+'/tests/'+l.replace('.','/')+'.java'
    if os.path.exists(ttpath)==False:
        ttpath=atpath+'/src/test/'+l.replace('.','/')+'.java'
    if os.path.exists(ttpath)==False:
        ttpath=atpath+'/gson/src/test/java/'+l.replace('.','/')+'.java'
    if os.path.exists(ttpath)==False:
        ttpath=atpath+'/test/'+l.replace('.','/')+'.java'
    p=subprocess.Popen('rm -rf '+ttpath,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    p.communicate()




#3.2原始变异的分：
def getms():
    p=subprocess.Popen('defects4j mutation',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd='/tmp/0926')
    z=p.stdout.read()
    z=z.decode('utf8','ignore')
    p.communicate()
    #如果出现No tests found in,就先把该测试用例所在类删除掉，再调用getms
    if "No tests found in " in z:
        l=z.split("No tests found in ")
        toremove=l[1].split('"')[0]
        removetestclass(toremove)
        return getms()
    lis=z.split('\n')
    ms=0
    numofmutant=0
    for l in lis:
        #最后的【：-1】是为了去除%
        if 'Mutants generated: ' in l:
            numofmutant=l.split('Mutants generated: ')[-1]
        if 'Mutants killed: ' in l:
            killed=l.split('Mutants killed: ')[-1]
            ms=float(killed)/float(numofmutant)
    return [numofmutant,ms]







#3.3.0搜集覆盖矩阵



def test(testname,tpath):
    #timeout=80
    p=subprocess.Popen('defects4j mutation -t '+testname,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=tpath)
    #这个问题我们说了无数遍了，要避免管道堵塞，就不能输出（虽然输出也会使得它挂起）用commun
    #z=p.stdout.read()
    p.communicate()
    #return z


def move(path,aimpath,atpath):
    p=subprocess.Popen('mv -f '+path+' '+aimpath,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=atpath)
    p.communicate()



def cleancsv():
    p=subprocess.Popen('rm -rf /tmp/csv',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    p.communicate()
    p=subprocess.Popen('mkdir /tmp/csv',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    p.communicate()

def clean0924():
    p=subprocess.Popen('rm -rf /tmp/0926',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    p.communicate()

#第一行：变异体编号，第一列：测试用例名称
def mergecsv(csvpath,numofmutants):
    matrix=[]
    m=[]
    for i in range(0,int(numofmutants)+1):
        m.append(i)
    matrix.append(m)
    lis=os.listdir(csvpath)
    for c in lis:
        m=[c[:-4]]
        for i in range(1,int(numofmutants)+1):
            m.append(0)
        csvreader=csv.reader(open(csvpath+'/'+c))
        #print(c)
        for row in csvreader:
            if '[' not in row[1]:
                if row[1]!='LIVE':
                    m[int(row[0])]=1
        matrix.append(m)
    return matrix







#汇总如以前一样：行代表一个测试用例


def getmatrix(atpath,numofmutant):
    p=subprocess.Popen('mkdir /tmp/csv',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=atpath)
    p.communicate()
    #这里可以搞细一点，把不是testmap里提到的test类过滤掉
    #第一步，提取testmap，记录所有类生成列表tcl 跳过这一步骤
    #fm=open(atpath+'/testMap.csv',"r")
    #testclasslis=fm.read().split('\n')
    #tcl=[]
    #for i in range(1,len(testclasslis)):
    #    if ',' in testclasslis[i]:
    #        tcl.append(testclasslis[i].split(',')[1])
    f=open(atpath+'/all_tests',"r")
    txt=f.read()
    alltest=txt.split('\n')[:-1]
    tests=[]
    for at in alltest:
        x=at.split('(')
        #第二步，检查x【1】【：-1】是否在tcl
        #if x[1][:-1] in tcl:
        t=x[1][:-1]+'::'+x[0]
        tests.append(t)
    for t in range(0,len(tests)):
        test(tests[t],atpath)
        print(str(t)+'/'+str(len(tests))+'success!')
        move(atpath+'/kill.csv','/tmp/csv/'+tests[t]+'.csv',atpath)
    return mergecsv('/tmp/csv',numofmutant)



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
                print(ans[an]-z[zi])
                print(an)
                print(zi)
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
                        print(len(index))
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


#对于sms而言，不必注释掉trigger test，只需要在矩阵中，删除掉那一行：.不，是多行
#增加输出，总变异得分
def getSMS(matrix,triggertest):
    triggerlis=triggertest.split(',')
    coverarray=[]
    ntcoverarray=[]
    testlist=[]
    allmutantlist=[]
    for i in range(1,len(matrix[0])):
        allmutantlist.append(i-1)
    for i in range(1,len(matrix)):
        c=[]
        ntc=[]
        testlist.append(i-1)
        for j in range(1,len(matrix[0])):
            c.append(matrix[i][j])
            if matrix[i][0] not in triggerlis:
                ntc.append(matrix[i][j])
        coverarray.append(c)
        if ntc!=[]:
            ntcoverarray.append(ntc)
    #先算coverarray的变异得分
    xn=getDMSG(coverarray)
    xn=filterxn(xn)
    mutantlist=xn[1]
    oms=computeMS(coverarray,testlist,mutantlist)
    ms1=computeMS(coverarray,testlist,allmutantlist)
    #再算ntc:
    nms=computeMS(ntcoverarray,testlist[:-len(triggerlis)],mutantlist)
    ms2=computeMS(ntcoverarray,testlist[:-len(triggerlis)],allmutantlist)
    return [oms,nms,mutantlist,ms1,ms2]







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




def getCMS(matrix,triggertest,mutantlist):
    triggerlis=triggertest.split(',')
    coverarray=[]
    ntcoverarray=[]
    testlist=[]
    for i in range(1,len(matrix)):
        c=[]
        ntc=[]
        testlist.append(i-1)
        for j in range(1,len(matrix[0])):
            c.append(matrix[i][j])
            if matrix[i][0] not in triggerlis:
                ntc.append(matrix[i][j])
        coverarray.append(c)
        if ntc!=[]:
            ntcoverarray.append(ntc)
    cmsmutantlist=clustermutant(coverarray,mutantlist)
    oms=computeMS(coverarray,testlist,cmsmutantlist)
    #再算ntc
    nms=computeMS(ntcoverarray,testlist[:-len(triggerlis)],cmsmutantlist)
    print(str(oms)+str(nms)+' CMSresults')
    return [oms,nms]


#3.4RMS 选30%
def RMS(labelarray):
    allmutantlist=[]
    randmutantlist=[]
    for i in range(0,len(labelarray[0])):
        allmutantlist.append(i)
    while int(len(allmutantlist)*0.3)!=len(randmutantlist):
        num=random.randint(0,len(allmutantlist)-1)
        if allmutantlist[num] not in randmutantlist:
            randmutantlist.append(allmutantlist[num])
    return randmutantlist


def getRMS(matrix,triggertest):
    triggerlis=triggertest.split(',')
    coverarray=[]
    ntcoverarray=[]
    testlist=[]
    for i in range(1,len(matrix)):
        c=[]
        ntc=[]
        testlist.append(i-1)
        for j in range(1,len(matrix[0])):
            c.append(matrix[i][j])
            if matrix[i][0] not in triggerlis:
                ntc.append(matrix[i][j])
        coverarray.append(c)
        if ntc!=[]:
            ntcoverarray.append(ntc)
    #先算coverarray的变异得分
    mutantlist=RMS(coverarray)
    oms=computeMS(coverarray,testlist,mutantlist)
    #再算ntc
    nms=computeMS(ntcoverarray,testlist[:-len(triggerlis)],mutantlist)
    return [oms,nms]


#3.5COS 麻烦一点，要先把变异体和变异算子映射起来。ROR,AOR,UOI,ABS,LCR
#AOR,ROR,LOR,ORU这四个，其他四个删除。LVR还是算进去，囊括了ABS。
#mutatorpath='/tmp/lang_1_f2/mutants.log'
def COS(mutatorpath):
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


def getCOS(matrix,triggertest,mutatorpath):
    triggerlis=triggertest.split(',')
    coverarray=[]
    ntcoverarray=[]
    testlist=[]
    for i in range(1,len(matrix)):
        c=[]
        ntc=[]
        testlist.append(i-1)
        for j in range(1,len(matrix[0])):
            c.append(matrix[i][j])
            if matrix[i][0] not in triggerlis:
                ntc.append(matrix[i][j])
        coverarray.append(c)
        if ntc!=[]:
            ntcoverarray.append(ntc)
    #先算coverarray的变异得分
    mutantlist=COS(mutatorpath)
    oms=computeMS(coverarray,testlist,mutantlist)
    #再算ntc
    nms=computeMS(ntcoverarray,testlist[:-len(triggerlis)],mutantlist)
    return [oms,nms]





#4.main
#项目名，起始bug编号，终止bug编号，不能用的bug们
#project=[['Chart',1,26,[1,2]],['Cli',1,40,[6]],['Closure',1,176,[63,93]],['Codec',1,18,[1,2,3,4,5,6]],['Collections',25,28,[]],['Compress',1,47,[]],['Csv',1,16,[]],['Gson',1,18,[]],['JacksonCore',1,26,[]],['JacksonDatabind',1,112,[]],['JacksonXml',1,6,[]],['Jsoup',1,93,[]],['JxPath',1,22,[]],['Lang',1,65,[2]],['Math',1,106,[]],['Mockito',1,38,[]],['Time',1,27,[21]],]
project=[['Chart',1,26,[1,2]],['Cli',16,40,[6]],['Closure',126,150,[63,93]],['Codec',1,18,[1,2,3,4,5,6]],['Collections',25,28,[]],['Compress',1,47,[]],['Csv',1,16,[]],['Gson',1,18,[]],['JacksonCore',19,26,[]],['JacksonDatabind',61,112,[]],['JacksonXml',1,6,[]],['Jsoup',1,93,[]],['JxPath',1,22,[]],['Lang',34,65,[2]],['Math',38,69,[]],['Mockito',24,38,[]],['Time',13,27,[21]],]

outputpath='/home/fl/Desktop/testeffectiveness/result'
def main():
  for i in range(2,3):
    out =open(outputpath+'/'+str(i)+'.csv','a')
    csv_write=csv.writer(out,dialect='excel')
    csv_write.writerow(['SC','BC','MS','SMS','CMS','RMS','COS'])
    out.close()
    for j in range(project[i][1],project[i][2]+1):
        print(j)
        if j not in project[i][3]:
            #pv示例：-p Lang -v 1f
            pv='-p '+project[i][0]+' -v '+str(j)+'f'
            getfixversion(pv)
            triggertest=gettriggertest()
            c=getc()
            sc=c[0]
            bc=c[1]
            m=getms()
            numofmutant=m[0]
            ms=m[1]
            if ms==0:
                continue
            atpath='/tmp/0926'
            matrix=getmatrix(atpath,numofmutant)
            SMSresult=getSMS(matrix,triggertest)
            osms=SMSresult[0]
            nsms=SMSresult[1]
            if osms>nsms:
                opSMS=1
            else:
                opSMS=0
            mutantlist=SMSresult[2]
            ms=SMSresult[3]
            #CMS要重复20次
            opCMS=[]
            for k in range(0,20):
                CMSresult=getCMS(matrix,triggertest,mutantlist)
                ocms=CMSresult[0]
                ncms=CMSresult[1]
                if ocms>ncms:
                    opCMS.append(1)
                else:
                    opCMS.append(0)
            #RMS要重复20次
            opRMS=[]
            for k in range(0,20):
                RMSresult=getRMS(matrix,triggertest)
                orms=RMSresult[0]
                nrms=RMSresult[1]
                if orms>nrms:
                    opRMS.append(1)
                else:
                    opRMS.append(0)
            mutatorpath='/tmp/0926/mutants.log'
            COSresult=getCOS(matrix,triggertest,mutatorpath)
            ocos=COSresult[0]
            ncos=COSresult[1]
            if ocos>ncos:
                opCOS=1
            else:
                opCOS=0
            #注释掉tt，再计算其他三个metrics
            clearalltt(triggertest,atpath)
            c=getc()
            nsc=c[0]
            nbc=c[1]
            #修改，ms还是通过矩阵获取。
            #m=getms()
            #numofmutant=m[0]
            nms=SMSresult[4]
            if float(sc)>float(nsc):
                print(sc,nsc)
                opSC=1
            else:
                opSC=0
            if float(bc)>float(nbc):
                opBC=1
            else:
                opBC=0
            if float(ms)>float(nms):
                opMS=1
            else:
                opMS=0
            ans=[j,opSC,opBC,opMS,opSMS,sum(opCMS)/20.0,sum(opRMS)/20.0,opCOS]
            print(ans)
            out =open(outputpath+'/'+str(i)+'j.csv','a')
            csv_write=csv.writer(out,dialect='excel')
            csv_write.writerow(ans)
            out.close()
            #一个版本做完之后要clean,移动回原test(多此一举！一次执行完就覆盖了呀）
            #getback(triggertest,atpath)
            cleancsv()
            clean0924()




main()

#Collections的问题是变异测试无法执行
#codec,gson的问题是testpath搞错了
#CSV也是如同collection一样，有某缺陷上无法变异测试
#那么总结一下0927做的改动：跳过变异测试不通过的bug。新增了两个testpath
#5:lang 34-65; closure:84-114
#4:lang:1-33; closure:115-145
