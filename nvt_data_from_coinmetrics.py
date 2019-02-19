# -*- coding: utf-8 -*-
"""
Created on Sat Jan 12 19:08:57 2019

@author: Leo
"""

import nvt_model as nm
import get_data_from_api as gdfa
import numpy as np


data = gdfa.get_history_data()

v_index = list(range(len(data['price(usd)'])))

# times index
ts_btc = list(np.array(data['txvolume(usd)'])[:,0])

# adjust volume of on chain 
txvolume =list(np.array(data['adjustedtxvolume(usd)'])[:,1])

# exchane volume 
exchangevolume =list(np.array(data['exchangevolume(usd)'])[:,1])

# count of tranactions
tx_count =list(np.array(data['txcount'])[:,1])

# activeaddresses
activeaddresses =np.array(data['activeaddresses'])[:,1]

marketcap_btc = list(np.array(data['marketcap(usd)'])[:,1])
btc_price_nvt = list(np.array(data['price(usd)'])[:,1])



#volume_btc = list(np.power(activeaddresses,2))

# 链上交易量+交易所交易量
#volume_btc = [txvolume[i]+exchangevolume[i] for i in range(0,len(txvolume))] 

# 平均每次交易量
#volume_btc = [txvolume[i]/tx_count[i] for i in range(0,len(txvolume))] 

# 平均每个活跃地址的交易量
volume_btc = [txvolume[i]/activeaddresses[i] for i in range(0,len(txvolume))] 

# 平均每个活跃地址的交易量
#volume_btc = [activeaddresses[i] * activeaddresses[i] for i in range(0,len(txvolume))] 

#volume_btc = activeaddresses

# 平均每个活跃用户的 交易频次
#volume_btc = [activeaddresses[i] / tx_count[i] for i in range(0,len(txvolume))]





nvt, nvt_MA = nm.cal_NVT_plot(v_index, volume_btc, marketcap_btc, ts_btc, btc_price_nvt, ma_volume=30, ma_nvt=90)
