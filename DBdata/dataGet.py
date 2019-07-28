import json
import pandas as pd
from pymongo import MongoClient, ASCENDING
import datetime as dt
from .constant import *


# 加载配置
config = open('/home/yao/test/stocker/DBdata/config.json', 'r')
setting = json.load(config)

MONGO_HOST = setting['MONGO_HOST']
MONGO_PORT = setting['MONGO_PORT']
SYMBOLS = setting['SYMBOLS']
START = setting["START"]
END = setting["END"]
FREQS = setting["FREQ"]

mc = MongoClient(MONGO_HOST, MONGO_PORT)        # Mongo连接


DB_NAME_DICT = {
'1MIN': MINUTE_DB_NAME,
'5MIN':MINUTE_5_DB_NAME,
'15MIN':MINUTE_15_DB_NAME,
'30MIN':MINUTE_30_DB_NAME,
'60MIN':MINUTE_60_DB_NAME,
'D':DAILY_DB_NAME,
'W':WEEKLY_DB_NAME
}

NODE_DB_NAME_DICT = {
'1MIN': '',
'5MIN':CHT_NODE_5_DB_NAME,
'15MIN':'',
'30MIN':CHT_NODE_30_DB_NAME,
'60MIN':'',
'D':CHT_NODE_D_DB_NAME,
'W':''
}

CB_DB_NAME_DICT = {
'1MIN': '',
'5MIN':CHT_CB_5_DB_NAME,
'15MIN':'',
'30MIN':CHT_CB_30_DB_NAME,
'60MIN':'',
'D':CHT_CB_D_DB_NAME,
'W':''
}

def loadDataKLine(symbol, start_time, end_time, freq):
    db_freq = freq
    if (freq[0] in ['0', '1', '2','3','4','5','6','7','8','9']) and (freq[-1] not in ['N']):
        db_freq = freq + 'MIN'

    if(freq.startswith('d')):
        db_freq = 'D'

    if (freq.startswith('w')):
        db_freq = 'W'
    db = mc[DB_NAME_DICT[db_freq]]

    start = dt.datetime.strptime(start_time, "%Y-%m-%d")
    end = dt.datetime.strptime(end_time, "%Y-%m-%d")

    flt = {'datetime': {'$gte': start,
                        '$lte':end}}

    data = pd.DataFrame(list(db[symbol].find(flt)))


    db = mc[NODE_DB_NAME_DICT[db_freq]]
    flt = {'btype': {'$eq': 0},
           'datetime': {'$gte': start,
                        '$lte': end}
           }
    node_list = list(db[symbol].find(flt))

    db = mc[CB_DB_NAME_DICT[db_freq]]
    flt = {}
    centralbase_list = list(db[symbol].find(flt))

    db = mc[NODE_DB_NAME_DICT[db_freq]]
    flt = {'btype': {'$ne': 0},
           'classfier': {'$eq': 1},
           'datetime': {'$gte': start,
                        '$lte': end}
           }
    beichi_list = list(db[symbol].find(flt))

    db = mc[NODE_DB_NAME_DICT[db_freq]]
    flt = {'btype': {'$ne': 0},
           'classfier': {'$eq': 2},
           'datetime': {'$gte': start,
                        '$lte': end}
           }
    share_beichi_list = list(db[symbol].find(flt))

    db = mc[NODE_DB_NAME_DICT[db_freq]]
    flt = {'btype': {'$ne': 0},
           'classfier': {'$eq': 3},
           'datetime': {'$gte': start,
                        '$lte': end}
           }
    panzh_beichi_list = list(db[symbol].find(flt))

    db = mc[NODE_DB_NAME_DICT[db_freq]]
    flt = {'btype': {'$ne': 0},
           'classfier': {'$eq': 4},
           'datetime': {'$gte': start,
                        '$lte': end}
           }
    share_panzh_beichi_list = list(db[symbol].find(flt))

    # 对日线数据进行处理
    if db_freq == "D":
        data['datetime'] = data['datetime'] + dt.timedelta(hours=23, minutes=59, seconds=59)
    data.set_index(data['datetime'], inplace=True)
    data.drop(['_id'], axis=1, inplace=True)


    data['node'] = None
    data['base_up'] = None
    data['base_down'] = None
    data['beichi'] = None
    data['sharebeichi'] = None
    data['panzhbeichi'] = None
    data['sharepanzhbeichi'] = None
    data['sec_buy'] = None

    if node_list != None:
        for node in node_list:
            time_seg = data.ix[data.index >= node['datetime'], 'close']
            if not time_seg.empty:
                time = time_seg.index[0]
                data.set_value(time, 'node', node['value'])

    if centralbase_list != None:
        for base in centralbase_list:
            data.ix[base['start']:base['end'], 'base_up'] = base['up']
            data.ix[base['start']:base['end'], 'base_down'] = base['down']
            data.ix[base['start']:base['end'], 'base_type'] = base['ctype']

    if beichi_list != None:
        for beichi in beichi_list:
            time_seg = data.ix[data.index >= beichi['datetime'], 'close']
            if not time_seg.empty:
                time = time_seg.index[0]
                data.set_value(time, 'beichi', beichi['value'])

    if share_beichi_list != None:
        for sharebeichi in share_beichi_list:
            time_seg = data.ix[data.index >= sharebeichi['datetime'], 'close']
            if not time_seg.empty:
                time = time_seg.index[0]
                data.set_value(time, 'sharebeichi', sharebeichi['value'])

    if panzh_beichi_list:
        for panzhbeichi in panzh_beichi_list:
            time_seg = data.ix[data.index >= panzhbeichi['datetime'], 'close']
            if not time_seg.empty:
                time = time_seg.index[0]
                data.set_value(time, 'panzhbeichi', panzhbeichi['value'])

    if share_panzh_beichi_list:
        for sharepanzhbeichi in share_panzh_beichi_list:
            time_seg = data.ix[data.index >= sharepanzhbeichi['datetime'], 'close']
            if not time_seg.empty:
                time = time_seg.index[0]
                data.set_value(time, 'sharepanzhbeichi', sharepanzhbeichi['value'])
    '''         
    for sec_buy in self.sec_buy_point_list:
        time_seg = self.data.ix[self.data.index>=sec_buy.time, 'close']
        time = time_seg.index[0]
        if time!=None:
            self.data.set_value(time, 'sec_buy', self.data.ix[time, 'close'])  
     '''
    if data.empty:
        return data
    data['datetime'] = data['datetime'].apply(lambda x: dt.datetime.strftime(x, '%Y-%m-%d  %H:%M:%S'))
    data.set_index(data['datetime'], inplace=True)
    return data

