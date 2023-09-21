import re
import io
import subprocess
import csv
import numpy as np
import os
from RQ1 import *
np.random.seed(0)


#1:pv示例：-p Lang -v 1f
#defects4j checkout -p Lang -v 1f -w /tmp/0815
def getfixversion(pv,workpath="/tmp/0815"):
    p=subprocess.Popen('defects4j checkout '+pv+' -w '+workpath,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    p.communicate()


#2：生成测试用例
def generatetestcases(pv):
    p=subprocess.Popen('gen_tests.pl -g evosuite '+pv+' -n 1 -o /tmp/0815 -b 300',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    p.communicate()


#3：执行测试用例，返回执行结果行：failedtest：['org.jfree.chart.renderer.category.AbstractCategoryItemRenderer_ESTest::test72', 'org.jfree.chart.renderer.category.AbstractCategoryItemRenderer_ESTest::test06']

def rungeneratedtestcases(workpath,pv):
    p=subprocess.Popen('defects4j test -w '+workpath+' -s /tmp/0815/'+pv.split(" ")[1]+'/evosuite/1/'+pv.split(" ")[1]+'-'+pv.split(" ")[-1]+'-evosuite.1.tar.bz2',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    z = p.stdout.read()
    z = str(z)
    if "Failing tests: 0" in z:
        #如果在buggy版本上全部测试用例都通过了，就跳过它
        p.communicate()
        return [""]
    if "Failing tests: " in z:
        #有fail掉的
        p.communicate()
        lis=z[:-3].split("\\n  - ")[1:]
        return lis
    p.communicate()
    return [""]


#执行修改（注释掉triggering）后的新测试用例集合
def runchangedgeneratedtestcases(workpath,pv):
    p=subprocess.Popen('defects4j test -w '+workpath+' -s /tmp/0815/'+pv.split(" ")[1]+'/evosuite/1/'+pv.split(" ")[1]+'-'+pv.split(" ")[-1]+'-evosuite.12.tar.bz2',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    z = p.stdout.read()
    z = str(z)
    if "Failing tests: 0" in z:
        #如果在buggy版本上全部测试用例都通过了，就跳过它
        p.communicate()
        return [""]
    if "Failing tests: " in z:
        #有fail掉的
        p.communicate()
        lis=z[:-3].split("\\n  - ")[1:]
        return lis
    p.communicate()
    return [""]


#def runcoveragegeneratedtestcases(workpath,pv):
#    p=subprocess.Popen('defects4j coverage -w '+workpath+' -s /tmp/0815/'+pv.split(" ")[1]+'/evosuite/1/'+pv.split(" ")[1]+'-'+pv.split(" ")[-1]+'-evosuite.1.tar.bz2',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
#    p.communicate()


#3.1语句覆盖：
def getc(workpath,bz2path):
    #p=subprocess.Popen('defects4j coverage',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd='/tmp/0926')
    p = subprocess.Popen(
        'defects4j coverage -w ' + workpath + ' -s '+bz2path, shell=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
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


#4：解压
def unziptest(pv,outputpath):
    #tar jxvf XXX.tar.bz2
    p = subprocess.Popen(
        'tar jxvf /tmp/0815/' + pv.split(" ")[1] + '/evosuite/1/' + pv.split(" ")[
            1] + '-' + pv.split(" ")[-1] + '-evosuite.1.tar.bz2 -C '+outputpath, shell=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    p.communicate()

#5:修改：


def deletemethod(txt,name):
    #从方法名前面的一个大括号开始删除
    listofstr=txt.split(' '+name+'(')
    #如果这个类只有一个测试方法，就要把这个类直接删除掉
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




#注释掉全部triggertest，atpath='/tmp/0926'
def clearalltt(triggertest,atpath):
    #lis=triggertest.split(',')
    lis = triggertest
    for l in lis:
        cleartt(l,atpath)


#:注释掉单个triggertest：离方法名称最近的@T改为//T
def cleartt(triggertes,atpath):
    lis=triggertes.split('::')
    ttpath=atpath+'/src/test/java/'+lis[0].replace('.','/')+'.java'
    if os.path.exists(ttpath) == False:
        ttpath = atpath + '/' + lis[0].replace('.', '/') + '.java'
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


def move(path,aimpath,atpath):
    p=subprocess.Popen('mv -f '+path+' '+aimpath,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=atpath)
    p.communicate()



#6：再压缩:tar -cvjpf xxx.tar.bz2 /aa/bb/文件夹名
def ziptest(path,outputpath,workpath):
    p = subprocess.Popen(
        'tar -cvjpf ' +path+" "+outputpath, shell=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,cwd=workpath)
    p.communicate()



#3.2原始变异的分：
def getms(workpath, bz2path):
    p=subprocess.Popen('defects4j mutation -s ' + bz2path,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=workpath)
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






def removetestclass(toremove):
    l=toremove
    atpath='/tmp/0816/'
    ttpath=atpath+'/src/test/java/'+l.replace('.','/')+'.java'
    if os.path.exists(ttpath) == False:
        ttpath = atpath + '/' + l.replace('.', '/') + '.java'
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







#main
#项目名，起始bug编号，终止bug编号，不能用的bug们
project=[['Chart',1,26,[1,2]],['Cli',1,40,[6]],['Closure',1,176,[63,93]],['Codec',1,18,[1,2,3,4,5,6]],['Collections',25,28,[]],['Compress',1,47,[]],['Csv',1,16,[]],['Gson',1,18,[]],['JacksonCore',1,26,[]],['JacksonDatabind',1,112,[]],['JacksonXml',1,6,[]],['Jsoup',1,93,[]],['JxPath',1,22,[]],['Lang',1,65,[2]],['Math',1,106,[]],['Mockito',1,38,[]],['Time',1,27,[21]],]
#project=[['Chart',1,26,[1,2]],['Cli',16,40,[6]],['Closure',126,150,[63,93]],['Codec',1,18,[1,2,3,4,5,6]],['Collections',25,28,[]],['Compress',1,47,[]],['Csv',1,16,[]],['Gson',1,18,[]],['JacksonCore',19,26,[]],['JacksonDatabind',61,112,[]],['JacksonXml',1,6,[]],['Jsoup',1,93,[]],['JxPath',1,22,[]],['Lang',34,65,[2]],['Math',38,69,[]],['Mockito',24,38,[]],['Time',13,27,[21]],]

outputpath='/home/fl/Desktop/testeffectiveness/result'
for i in range(0,17):
    for j in range(project[i][1],project[i][2]+1):
        print(j)
        if j not in project[i][3]:
            #pv示例：-p Lang -v 1f
            pv='-p '+project[i][0]+' -v '+str(j)+'f'
            pv2='-p '+project[i][0]+' -v '+str(j)+'b'
            getfixversion(pv)
            wp="/tmp/0816"
            getfixversion(pv2,wp)
            generatetestcases(pv)
            triggertest=rungeneratedtestcases(wp,pv)
            #如果是“”，跳过
            if triggertest==[""]:
                continue
            #todo:解压出来
            unziptest(pv, wp)
            #一个个run
            fixpath = "/tmp/0815"
            bz2path='/tmp/0815/'+pv.split(" ")[1]+'/evosuite/1/'+pv.split(" ")[1]+'-'+pv.split(" ")[-1]+'-evosuite.1.tar.bz2'
            c=getc(fixpath,bz2path)




            sc=c[0]
            bc=c[1]
            m=getms(fixpath,bz2path)
            numofmutant=m[0]
            ms=m[1]
            if ms==0:
                continue
            #注释掉tt，再计算其他三个metrics

            atpath = '/tmp/0815'
            matrix = getmatrix(atpath, numofmutant)
            SMSresult = getSMS(matrix, ",".join(triggertest))
            osms = SMSresult[0]
            nsms = SMSresult[1]
            if osms > nsms:
                opSMS = 1
            else:
                opSMS = 0
            mutantlist = SMSresult[2]
            ms = SMSresult[3]
            # CMS要重复20次
            opCMS = []
            for k in range(0, 20):
                CMSresult = getCMS(matrix, ",".join(triggertest), mutantlist)
                ocms = CMSresult[0]
                ncms = CMSresult[1]
                if ocms > ncms:
                    opCMS.append(1)
                else:
                    opCMS.append(0)
            # RMS要重复20次
            opRMS = []
            for k in range(0, 20):
                RMSresult = getRMS(matrix, ",".join(triggertest))
                orms = RMSresult[0]
                nrms = RMSresult[1]
                if orms > nrms:
                    opRMS.append(1)
                else:
                    opRMS.append(0)
            mutatorpath = '/tmp/0815/mutants.log'
            COSresult = getCOS(matrix, ",".join(triggertest), mutatorpath)
            ocos = COSresult[0]
            ncos = COSresult[1]
            if ocos > ncos:
                opCOS = 1
            else:
                opCOS = 0
            # 注释掉tt，再计算其他三个metrics
            clearalltt(triggertest, wp)
            nbz2path='/tmp/0815/'+pv.split(" ")[1]+'/evosuite/1/'+pv.split(" ")[1]+'-'+pv.split(" ")[-1]+'-evosuite.12.tar.bz2'
            ziptest(nbz2path, "./"+triggertest[0].split('.')[0],wp)
            c=getc(fixpath,nbz2path)
            nsc = c[0]
            nbc = c[1]
            # 修改，ms还是通过矩阵获取。
            # m=getms()
            # numofmutant=m[0]
            nms = SMSresult[4]
            if float(sc) > float(nsc):
                print(sc, nsc)
                opSC = 1
            else:
                opSC = 0
            if float(bc) > float(nbc):
                opBC = 1
            else:
                opBC = 0
            if float(ms) > float(nms):
                opMS = 1
            else:
                opMS = 0
            ans = [j, opSC, opBC, opMS, opSMS, sum(opCMS) / 20.0, sum(opRMS) / 20.0, opCOS]
            print(ans)
            out = open(outputpath + '/' + str(i) + 'j.csv', 'a')
            csv_write = csv.writer(out, dialect='excel')
            csv_write.writerow(ans)
            out.close()
            # 一个版本做完之后要clean,移动回原test(多此一举！一次执行完就覆盖了呀）
            # getback(triggertest,atpath)
            # 压缩包复制到结果文件中
            move('/tmp/0815/' + pv.split(" ")[1] + '/evosuite/1/' + pv.split(" ")[1] + '-' + pv.split(" ")[
                -1] + '-evosuite.1.tar.bz2', outputpath, atpath)
            cleancsv()
            clean0924()
