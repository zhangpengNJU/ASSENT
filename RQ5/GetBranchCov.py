#语句覆盖率走覆盖矩阵获取，分支覆盖率由若干ser文件合并得到
#输入:ser文件，带合并测试用例名称列表。返回：BC
import subprocess


#合并若干ser，得到一个新的ser
#cobertura-merge test1path test2path test3path
#testlist[0]: /././classpath[testname].ser
def mergeSER(testlist,cwdpath):
    s=''
    for t in testlist:
        s+=t+" "
    p = subprocess.Popen(
        'cobertura-merge ' + s , shell=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,cwd=cwdpath)
    #z=p.stdout.read()
    #z=z.decode('utf8','ignore')
    p.communicate()




#ser->report
#cobertura-report --format xml --destination output.xml
def report(workpath):
    p = subprocess.Popen(
        'cobertura-report --format xml --destination output.xml', shell=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,cwd=workpath)
    #z=p.stdout.read()
    #z=z.decode('utf8','ignore')
    p.communicate()


import xml.etree.ElementTree as ET


# 解析合并后的XML：
def XMLparser(xmlpath):
    tree = ET.parse(xmlpath)
    root = tree.getroot()
    return float(root.get("branch-rate"))


# open(xmlpath,"r")
#xmlpath = "/home/luzeyu/Desktop/mytso3/output.xml/coverage.xml"
#r = XMLparser(xmlpath)

