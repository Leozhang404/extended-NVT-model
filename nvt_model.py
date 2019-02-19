# -*- coding: utf-8 -*-
"""
Created on Tue Jan  8 19:21:30 2019

@author: Administrator
"""

from price_history import get_market_history_price
#import pandas as pd
import matplotlib.pyplot as plt
import math
import numpy as np
import json


# Moving Average
def MA_Avg(data, n):
    """ 
    对数据data进行n天的移动平均
    """
    i = 0
    N = len(data)
    ma_data = []
    while i < N:
        if i < n:
            t = np.mean(data[0:i+1])
        else:
            t= np.mean(data[i-n:i+1])
        ma_data.append(t)
        i = i+1
    return ma_data

def get_percenttile(data_list, q, ma):
    """
    get q percenttile number
    """
    p = []
    for i in range(len(data_list)):
        if i <ma:
            p.append(np.percentile(data_list[0:i+1], q))
        else:
            p.append(np.percentile(data_list[i-ma:i+1], q))
    return p
        
        

def get_data_from_json():
    
    data = get_market_history_price(name = 'bitcoin', symbol = 'bitcoin', slug = 'bitcoin')
    if data is None:
        with open("btc.json",'r') as load_f:
            data = json.load(load_f)
            print("Successfully get data from json file from local computer!")
    return data



def data_process(data):
    # get BTC data from coinmarketcap.com
#    data = get_market_history_price(name = 'bitcoin', symbol = 'bitcoin', slug = 'bitcoin')
    
    
    # data pre-processing
    days = len(data)
    
    volume= []   # 交易量
    marketcap = [] # 市值
    ts = [] # 时间：day
    btc_price = [] # 收盘价
    
    for d in reversed(data):
        if d['volume'] == '-' :
            volume.append(0) #获取不到的数据用1代替
        else:
            volume.append(float(d['volume'].replace(',','')))
        marketcap.append(float(d['marketcap'].replace(',','')))
        ts.append(int(d['ts'].replace(',','')))
        btc_price.append(float(d['close'].replace(',','')))
    
    
    # get data volume != 0
    v_index = [i for i  in range(days) if volume[i] != 0]
    volume_btc = [volume[i] for i in v_index]
    marketcap_btc = [marketcap[i] for i in v_index]
    ts_btc = [ts[i] for i in v_index]
    btc_price_nvt = [btc_price[i] for i in v_index]
    return v_index, volume_btc, marketcap_btc, ts_btc, btc_price_nvt


def cal_NVT_plot(v_index, volume_btc, marketcap_btc, ts_btc, btc_price_nvt, ma_volume, ma_nvt):
    # calculation NVT signal
    # MA(1)
#    ma = 90
    
    volume_MA = MA_Avg(volume_btc, ma_volume) # 移动平均volume
    nvt_or = [marketcap_btc[i]/volume_MA[i] for i in range(len(v_index))] # volume ma 之后的nvt
    nvt0_or = [marketcap_btc[i]/volume_btc[i] for i in range(len(v_index))] # 无 ma的nvt
    nvt_MA_or = MA_Avg(nvt_or,ma_nvt) # nvt 进行ma
    
    # NVT 上下分位点
    up_bd = get_percenttile(nvt_or, 90, int(ma_nvt*2)) 
    down_bd = get_percenttile(nvt_or,10, int(ma_nvt/2))
    
    # normalized
#    nvt = [i/max(nvt_or) for i in nvt_or]
#    nvt0 = [i/max(nvt0_or) for i in nvt0_or]
#    nvt_MA = [i/max(nvt_MA_or) for i in nvt_MA_or]
    
    nvt = [i for i in nvt_or]
    nvt0 = [i for i in nvt0_or]
    nvt_MA = [i for i in nvt_MA_or]
    
    #btc price normalized
    
    
#    x_ts = ts_btc
#    x_ts = list(range(len(v_index)))
    
    
    # set  x axis 
    x_ts = [str(int(t/10000)) for t in ts_btc]  # get year
    axis_year = [i for i in range(1,len(x_ts)) if x_ts[i]!=x_ts[i-1]] # first day every year
    temp = [i for i in range(1,len(x_ts)) if x_ts[i]==x_ts[i-1]]
    for i in temp:
        x_ts[i]=''
#    x_ts[0] = ''  # 不显示第一个作标年份
    
        
    # plot figure    
    fig, ax1 = plt.subplots()
   
    p1, = ax1.plot(list(range(len(v_index))), btc_price_nvt, color='coral')  # btc 价格曲线
    
    ax2 = ax1.twinx()
    p2, = ax2.plot(list(range(len(v_index))), nvt, color='blue')  # NVT曲线 volume_MA=90
    p3, = ax2.plot(list(range(len(v_index))), nvt0, color='gray', alpha=0.2)  # NVT曲线 volume_MA=1
    p4, = ax2.plot(list(range(len(v_index))), nvt_MA, color='red')  # NVT曲线 volume_MA=90
    
#    p5, = ax2.plot(list(range(len(v_index))), up_bd, color='red')  # NVT up boundary
#    p6, = ax2.plot(list(range(len(v_index))), down_bd, color='yellow')  # NVT up boundary
    
    # 绘制NVT合理区间
    
    up_confident = [np.percentile(nvt, 70)]*len(v_index)
    down_confident = [np.percentile(nvt, 5)]*len(v_index)
    ax2.plot(list(range(len(v_index))), up_confident,'k--')   # 上界
    ax2.plot(list(range(len(v_index))), down_confident,'k--')   # 下界
    
    

    # 绘制年线
    x_real = list(range(len(v_index)))
    for i in axis_year:
        ax1.plot([x_real[i]]*100, list(np.linspace(0, math.ceil(max(btc_price_nvt)*1.1),100)) ,'k-.', alpha=0.5, lw=1)
    
    

    fig.legend(handles=(p1,p2), labels=('BTC Price USD','NVT Ratio'), loc=1, bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
    
    ax1.set_yscale('symlog', linthreshy=0.1)
    ax2.set_yscale('symlog', linthreshy=0.1)
    
    ax1.set_ylim(1, math.ceil(max(btc_price_nvt)*1.1))
#    ax2.set_ylim(0, max(nvt)*10)
#    ax2.set_ylim(0, 200000)
    
    ax1.set_xticks(list(range(len(v_index))))
    ax1.set_xticklabels(x_ts)
    
#    for label in ax1.xaxis.get_ticklabels():
#        # label is a Text instance
#        label.set_color('black')
#        label.set_rotation(0)
#        label.set_fontsize(12)
       

#    ax1.set_xticklabels(x_ts)
    ax1.set_title("Bitcoin NVT signal")
    ax1.set_xlabel("Time(day)")
    ax1.set_ylabel("BTC Price USD")
    ax2.set_ylabel("NVT Ratio")
    
    plt.grid(axis = 'y',linestyle='--')
    
#    plt.yticks()
#    ax1.set_xticklabels(x_ts)

    plt.show()
    
    return nvt, nvt_MA
 

if __name__ == '__main__':
    data = get_data_from_json() # 获取数据 网站获取或者本地获取
    v_index, volume_btc, marketcap_btc, ts_btc, btc_price_nvt = data_process(data) # 数据获取以及处理
    cal_NVT_plot(v_index, volume_btc, marketcap_btc, ts_btc, btc_price_nvt, ma_volume=28, ma_nvt=60) # 计算NVT并做图


























