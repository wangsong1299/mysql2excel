from __future__ import unicode_literals

from django.db import models
from channels import Group

import re, os, datetime, json
from DataLib.DataMergeModel import DataMergeModel
from DataLib.DataBuildModel import DataBuildModel
from DataLib.DataFilterModel import DataFilterModel
from DataLib.DataStatisticModel import DataStatisticModel

# import sys 
# reload(sys) 
# sys.setdefaultencoding('utf-8') 

sql_db = {
    'tushare_db': {
        'host': '127.0.0.1',
        'user': 'root',
        'pwd': 'Gab821211',
        'db': 'tushare',
        'port': 3306
    },
    'tushare_test_db': {
        'host': '127.0.0.1',
        'user': 'root',
        'pwd': 'Gab821211',
        'db': 'tushare_test2',
        'port': 3306
    },
    'finance_db': {
        'host': '120.27.48.180',
        'user': 'root',
        'pwd': 'Vito921208',
        'db': 'finance_db',
        'port': 3306
    },
    'jobhelper_db': {
        'host': '120.27.48.180',
        'user': 'root',
        'pwd': 'Vito921208',
        'db': 'jobhelper_db',
        'port': 3306
    },
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, 'app/static/datafile/').replace('\\','/')
dataBuild = DataBuildModel(STATIC_DIR, logPath = STATIC_DIR+'debug')
dataMerge = DataMergeModel()

cache_data = {}

def splitCommand(command):
    method = re.findall(r'^\s*([^\s]+)',command)
    method = method[0]
    cmdmap = dict()
    tmp_list = re.findall(r'--([^\s]+)\s+([^\-\-]+)',command)
    for item in tmp_list:
        if item[0] == 'query':
            tmp_str = command[command.find('--query') + 8:]
            if tmp_str.find('--') > 0:
                tmp_str = tmp_str[:tmp_str.find('--')]
            cmdmap[item[0]] = tmp_str.strip()
        else:
            cmdmap[item[0]] = item[1].strip()

    return [method, cmdmap]

# Create your models here.
def parseCommand(command, group_user = 'cmd-line'):
    try:
        [method, cmdmap] = splitCommand(command)
        Group(group_user).send({'text': json.dumps([method, cmdmap]) })
        if method == 'COMMAND':
            dealCommand(cmdmap, group_user = group_user)
        elif method == 'loadmysql':
            dealMysqlload(cmdmap, group_user = group_user)
        elif method == 'loadexcel':
            dealExcelload(cmdmap, group_user = group_user)
        elif method == 'saveexcel':
            dealExcelsave(cmdmap, group_user = group_user)
        elif method == 'merge':
            dealMerge(cmdmap, group_user = group_user)
        else:
            Group(group_user).send({'text': 'Error: command not found!'})
        wanderNodes(group_user)
    except Exception, what:
        Group(group_user).send({'text': 'Error: ' + str(what)})

def dealCommand(cmdmap, group_user = 'cmd-line'):
    if cmdmap.has_key('autosave'):
        if cmdmap['autosave'] == 'true':
            cache_data[group_user]['auto-save'] = True
        else:
            cache_data[group_user]['auto-save'] = False

def dealMysqlload(cmdmap, group_user = 'cmd-line'):
    db = cmdmap['db']
    query = cmdmap['query']
    tar = cmdmap['tar']
    dataBuild.mysqlConnect(sql_db[db])
    df = dataBuild.mysqlQuery(query)
    dataBuild.mysqlDestroy()

    cache_data[group_user][tar] = df
    Group(group_user).send({'text': 'Mysql data loaded!'})

    if cache_data[group_user].has_key('auto-save'):
        if cache_data[group_user]['auto-save']:
            Group(group_user).send({'text': 'auto saving...'})
            dataBuild.excelWriterRaw(df, tar, if_exists = 'replace')
            Group(group_user).send({'text': 'Excel data saved due to autosave config!'})

def dealExcelload(cmdmap, group_user = 'cmd-line'):
    tar = cmdmap['tar']
    if cmdmap.has_key('sheet'):
        sheetName = cmdmap['sheet']
    else:
        sheetName = 'Sheet1'
    df = dataBuild.excelReader(tar, sheetName)

    cache_data[group_user][tar] = df
    Group(group_user).send({'text': 'Excel data loaded!'})

def dealExcelsave(cmdmap, group_user = 'cmd-line'):
    tar = cmdmap['tar']
    src = cmdmap['src']
    if_exists = 'replace'
    df = cache_data[group_user][src]

    Group(group_user).send({'text': 'write waiting...'})
    dataBuild.excelWriterRaw(df, tar, if_exists = if_exists)

    Group(group_user).send({'text': 'Excel data saved!'})
    Group(group_user).send({'text': 'Excel path is /static/datafile/' + tar + '.xlsx'})

def dealMerge(cmdmap, group_user = 'cmd-line'):
    tar = cmdmap['tar']
    srclist = cmdmap['src'].strip()
    srclist = re.split(r'\s+', srclist)
    joinlist = cmdmap['join'].strip()
    joinlist = re.split(r'\s+', joinlist)

    how = joinlist[0]
    del joinlist[0]
    relation = joinlist

    Group(group_user).send({'text': 'start merging...'})
    df = cache_data[group_user][srclist[0]]
    for i in range(1, len(srclist)):
        dfTmp = cache_data[group_user][srclist[i]]
        df = dataMerge.runMerge(df, dfTmp, {
                'how': how,
                'relation': relation
            })
    cache_data[group_user][tar] = df
    Group(group_user).send({'text': 'merge succeed!'})

    if cache_data[group_user].has_key('auto-save'):
        if cache_data[group_user]['auto-save']:
            Group(group_user).send({'text': 'auto saving...'})
            dataBuild.excelWriterRaw(df, tar, if_exists = 'replace')
            Group(group_user).send({'text': 'Excel data saved due to autosave config!'})


# wander cache nodes
def wanderNodes(group_user = 'cmd-line'):
    if cache_data.has_key(group_user):
        cache = cache_data[group_user]
        node_list = []
        for key in cache:
            if key == 'auto-save':
                continue
            node_list.append(key)
        Group(group_user).send({'text': 'cached nodes: ' + ' , '.join(node_list)})