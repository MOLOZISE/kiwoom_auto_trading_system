import numpy as np
import pandas as pd
import math
COLUMNS_CHART_DATA = ['date', 'time', 'open', 'high', 'low', 'close', 'volume', 'pc']

COLUMNS_CHART_DATA_L = ['time', 'open', 'high', 'low', 'close', 'volume', 'pc']

COLUMNS_CHART_DATA_T = ['date', 'time', 'open', 'high', 'low', 'close', 'volume']

# 현재까지는 N만 썼지만 20200829 기준
COLUMNS_CHART_DATA_N = ['time', 'open', 'high', 'low', 'close', 'volume']

COLUMNS_CHART_DATA_TEST_H = ['mado_price', 'masu_price']

#################################################

# 이제는 새로운 시도를 위해 20200829 기준
COLUMNS_CHART_DATA_C = ['time', 'madohoga', 'masuhoga', 'close', 'nothing1', 'nothing2', 'nothing3', 'madovol', 'masuvol', 'sunmasu', 'nujuk', 'dagum', 'chegeul']

COLUMNS_CHART_DATA_U = ['time', 'close', 'chegeulvol', 'chegeul']

COLUMNS_CHART_DATA_X = ['time', 'close', 'accvol', 'chegeulvol', 'chegeul']

COLUMNS_CHART_DATA_Y = ['time', 'close', 'accvol', 'chegeul']

COLUMNS_CHART_DATA_Z = ['time', 'close', 'masuvol', 'madovol', 'chegeul']

COLUMNS_CHART_DATA_Z3 = ['time', 'close', 'moneyvol', 'chegeul']

COLUMNS_CHART_DATA_D = ['time', 'close', 'volume', 'bef_volume', 'aft_volume',
                        'moneyvolume', 'bef_moneyvolume', 'aft_moneyvolume',
                        'bef_volume_weight', 'aft_volume_weight', 'bef_moneyvolume_weight', 'aft_moneyvolume_weight']
COLUMNS_CHART_DATA_H = ['time', 'mado_price', 'masu_price', 'total_mado', 'total_masu',
                        'mado_1', 'mado_2', 'mado_3', 'mado_4', 'mado_5', 'mado_6', 'mado_7', 'mado_8', 'mado_9', 'mado_10',
                        'masu_1', 'masu_2', 'masu_3', 'masu_4', 'masu_5', 'masu_6', 'masu_7', 'masu_8', 'masu_9', 'masu_10']

COLUMNS_CHART_DATA_MM = ['mado_1', 'mado_2', 'mado_3', 'mado_4', 'mado_5', 'mado_6', 'mado_7', 'mado_8', 'mado_9', 'mado_10',
                        'masu_1', 'masu_2', 'masu_3', 'masu_4', 'masu_5', 'masu_6', 'masu_7', 'masu_8', 'masu_9', 'masu_10']

COLUMNS_CHART_DATA_H2 = ['stock_code', 'time', 'mado_price', 'masu_price', 'total_mado', 'total_masu',
                        'mado_1', 'mado_2', 'mado_3', 'mado_4', 'mado_5', 'mado_6', 'mado_7', 'mado_8', 'mado_9', 'mado_10',
                        'masu_1', 'masu_2', 'masu_3', 'masu_4', 'masu_5', 'masu_6', 'masu_7', 'masu_8', 'masu_9', 'masu_10',
                         '5_next_price']

COLUMNS_CHART_DATA_K = ['close']

COLUMNS_CHART_DATA_OSSP_ALL = ['next_close_ratio']

COLUMNS_CHART_DATA_M = ['mado_price', 'masu_price']

COLUMNS_CHART_DATA_H2_1 = ['price_uprate']

COLUMNS_TRAINING_DATA_C1 = [
    'close_lastclose_ratio',
    'madovol_lastmadovol_ratio',
    'masuvol_lastmasuvol_ratio',
    'chegeul_lastchegeul_ratio',
    'close_ma5_ratio', 'close_ma10_ratio',
    'madovol_ma5_ratio', 'madovol_ma10_ratio',
    'masuvol_ma5_ratio', 'masuvol_ma10_ratio',
    'chegeul_ma5_ratio', 'chegeul_ma10_ratio'
]

COLUMNS_TRAINING_DATA_U1 = [
    'close_lastclose_ratio',
    'chegeulvol_lastchegeulvol_ratio',
    'chegeul_lastchegeul_ratio',
    'close_ma5_ratio', 'close_ma10_ratio',
    'chegeulvol_ma5_ratio', 'chegeulvol_ma10_ratio',
    'chegeul_ma5_ratio', 'chegeul_ma10_ratio'
]

COLUMNS_TRAINING_DATA_X1 = [
    'close_lastclose_ratio',
    'accvol_lastaccvol_ratio',
    'chegeulvol_lastchegeulvol_ratio',
    'chegeul_lastchegeul_ratio',
    'close_ma5_ratio', 'close_ma10_ratio',
    'accvol_ma5_ratio', 'accvol_ma10_ratio',
    'chegeulvol_ma5_ratio', 'chegeulvol_ma10_ratio',
    'chegeul_ma5_ratio', 'chegeul_ma10_ratio'
]

COLUMNS_TRAINING_DATA_Y1 = [
    'close_lastclose_ratio',
    'accvol_lastaccvol_ratio',
    'chegeul_lastchegeul_ratio',
    'close_ma5_ratio', 'close_ma10_ratio',
    'accvol_ma5_ratio', 'accvol_ma10_ratio',
    'chegeul_ma5_ratio', 'chegeul_ma10_ratio'
]

COLUMNS_TRAINING_DATA_Y2 = [
    'close_ma5_ratio', 'close_ma10_ratio', 'close_ma15_ratio', 'close_ma20_ratio', 'close_ma25_ratio', 'close_ma30_ratio',
    'accvol_ma5_ratio', 'accvol_ma10_ratio', 'accvol_ma15_ratio', 'accvol_ma20_ratio', 'accvol_ma25_ratio', 'accvol_ma30_ratio',
    'chegeul_ma5_ratio', 'chegeul_ma10_ratio', 'chegeul_ma15_ratio', 'chegeul_ma20_ratio', 'chegeul_ma25_ratio', 'chegeul_ma30_ratio'
]

COLUMNS_TRAINING_DATA_Y3 = [
    'current_chegeul',
    'close_ma3_ratio', 'close_ma6_ratio', 'close_ma9_ratio', 'close_ma12_ratio', 'close_ma15_ratio',
    'accvol_ma3_ratio', 'accvol_ma6_ratio', 'accvol_ma9_ratio', 'accvol_ma12_ratio', 'accvol_ma15_ratio',
    'chegeul_ma3_ratio', 'chegeul_ma6_ratio', 'chegeul_ma9_ratio', 'chegeul_ma12_ratio', 'chegeul_ma15_ratio'
]

COLUMNS_TRAINING_DATA_Z1 = [
    'close_lastclose_ratio',
    'masuvol_lastmasuvol_ratio',
    'madovol_lastmadovol_ratio',
    'chegeul_lastchegeul_ratio',
    'close_ma5_ratio', 'close_ma10_ratio',
    'masuvol_ma5_ratio', 'masuvol_ma10_ratio',
    'madovol_ma5_ratio', 'madovol_ma10_ratio',
    'chegeul_ma5_ratio', 'chegeul_ma10_ratio'
]

COLUMNS_TRAINING_DATA_Z2 = [
    'accvol_lastaccvol_ratio',
    'chegeul_lastchegeul_ratio',
    'accvol_ma5_ratio', 'accvol_ma10_ratio', 'accvol_ma15_ratio',
    'chegeul_ma5_ratio', 'chegeul_ma10_ratio', 'chegeul_ma15_ratio'
]

COLUMNS_TRAINING_DATA_Z3 = [
    'moneyvol_lastmoneyvol_ratio',
    'chegeul_lastchegeul_ratio',
    'moneyvol_ma5_ratio', 'moneyvol_ma10_ratio',
    'chegeul_ma5_ratio', 'chegeul_ma10_ratio'
]

COLUMNS_TRAINING_DATA_DV = [
    'close_lastclose_ratio',
    'volume_lastvolume_ratio',
    'bef_volume_lastbef_volume_ratio',
    'aft_volume_lastaft_volume_ratio',
    'moneyvolume_lastmoneyvolume_ratio',
    'bef_moneyvolume_lastbef_moneyvolume_ratio',
    'aft_moneyvolume_lastaft_moneyvolume_ratio',
    'bef_volume_weight', 'aft_volume_weight',
    'bef_moneyvolume_weight', 'aft_moneyvolume_weight',
    'close_ma5_ratio', 'volume_ma5_ratio', 'bef_volume_ma5_ratio', 'aft_volume_ma5_ratio',
    'moneyvolume_ma5_ratio', 'bef_moneyvolume_ma5_ratio', 'aft_moneyvolume_ma5_ratio',
    'close_ma10_ratio', 'volume_ma10_ratio', 'bef_volume_ma10_ratio', 'aft_volume_ma10_ratio',
    'moneyvolume_ma10_ratio', 'bef_moneyvolume_ma10_ratio', 'aft_moneyvolume_ma10_ratio',
]

COLUMNS_TRAINING_DATA_H1 = [
    'mado_1w', 'mado_2w', 'mado_3w', 'mado_4w', 'mado_5w',
    'mado_6w', 'mado_7w', 'mado_8w', 'mado_9w', 'mado_10w',
    'masu_1w', 'masu_2w', 'masu_3w', 'masu_4w', 'masu_5w',
    'masu_6w', 'masu_7w', 'masu_8w', 'masu_9w', 'masu_10w',
    'mado_allrate', 'masu_allrate',
    'mado_lastmado_ratio', 'masu_lastmasu_ratio',
    'mado_ma5_ratio', 'mado_ma10_ratio',
    'masu_ma5_ratio', 'masu_ma10_ratio',
]

COLUMNS_TRAINING_DATA_H2 = [
    'mado_1w', 'mado_2w', 'mado_3w', 'mado_4w', 'mado_5w',
    'mado_6w', 'mado_7w', 'mado_8w', 'mado_9w', 'mado_10w',
    'masu_1w', 'masu_2w', 'masu_3w', 'masu_4w', 'masu_5w',
    'masu_6w', 'masu_7w', 'masu_8w', 'masu_9w', 'masu_10w',
    'mado_allrate', 'masu_allrate',
]

COLUMNS_TRAINING_DATA_H3 = [
    'mado_1w', 'mado_2w', 'mado_3w', 'mado_4w', 'mado_5w',
    'mado_6w', 'mado_7w', 'mado_8w', 'mado_9w', 'mado_10w',
    'masu_1w', 'masu_2w', 'masu_3w', 'masu_4w', 'masu_5w',
    'masu_6w', 'masu_7w', 'masu_8w', 'masu_9w', 'masu_10w'
]

################################################

COLUMNS_TRAINING_DATA_V1 = [
    'open_lastclose_ratio', 'high_close_ratio', 'low_close_ratio',
    'close_lastclose_ratio', 'volume_lastvolume_ratio',
    'close_ma5_ratio', 'volume_ma5_ratio',
    'close_ma10_ratio', 'volume_ma10_ratio',
    'close_ma20_ratio', 'volume_ma20_ratio',
    'close_ma60_ratio', 'volume_ma60_ratio',
    'close_ma120_ratio', 'volume_ma120_ratio',
]

##내가 만든 학습 데이터(V1 데이터로는 분봉에서의 조회가 어려워서...
COLUMNS_TRAINING_DATA_A1 = [
    'open_lastclose_ratio', 'high_lastclose_ratio', 'low_lastclose_ratio',
    'close_lastclose_ratio', 'volume_lastvolume_ratio', 'pc_lastpc_ratio',
    'open_ma5_ratio', 'open_ma10_ratio', 'open_ma15_ratio', 'open_ma20_ratio',
    'high_ma5_ratio', 'high_ma10_ratio', 'high_ma15_ratio', 'high_ma20_ratio',
    'low_ma5_ratio', 'low_ma10_ratio', 'low_ma15_ratio', 'low_ma20_ratio',
    'close_ma5_ratio', 'close_ma10_ratio', 'close_ma15_ratio', 'close_ma20_ratio',
    'volume_ma5_ratio', 'volume_ma10_ratio', 'volume_ma15_ratio', 'volume_ma20_ratio',
    'pc_ma5_ratio', 'pc_ma10_ratio', 'pc_ma15_ratio', 'pc_ma20_ratio'
]

COLUMNS_TRAINING_DATA_F1 = [
    'open_lastclose_ratio', 'high_lastclose_ratio', 'low_lastclose_ratio',
    'close_lastclose_ratio', 'volume_lastvolume_ratio',
    'open_ma5_ratio', 'open_ma10_ratio',
    'high_ma5_ratio', 'high_ma10_ratio',
    'low_ma5_ratio', 'low_ma10_ratio',
    'close_ma5_ratio', 'close_ma10_ratio',
    'volume_ma5_ratio', 'volume_ma10_ratio'
]

COLUMNS_TRAINING_DATA_T1 = [
    'open_lastclose_ratio', 'high_lastclose_ratio', 'low_lastclose_ratio',
    'close_lastclose_ratio', 'volume_lastvolume_ratio',
    'open_ma5_ratio', 'open_ma10_ratio',
    'high_ma5_ratio', 'high_ma10_ratio',
    'low_ma5_ratio', 'low_ma10_ratio',
    'close_ma5_ratio', 'close_ma10_ratio',
    'volume_ma5_ratio', 'volume_ma10_ratio'
]

COLUMNS_TRAINING_DATA_V1_RICH = [
    'open_lastclose_ratio', 'high_close_ratio', 'low_close_ratio',
    'close_lastclose_ratio', 'volume_lastvolume_ratio',
    'close_ma5_ratio', 'volume_ma5_ratio',
    'close_ma10_ratio', 'volume_ma10_ratio',
    'close_ma20_ratio', 'volume_ma20_ratio',
    'close_ma60_ratio', 'volume_ma60_ratio',
    'close_ma120_ratio', 'volume_ma120_ratio',
    'inst_lastinst_ratio', 'frgn_lastfrgn_ratio',
    'inst_ma5_ratio', 'frgn_ma5_ratio',
    'inst_ma10_ratio', 'frgn_ma10_ratio',
    'inst_ma20_ratio', 'frgn_ma20_ratio',
    'inst_ma60_ratio', 'frgn_ma60_ratio',
    'inst_ma120_ratio', 'frgn_ma120_ratio',
]

COLUMNS_TRAINING_DATA_V2 = [
    'per', 'pbr', 'roe',
    'open_lastclose_ratio', 'high_close_ratio', 'low_close_ratio',
    'close_lastclose_ratio', 'volume_lastvolume_ratio',
    'close_ma5_ratio', 'volume_ma5_ratio',
    'close_ma10_ratio', 'volume_ma10_ratio',
    'close_ma20_ratio', 'volume_ma20_ratio',
    'close_ma60_ratio', 'volume_ma60_ratio',
    'close_ma120_ratio', 'volume_ma120_ratio',
    'market_kospi_ma5_ratio', 'market_kospi_ma20_ratio',
    'market_kospi_ma60_ratio', 'market_kospi_ma120_ratio',
    'bond_k3y_ma5_ratio', 'bond_k3y_ma20_ratio',
    'bond_k3y_ma60_ratio', 'bond_k3y_ma120_ratio'
]

COLUMNS_TRAINING_DATA_OSSP_ALL = [
    'open_lastopen_ratio', 'high_lasthigh_ratio', 'low_lastlow_ratio',
    'close_lastclose_ratio', 'volume_lastvolume_ratio',
    'open_ma10_ratio', 'high_ma10_ratio', 'low_ma10_ratio', 'close_ma10_ratio', 'volume_ma10_ratio',
    'percent_b', 'Band_width',
    'PDI', 'MDI', 'ADX',
    'percent_k', 'percent_d',
    'MACD', 'SIGNAL',
    'RSI', 'Momentum'
]

COLUMNS_TRAINING_DATA_HT = [
    'mado_1w', 'mado_2w', 'mado_3w', 'mado_4w', 'mado_5w',
    'mado_6w', 'mado_7w', 'mado_8w', 'mado_9w', 'mado_10w',
    'masu_1w', 'masu_2w', 'masu_3w', 'masu_4w', 'masu_5w',
    'masu_6w', 'masu_7w', 'masu_8w', 'masu_9w', 'masu_10w',
    'mado_allrate', 'masu_allrate',
    'mado_ma5_sub', 'mado_ma10_sub',
    'mado_ma5_last', 'mado_ma10_last',
    'next_5'
]

def make_dataset(data, label, window_size=5):
    feature_list = []
    label_list = []
    for i in range(len(data) - window_size):
        feature_list.append(np.array(data.iloc[i:i+window_size]))
        label_list.append(np.array(label.iloc[i+window_size]))
    return np.array(feature_list), np.array(label_list)

def preprocess(input_data, ver):
    data = input_data
    # 시작 ~ 5분까지의 시고저종 거래량 평균으로 기준점을 잡고
    # 각 입력 데이터(시고저종 거래량을) v라 할때 각 훈련 데이터 = v - 기준점 / 기준점으로 비율로 나타내면 될듯?
    # 일봉 데이터 관찰 -> 5분 이동평균선이 주가를 잘 따르는 것 같음(경향성의 반영)
    if ver == 'a1':
        windows = [5, 10, 15, 20]  # 이동평균선 5분짜리만 사용 필요하다면 windows = [5, 10, 20, 60, 120] 추가 가능
        for window in windows:
            data['open_ma{}'.format(window)] = data['open'].rolling(window).mean()
            data['high_ma{}'.format(window)] = data['high'].rolling(window).mean()
            data['low_ma{}'.format(window)] = data['low'].rolling(window).mean()
            data['close_ma{}'.format(window)] = data['close'].rolling(window).mean()
            data['volume_ma{}'.format(window)] = data['volume'].rolling(window).mean()
            data['pc_ma{}'.format(window)] = data['pc'].rolling(window).mean()
            data['open_ma%d_ratio' % window] = (data['open'] - data['open_ma%d' % window]) / data['open_ma%d' % window]
            data['high_ma%d_ratio' % window] = (data['high'] - data['high_ma%d' % window]) / data['high_ma%d' % window]
            data['low_ma%d_ratio' % window] = (data['low'] - data['low_ma%d' % window]) / data['low_ma%d' % window]
            data['close_ma%d_ratio' % window] = (data['close'] - data['close_ma%d' % window]) / data['close_ma%d' % window]
            data['volume_ma%d_ratio' % window] = (data['volume'] - data['volume_ma%d' % window]) / data['volume_ma%d' % window]
            data['pc_ma%d_ratio' % window] = (data['pc'] - data['pc_ma%d' % window]) / data['pc_ma%d' % window]

        data['open_lastclose_ratio'] = np.zeros(len(data))
        data.loc[1:, 'open_ratio'] = (data.loc[1:, 'open'].copy().values - data.loc[:len(data)-2, 'close'].copy().values) / data.loc[:len(data)-2, 'close'].copy().values
        data['high_lastclose_ratio'] = np.zeros(len(data))
        data.loc[1:, 'high_ratio'] = (data.loc[1:, 'high'].copy().values - data.loc[:len(data)-2, 'close'].copy().values) / data.loc[:len(data)-2, 'close'].copy().values
        data['low_lastclose_ratio'] = np.zeros(len(data))
        data.loc[1:, 'low_ratio'] = (data.loc[1:, 'low'].copy().values - data.loc[:len(data)-2, 'close'].copy().values) / data.loc[:len(data)-2, 'close'].copy().values
        data['close_lastclose_ratio'] = np.zeros(len(data))
        data.loc[1:, 'close_ratio'] = (data.loc[1:, 'close'].copy().values - data.loc[:len(data)-2, 'close'].copy().values) / data.loc[:len(data)-2, 'close'].copy().values
        data['volume_lastvolume_ratio'] = np.zeros(len(data))
        data.loc[1:, 'volume_ratio'] = (data.loc[1:, 'volume'].copy().values - data.loc[:len(data)-2, 'volume'].copy().values) / data.loc[:len(data)-2, 'volume'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
        data['pc_lastpc_ratio'] = np.zeros(len(data))
        data.loc[1:, 'pc_ratio'] = (data.loc[1:, 'pc'].copy().values - data.loc[:len(data)-2, 'pc'].copy().values) / data.loc[:len(data)-2, 'pc'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
        print(data)
    if ver == 'f1':
        windows = [5, 10]  # 이동평균선 5분짜리만 사용 필요하다면 windows = [5, 10, 20, 60, 120] 추가 가능
        for window in windows:
            data['open_ma{}'.format(window)] = data['open'].rolling(window).mean()
            data['high_ma{}'.format(window)] = data['high'].rolling(window).mean()
            data['low_ma{}'.format(window)] = data['low'].rolling(window).mean()
            data['close_ma{}'.format(window)] = data['close'].rolling(window).mean()
            data['volume_ma{}'.format(window)] = data['volume'].rolling(window).mean()

            data['open_ma%d_ratio' % window] = (data['open'] - data['open_ma%d' % window]) / data['open_ma%d' % window]
            data['high_ma%d_ratio' % window] = (data['high'] - data['high_ma%d' % window]) / data['high_ma%d' % window]
            data['low_ma%d_ratio' % window] = (data['low'] - data['low_ma%d' % window]) / data['low_ma%d' % window]
            data['close_ma%d_ratio' % window] = (data['close'] - data['close_ma%d' % window]) / data['close_ma%d' % window]
            data['volume_ma%d_ratio' % window] = (data['volume'] - data['volume_ma%d' % window]) / data['volume_ma%d' % window]

        data['open_lastclose_ratio'] = np.zeros(len(data))
        data.loc[1:, 'open_lastclose_ratio'] = (data.loc[1:, 'open'].copy().values - data.loc[:len(data) - 2, 'close'].copy().values) / data.loc[:len(data) - 2, 'close'].copy().values
        data['high_lastclose_ratio'] = np.zeros(len(data))
        data.loc[1:, 'high_lastclose_ratio'] = (data.loc[1:, 'high'].copy().values - data.loc[:len(data) - 2, 'close'].copy().values) / data.loc[:len(data) - 2, 'close'].copy().values
        data['low_lastclose_ratio'] = np.zeros(len(data))
        data.loc[1:, 'low_lastclose_ratio'] = (data.loc[1:, 'low'].copy().values - data.loc[:len(data) - 2, 'close'].copy().values) / data.loc[:len(data) - 2, 'close'].copy().values
        data['close_lastclose_ratio'] = np.zeros(len(data))
        data.loc[1:, 'close_lastclose_ratio'] = (data.loc[1:, 'close'].copy().values - data.loc[:len(data) - 2, 'close'].copy().values) / data.loc[:len(data) - 2, 'close'].copy().values
        data['volume_lastvolume_ratio'] = np.zeros(len(data))
        data.loc[1:, 'volume_lastvolume_ratio'] = (data.loc[1:, 'volume'].copy().values - data.loc[:len(data) - 2, 'volume'].copy().values) / data.loc[:len(data) - 2, 'volume'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
    ########
    if ver == 'c1':
        windows = [5, 10]  # 이동평균선 5분짜리만 사용 필요하다면 windows = [5, 10, 20, 60, 120] 추가 가능
        for window in windows:
            data['close_ma{}'.format(window)] = data['close'].rolling(window).mean()
            data['madovol_ma{}'.format(window)] = data['madovol'].rolling(window).mean()
            data['masuvol_ma{}'.format(window)] = data['masuvol'].rolling(window).mean()
            data['chegeul_ma{}'.format(window)] = data['chegeul'].rolling(window).mean()

            data['close_ma%d_ratio' % window] = (data['close'] - data['close_ma%d' % window]) / data['close_ma%d' % window]
            data['madovol_ma%d_ratio' % window] = (data['madovol'] - data['madovol_ma%d' % window]) / data['madovol_ma%d' % window]
            data['masuvol_ma%d_ratio' % window] = (data['masuvol'] - data['masuvol_ma%d' % window]) / data['masuvol_ma%d' % window]
            data['chegeul_ma%d_ratio' % window] = (data['chegeul'] - data['chegeul_ma%d' % window]) / data['chegeul_ma%d' % window]

        data['close_lastclose_ratio'] = np.zeros(len(data))
        data.loc[1:, 'close_lastclose_ratio'] = (data.loc[1:, 'close'].copy().values - data.loc[:len(data) - 2, 'close'].copy().values) / data.loc[:len(data) - 2, 'close'].copy().values
        data['madovol_lastmadovol_ratio'] = np.zeros(len(data))
        data.loc[1:, 'madovol_lastmadovol_ratio'] = (data.loc[1:, 'madovol'].copy().values - data.loc[:len(data) - 2, 'madovol'].copy().values) / data.loc[:len(data) - 2, 'madovol'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
        data['madovol_lastmadovol_ratio'] = np.zeros(len(data))
        data.loc[1:, 'masuvol_lastmasuvol_ratio'] = (data.loc[1:, 'masuvol'].copy().values - data.loc[:len(data) - 2,'masuvol'].copy().values) / data.loc[:len(data) - 2,'masuvol'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
        data['madovol_lastmadovol_ratio'] = np.zeros(len(data))
        data.loc[1:, 'chegeul_lastchegeul_ratio'] = (data.loc[1:, 'chegeul'].copy().values - data.loc[:len(data) - 2,'chegeul'].copy().values) / data.loc[:len(data) - 2,'chegeul'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
    if ver == 'u1':
        windows = [5, 10]  # 이동평균선 5분짜리만 사용 필요하다면 windows = [5, 10, 20, 60, 120] 추가 가능
        for window in windows:
            data['close_ma{}'.format(window)] = data['close'].rolling(window).mean()
            data['chegeulvol_ma{}'.format(window)] = data['chegeulvol'].rolling(window).mean()
            data['chegeul_ma{}'.format(window)] = data['chegeul'].rolling(window).mean()

            data['close_ma%d_ratio' % window] = (data['close'] - data['close_ma%d' % window]) / data['close_ma%d' % window]
            data['chegeulvol_ma%d_ratio' % window] = (data['chegeulvol'] - data['chegeulvol_ma%d' % window]) / data['chegeulvol_ma%d' % window]
            data['chegeul_ma%d_ratio' % window] = (data['chegeul'] - data['chegeul_ma%d' % window]) / data['chegeul_ma%d' % window]

        data['close_lastclose_ratio'] = np.zeros(len(data))
        data.loc[1:, 'close_lastclose_ratio'] = (data.loc[1:, 'close'].copy().values - data.loc[:len(data) - 2, 'close'].copy().values) / data.loc[:len(data) - 2, 'close'].copy().values
        data['chegeulvol_lastchegeulvol_ratio'] = np.zeros(len(data))
        data.loc[1:, 'chegeulvol_lastchegeulvol_ratio'] = (data.loc[1:, 'chegeulvol'].copy().values - data.loc[:len(data) - 2, 'chegeulvol'].copy().values) / data.loc[:len(data) - 2, 'chegeulvol'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
        data['chegeul_lastchegeul_ratio'] = np.zeros(len(data))
        data.loc[1:, 'chegeul_lastchegeul_ratio'] = (data.loc[1:, 'chegeul'].copy().values - data.loc[:len(data) - 2,'chegeul'].copy().values) / data.loc[:len(data) - 2,'chegeul'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
    if ver == 'x1':
        windows = [5, 10]  # 이동평균선 5분짜리만 사용 필요하다면 windows = [5, 10, 20, 60, 120] 추가 가능
        for window in windows:
            data['close_ma{}'.format(window)] = data['close'].rolling(window).mean()
            data['accvol_ma{}'.format(window)] = data['accvol'].rolling(window).mean()
            data['chegeulvol_ma{}'.format(window)] = data['chegeulvol'].rolling(window).mean()
            data['chegeul_ma{}'.format(window)] = data['chegeul'].rolling(window).mean()

            data['close_ma%d_ratio' % window] = (data['close'] - data['close_ma%d' % window]) / data['close_ma%d' % window]
            data['accvol_ma%d_ratio' % window] = (data['accvol'] - data['accvol_ma%d' % window]) / data['accvol_ma%d' % window]
            data['chegeulvol_ma%d_ratio' % window] = (data['chegeulvol'] - data['chegeulvol_ma%d' % window]) / data['chegeulvol_ma%d' % window]
            data['chegeul_ma%d_ratio' % window] = (data['chegeul'] - data['chegeul_ma%d' % window]) / data['chegeul_ma%d' % window]

        data['close_lastclose_ratio'] = np.zeros(len(data))
        data.loc[1:, 'close_lastclose_ratio'] = (data.loc[1:, 'close'].copy().values - data.loc[:len(data) - 2, 'close'].copy().values) / data.loc[:len(data) - 2, 'close'].copy().values
        data['accvol_lastaccvol_ratio'] = np.zeros(len(data))
        data.loc[1:, 'accvol_lastaccvol_ratio'] = (data.loc[1:, 'accvol'].copy().values - data.loc[:len(data) - 2,'accvol'].copy().values) / data.loc[:len(data) - 2,'accvol'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
        data['chegeulvol_lastchegeulvol_ratio'] = np.zeros(len(data))
        data.loc[1:, 'chegeulvol_lastchegeulvol_ratio'] = (data.loc[1:, 'chegeulvol'].copy().values - data.loc[:len(data) - 2, 'chegeulvol'].copy().values) / data.loc[:len(data) - 2, 'chegeulvol'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
        data['chegeul_lastchegeul_ratio'] = np.zeros(len(data))
        data.loc[1:, 'chegeul_lastchegeul_ratio'] = (data.loc[1:, 'chegeul'].copy().values - data.loc[:len(data) - 2,'chegeul'].copy().values) / data.loc[:len(data) - 2,'chegeul'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
    if ver == 'y1':
        windows = [5, 10]  # 이동평균선 5분짜리만 사용 필요하다면 windows = [5, 10, 20, 60, 120] 추가 가능
        for window in windows:
            data['close_ma{}'.format(window)] = data['close'].rolling(window).mean()
            data['accvol_ma{}'.format(window)] = data['accvol'].rolling(window).mean()
            data['chegeul_ma{}'.format(window)] = data['chegeul'].rolling(window).mean()

            data['close_ma%d_ratio' % window] = (data['close'] - data['close_ma%d' % window]) / data['close_ma%d' % window]
            data['accvol_ma%d_ratio' % window] = (data['accvol'] - data['accvol_ma%d' % window]) / data['accvol_ma%d' % window]
            data['chegeul_ma%d_ratio' % window] = (data['chegeul'] - data['chegeul_ma%d' % window]) / data['chegeul_ma%d' % window]

        data['close_lastclose_ratio'] = np.zeros(len(data))
        data.loc[1:, 'close_lastclose_ratio'] = (data.loc[1:, 'close'].copy().values - data.loc[:len(data) - 2, 'close'].copy().values) / data.loc[:len(data) - 2, 'close'].copy().values
        data['accvol_lastaccvol_ratio'] = np.zeros(len(data))
        data.loc[1:, 'accvol_lastaccvol_ratio'] = (data.loc[1:, 'accvol'].copy().values - data.loc[:len(data) - 2,'accvol'].copy().values) / data.loc[:len(data) - 2,'accvol'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
        data['chegeul_lastchegeul_ratio'] = np.zeros(len(data))
        data.loc[1:, 'chegeul_lastchegeul_ratio'] = (data.loc[1:, 'chegeul'].copy().values - data.loc[:len(data) - 2,'chegeul'].copy().values) / data.loc[:len(data) - 2,'chegeul'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
    if ver == 'y2':
        windows = [5, 10, 15, 20, 25, 30]  # 이동평균선 5분짜리만 사용 필요하다면 windows = [5, 10, 20, 60, 120] 추가 가능
        for window in windows:
            data['close_ma{}'.format(window)] = data['close'].rolling(window).mean()
            data['accvol_ma{}'.format(window)] = data['accvol'].rolling(window).mean()
            data['chegeul_ma{}'.format(window)] = data['chegeul'].rolling(window).mean()

            data['close_ma%d_ratio' % window] = (data['close'] - data['close_ma%d' % window]) / data['close_ma%d' % window]
            data['accvol_ma%d_ratio' % window] = (data['accvol'] - data['accvol_ma%d' % window]) / data['accvol_ma%d' % window]
            data['chegeul_ma%d_ratio' % window] = (data['chegeul'] - data['chegeul_ma%d' % window]) / data['chegeul_ma%d' % window]
    if ver == 'y3':
        data['current_chegeul'] = data['chegeul']
        windows = [3, 6, 9, 12, 15]  # 이동평균선 5분짜리만 사용 필요하다면 windows = [5, 10, 20, 60, 120] 추가 가능
        for window in windows:
            data['close_ma{}'.format(window)] = data['close'].rolling(window).mean()
            data['accvol_ma{}'.format(window)] = data['accvol'].rolling(window).mean()
            data['chegeul_ma{}'.format(window)] = data['chegeul'].rolling(window).mean()

            data['close_ma%d_ratio' % window] = (data['close'] - data['close_ma%d' % window]) / data['close_ma%d' % window]
            data['accvol_ma%d_ratio' % window] = (data['accvol'] - data['accvol_ma%d' % window]) / data['accvol_ma%d' % window]
            data['chegeul_ma%d_ratio' % window] = (data['chegeul'] - data['chegeul_ma%d' % window]) / data['chegeul_ma%d' % window]
    if ver == 'z1':
        windows = [5, 10]  # 이동평균선 5분짜리만 사용 필요하다면 windows = [5, 10, 20, 60, 120] 추가 가능
        for window in windows:
            data['close_ma{}'.format(window)] = data['close'].rolling(window).mean()
            data['masuvol_ma{}'.format(window)] = data['masuvol'].rolling(window).mean()
            data['madovol_ma{}'.format(window)] = data['madovol'].rolling(window).mean()
            data['chegeul_ma{}'.format(window)] = data['chegeul'].rolling(window).mean()

            data['close_ma%d_ratio' % window] = (data['close'] - data['close_ma%d' % window]) / data['close_ma%d' % window]
            data['masuvol_ma%d_ratio' % window] = (data['masuvol'] - data['masuvol_ma%d' % window]) / data['masuvol_ma%d' % window]
            data['madovol_ma%d_ratio' % window] = (data['madovol'] - data['madovol_ma%d' % window]) / data['madovol_ma%d' % window]
            data['chegeul_ma%d_ratio' % window] = (data['chegeul'] - data['chegeul_ma%d' % window]) / data['chegeul_ma%d' % window]

        data['close_lastclose_ratio'] = np.zeros(len(data))
        data.loc[1:, 'close_lastclose_ratio'] = (data.loc[1:, 'close'].copy().values - data.loc[:len(data) - 2, 'close'].copy().values) / data.loc[:len(data) - 2, 'close'].copy().values
        data['masuvol_lastmasuvol_ratio'] = np.zeros(len(data))
        data.loc[1:, 'masuvol_lastmasuvol_ratio'] = (data.loc[1:, 'masuvol'].copy().values - data.loc[:len(data) - 2,'masuvol'].copy().values) / data.loc[:len(data) - 2, 'masuvol'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
        data['madovol_lastmadovol_ratio'] = np.zeros(len(data))
        data.loc[1:, 'madovol_lastmadovol_ratio'] = (data.loc[1:, 'madovol'].copy().values - data.loc[:len(data) - 2,'madovol'].copy().values) / data.loc[:len(data) - 2,'madovol'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
        data['chegeul_lastchegeul_ratio'] = np.zeros(len(data))
        data.loc[1:, 'chegeul_lastchegeul_ratio'] = (data.loc[1:, 'chegeul'].copy().values - data.loc[:len(data) - 2,'chegeul'].copy().values) / data.loc[:len(data) - 2, 'chegeul'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
    if ver == 'z3':
        windows = [5, 10]  # 이동평균선 5분짜리만 사용 필요하다면 windows = [5, 10, 20, 60, 120] 추가 가능
        for window in windows:
            data['close_ma{}'.format(window)] = data['close'].rolling(window).mean()
            data['moneyvol_ma{}'.format(window)] = data['moneyvol'].rolling(window).mean()
            data['chegeul_ma{}'.format(window)] = data['chegeul'].rolling(window).mean()

            data['close_ma%d_ratio' % window] = (data['close'] - data['close_ma%d' % window]) / data['close_ma%d' % window]
            data['moneyvol_ma%d_ratio' % window] = (data['moneyvol'] - data['moneyvol_ma%d' % window]) / data['moneyvol_ma%d' % window]
            data['chegeul_ma%d_ratio' % window] = (data['chegeul'] - data['chegeul_ma%d' % window]) / data['chegeul_ma%d' % window]

        data['close_lastclose_ratio'] = np.zeros(len(data))
        data.loc[1:, 'close_lastclose_ratio'] = (data.loc[1:, 'close'].copy().values - data.loc[:len(data) - 2, 'close'].copy().values) / data.loc[:len(data) - 2, 'close'].copy().values
        data['moneyvol_lastmoneyvol_ratio'] = np.zeros(len(data))
        data.loc[1:, 'moneyvol_lastmoneyvol_ratio'] = (data.loc[1:, 'moneyvol'].copy().values - data.loc[:len(data) - 2, 'moneyvol'].copy().values) / data.loc[:len(data) - 2, 'moneyvol'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
        data['chegeul_lastchegeul_ratio'] = np.zeros(len(data))
        data.loc[1:, 'chegeul_lastchegeul_ratio'] = (data.loc[1:, 'chegeul'].copy().values - data.loc[:len(data) - 2, 'chegeul'].copy().values) / data.loc[:len(data) - 2, 'chegeul'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
    if ver == 'dv':
        windows = [5, 10]  # 이동평균선 5분짜리만 사용 필요하다면 windows = [5, 10, 20, 60, 120] 추가 가능
        for window in windows:
            data['close_ma{}'.format(window)] = data['close'].rolling(window).mean()
            data['volume_ma{}'.format(window)] = data['volume'].rolling(window).mean()
            data['moneyvolume_ma{}'.format(window)] = data['moneyvolume'].rolling(window).mean()
            data['bef_volume_ma{}'.format(window)] = data['bef_volume'].rolling(window).mean()
            data['aft_volume_ma{}'.format(window)] = data['aft_volume'].rolling(window).mean()
            data['bef_moneyvolume_ma{}'.format(window)] = data['bef_moneyvolume'].rolling(window).mean()
            data['aft_moneyvolume_ma{}'.format(window)] = data['aft_moneyvolume'].rolling(window).mean()
            # data['bef_volume_weight_ma{}'.format(window)] = data['bef_volume_weight'].rolling(window).mean()
            # data['aft_volume_weight_ma{}'.format(window)] = data['aft_volume_weight'].rolling(window).mean()
            # data['bef_moneyvolume_weight_ma{}'.format(window)] = data['bef_moneyvolume_weight'].rolling(window).mean()
            # data['aft_moneyvolume_weight_ma{}'.format(window)] = data['aft_moneyvolume_weight'].rolling(window).mean()

            data['close_ma%d_ratio' % window] = (data['close'] - data['close_ma%d' % window]) / data['close_ma%d' % window]
            data['volume_ma%d_ratio' % window] = (data['volume'] - data['volume_ma%d' % window]) / data['volume_ma%d' % window]
            data['moneyvolume_ma%d_ratio' % window] = (data['moneyvolume'] - data['moneyvolume_ma%d' % window]) / data['moneyvolume_ma%d' % window]
            data['bef_volume_ma%d_ratio' % window] = (data['bef_volume'] - data['bef_volume_ma%d' % window]) / data[
                'bef_volume_ma%d' % window]
            data['aft_volume_ma%d_ratio' % window] = (data['aft_volume'] - data['aft_volume_ma%d' % window]) / data[
                'aft_volume_ma%d' % window]
            data['bef_moneyvolume_ma%d_ratio' % window] = (data['bef_moneyvolume'] - data['bef_moneyvolume_ma%d' % window]) / data[
                'bef_moneyvolume_ma%d' % window]
            data['aft_moneyvolume_ma%d_ratio' % window] = (data['aft_moneyvolume'] - data['aft_moneyvolume_ma%d' % window]) / data[
                'aft_moneyvolume_ma%d' % window]
            # data['bef_volume_weight_ma%d_ratio' % window] = (data['bef_volume_weight'] - data['bef_volume_weight_ma%d' % window]) / data[
            #     'bef_volume_weight_ma%d' % window]
            # data['aft_volume_weight_ma%d_ratio' % window] = (data['aft_volume_weight'] - data['aft_volume_weight_ma%d' % window]) / data[
            #     'aft_volume_weight_ma%d' % window]
            # data['bef_moneyvolume_weight_ma%d_ratio' % window] = (data['bef_moneyvolume_weight'] - data['bef_moneyvolume_weight_ma%d' % window]) / data[
            #     'bef_moneyvolume_weight_ma%d' % window]
            # data['aft_moneyvolume_weight_ma%d_ratio' % window] = (data['aft_moneyvolume_weight'] - data['aft_moneyvolume_weight_ma%d' % window]) / data[
            #     'aft_moneyvolume_weight_ma%d' % window]

        data['close_lastclose_ratio'] = np.zeros(len(data))
        data.loc[1:, 'close_lastclose_ratio'] = (data.loc[1:, 'close'].copy().values - data.loc[:len(data) - 2,'close'].copy().values) / data.loc[:len(data) - 2,'close'].copy().values
        data['volume_lastvolume_ratio'] = np.zeros(len(data))
        data.loc[1:, 'volume_lastvolume_ratio'] = (data.loc[1:, 'volume'].copy().values - data.loc[:len(data) - 2,'volume'].copy().values) / data.loc[:len(data) - 2,'volume'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
        data['bef_volume_lastbef_volume_ratio'] = np.zeros(len(data))
        data.loc[1:, 'bef_volume_lastbef_volume_ratio'] = (data.loc[1:, 'bef_volume'].copy().values - data.loc[:len(data) - 2,'bef_volume'].copy().values) / data.loc[:len(data) - 2,'bef_volume'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
        data['aft_volume_lastaft_volume_ratio'] = np.zeros(len(data))
        data.loc[1:, 'aft_volume_lastaft_volume_ratio'] = (data.loc[1:, 'aft_volume'].copy().values - data.loc[:len(data) - 2,'aft_volume'].copy().values) / data.loc[:len(data) - 2,'aft_volume'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
        data['moneyvolume_lastmoneyvolume_ratio'] = np.zeros(len(data))
        data.loc[1:, 'moneyvolume_lastmoneyvolume_ratio'] = (data.loc[1:, 'moneyvolume'].copy().values - data.loc[:len(data) - 2,'moneyvolume'].copy().values) / data.loc[:len(data) - 2,'moneyvolume'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
        data['bef_moneyvolume_lastbef_moneyvolume_ratio'] = np.zeros(len(data))
        data.loc[1:, 'bef_moneyvolume_lastbef_moneyvolume_ratio'] = (data.loc[1:, 'bef_moneyvolume'].copy().values - data.loc[:len(data) - 2,'bef_moneyvolume'].copy().values) / data.loc[:len(data) - 2,'bef_moneyvolume'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
        data['aft_moneyvolume_lastaft_moneyvolume_ratio'] = np.zeros(len(data))
        data.loc[1:, 'aft_moneyvolume_lastaft_moneyvolume_ratio'] = (data.loc[1:, 'aft_moneyvolume'].copy().values - data.loc[:len(data) - 2,'aft_moneyvolume'].copy().values) / data.loc[:len(data) - 2,'aft_moneyvolume'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
    if ver == 'h1':
        windows = [5, 10]  # 이동평균선 5분짜리만 사용 필요하다면 windows = [5, 10, 20, 60, 120] 추가 가능
        for window in windows:
            data['mado_ma{}'.format(window)] = data['total_mado'].rolling(window).mean()
            data['masu_ma{}'.format(window)] = data['total_masu'].rolling(window).mean()

            data['mado_ma%d_ratio' % window] = (data['total_mado'] - data['mado_ma%d' % window]) / data['mado_ma%d' % window]
            data['masu_ma%d_ratio' % window] = (data['total_masu'] - data['masu_ma%d' % window]) / data['masu_ma%d' % window]

        data['mado_lastmado_ratio'] = np.zeros(len(data))
        data.loc[1:, 'mado_lastmado_ratio'] = (data.loc[1:, 'total_mado'].copy().values - data.loc[:len(data) - 2,'total_mado'].copy().values) / data.loc[:len(data) - 2,'total_mado'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
        data['masu_lastmasu_ratio'] = np.zeros(len(data))
        data.loc[1:, 'masu_lastmasu_ratio'] = (data.loc[1:, 'total_masu'].copy().values - data.loc[:len(data) - 2,'total_masu'].copy().values) / data.loc[:len(data) - 2,'total_masu'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
        data['mado_allrate'] = (data['total_mado'] / (data['total_mado'] + data['total_masu']))
        data['masu_allrate'] = (data['total_masu'] / (data['total_mado'] + data['total_masu']))
        for numa in range(10):
            i = numa + 1
            data['mado_%dw' % i] = (data['mado_%d' % i] / data['total_mado'])
        for numb in range(10):
            j = numb + 1
            data['masu_%dw' % j] = (data['masu_%d' % j] / data['total_masu'])
    if ver == 'h2':
        data['mado_allrate'] = (data['total_mado'] / (data['total_mado'] + data['total_masu']))
        data['masu_allrate'] = (data['total_masu'] / (data['total_mado'] + data['total_masu']))
        for numa in range(10):
            i = numa + 1
            data['mado_%dw' % i] = (data['mado_%d' % i] / data['total_mado'])
        for numb in range(10):
            j = numb + 1
            data['masu_%dw' % j] = (data['masu_%d' % j] / data['total_masu'])
        data['price_uprate'] = ((data['masu_price'] - data['5_next_price']) / data['masu_price']) * (1000)
        is_less = (data['price_uprate'] >= -300)
        is_more = (data['price_uprate'] <= 300)
        data = data[is_less & is_more]
        un_less = (data['price_uprate'] <= -10)
        un_more = (data['price_uprate'] >= 10)
        data = data[un_less | un_more]
        # def category(x):
        #     if x <= -30:
        #         return 0
        #     elif (x >= -30) & (x <= -20):
        #         return 1
        #     elif (x >= -20) & (x <= -10):
        #         return 2
        #     elif (x >= -10) & (x <= 0):
        #         return 3
        #     elif (x >= 0) & (x <= 10):
        #         return 4
        #     elif (x >= 10) & (x <= 20):
        #         return 5
        #     elif (x >= 20) & (x <= 30):
        #         return 6
        #     else:
        #         return 7
        # # def category(x):
        # #     if (x <= 0):
        # #         return 0
        # #     else:
        # #         return 1
        # data['price_uprate'] = data['price_uprate'].apply(category)
        #data = data[data['price_uprate'] != 0]
        # def sigmoid(x):
        #     return 1 / (1 + np.exp(-x))
        #data['price_uprate'] = np.tanh(data['price_uprate'])
    #######
    if ver == 'h3':
        for numa in range(10):
            i = numa + 1
            data['mado_%dw' % i] = (data['mado_%d' % i] / (data['total_mado'] + data['total_masu']))
        for numb in range(10):
            j = numb + 1
            data['masu_%dw' % j] = (data['masu_%d' % j] / (data['total_mado'] + data['total_masu']))
        data['price_uprate'] = ((data['5_next_price'] - data['mado_price']) / data['mado_price']) * (1000)
        #data['price_uprate'] = np.where(data['price_uprate'] > 0, 0, 1)

        #data['price_uprate'] = ((data['5_next_price'] - data['masu_price']) / data['masu_price']) * (1000)
        #is_zero = (data['mado_price'] == 0)
        # is_less = (data['price_uprate'] >= -300)
        # is_more = (data['price_uprate'] <= 300)
        # data = data[is_less & is_more]
        # un_less = (data['price_uprate'] <= -10)
        # un_more = (data['price_uprate'] >= 10)
        # data = data[un_less | un_more]
        # #data = data[data['price_uprate'] != 0]
    if ver == 'v1' or ver == 'v1.rich':
        windows = [5, 10, 20, 60, 120]
        for window in windows:
            data['close_ma{}'.format(window)] = data['close'].rolling(window).mean()
            data['volume_ma{}'.format(window)] = data['volume'].rolling(window).mean()
            data['close_ma%d_ratio' % window] = (data['close'] - data['close_ma%d' % window]) / data[
                'close_ma%d' % window]
            data['volume_ma%d_ratio' % window] = (data['volume'] - data['volume_ma%d' % window]) / data[
                'volume_ma%d' % window]

            if ver == 'v1.rich':
                data['inst_ma{}'.format(window)] = \
                    data['close'].rolling(window).mean()
                data['frgn_ma{}'.format(window)] = \
                    data['volume'].rolling(window).mean()
                data['inst_ma%d_ratio' % window] = \
                    (data['close'] - data['inst_ma%d' % window]) \
                    / data['inst_ma%d' % window]
                data['frgn_ma%d_ratio' % window] = \
                    (data['volume'] - data['frgn_ma%d' % window]) \
                    / data['frgn_ma%d' % window]

        data['open_lastclose_ratio'] = np.zeros(len(data))
        data.loc[1:, 'open_lastclose_ratio'] = (data['open'][1:].values - data['close'][:-1].values) / data['close'][
                                                                                                       :-1].values

        data['high_close_ratio'] = (data['high'].values - data['close'].values) / data['close'].values

        data['low_close_ratio'] = (data['low'].values - data['close'].values) / data['close'].values

        data['close_lastclose_ratio'] = np.zeros(len(data))
        data.loc[1:, 'close_lastclose_ratio'] = (data['close'][1:].values - data['close'][:-1].values) / data['close'][
                                                                                                         :-1].values

        data['volume_lastvolume_ratio'] = np.zeros(len(data))
        data.loc[1:, 'volume_lastvolume_ratio'] = (data['volume'][1:].values - data['volume'][:-1].values) / data[
                                                                                                                 'volume'][
                                                                                                             :-1].replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values

        if ver == 'v1.rich':
            data['inst_lastinst_ratio'] = np.zeros(len(data))
            data.loc[1:, 'inst_lastinst_ratio'] = \
                (data['inst'][1:].values - data['inst'][:-1].values) \
                / data['inst'][:-1] \
                    .replace(to_replace=0, method='ffill') \
                    .replace(to_replace=0, method='bfill').values
            data['frgn_lastfrgn_ratio'] = np.zeros(len(data))
            data.loc[1:, 'frgn_lastfrgn_ratio'] = \
                (data['frgn'][1:].values - data['frgn'][:-1].values) \
                / data['frgn'][:-1] \
                    .replace(to_replace=0, method='ffill') \
                    .replace(to_replace=0, method='bfill').values
    if ver == 'ossp_all':
        # 주가, 거래량 이동 평균
        windows0 = [10]  # 이동평균선 5분짜리만 사용 필요하다면 windows = [5, 10, 20, 60, 120] 추가 가능
        for window in windows0:
            data['open_ma{}'.format(window)] = data['open'].rolling(window).mean()
            data['high_ma{}'.format(window)] = data['high'].rolling(window).mean()
            data['low_ma{}'.format(window)] = data['low'].rolling(window).mean()
            data['close_ma{}'.format(window)] = data['close'].rolling(window).mean()
            data['volume_ma{}'.format(window)] = data['volume'].rolling(window).mean()
            # 주가, 거래량 이동 평균 비율
            data['open_ma%d_ratio' % window] = (data['open'] - data['open_ma%d' % window]) / data['open_ma%d' % window]
            data['high_ma%d_ratio' % window] = (data['high'] - data['high_ma%d' % window]) / data['high_ma%d' % window]
            data['low_ma%d_ratio' % window] = (data['low'] - data['low_ma%d' % window]) / data['low_ma%d' % window]
            data['close_ma%d_ratio' % window] = (data['close'] - data['close_ma%d' % window]) / data['close_ma%d' % window]
            data['volume_ma%d_ratio' % window] = (data['volume'] - data['volume_ma%d' % window]) / data['volume_ma%d' % window]
        windows1 = [20]
        # BollingerBand
        for window in windows1:
            # 중심선 # 20개 표준편차 # 하한선 # 상한선
            data['close_ma{}'.format(window)] = data['close'].rolling(window).mean()
            data['close_std{}'.format(window)] = data['close'].rolling(window).std()
            data['down_line'] = data['close_ma{}'.format(window)] - data['close_std{}'.format(window)] * 2
            data['upper_line'] = data['close_ma{}'.format(window)] + data['close_std{}'.format(window)] * 2
            data['percent_b'] = (data['close'] - data['down_line']) / (data['upper_line'] - data['down_line'])
            data['Band_width'] = (data['upper_line'] - data['down_line']) / data['close_ma{}'.format(window)]
        # DMI
        data['PDM'] = np.zeros(len(data))
        data.loc[1:, 'PDM'] = np.abs(data.loc[1:, 'high'].copy().values - data.loc[:len(data) - 2, 'high'].copy().values)
        data['MDM'] = np.zeros(len(data))
        data.loc[1:, 'MDM'] = np.abs(data.loc[1:, 'low'].copy().values - data.loc[:len(data) - 2, 'low'].copy().values)
        data['TR'] = np.zeros(len(data))
        data.loc[1:, 'TR'] = np.maximum(np.abs(data.loc[1:, 'high'].copy().values - data.loc[1:, 'low'].copy().values),
                                    np.abs(data.loc[1:, 'high'].copy().values - data.loc[:len(data) - 2, 'close'].copy().values),
                                    np.abs(data.loc[1:, 'low'].copy().values - data.loc[:len(data) - 2, 'close'].copy().values))
        windows2 = [10]
        for window in windows2:
            data['PDI'] = data['PDM'].rolling(window).mean() / data['TR'].rolling(window).mean()
            data['MDI'] = data['MDM'].rolling(window).mean() / data['TR'].rolling(window).mean()
        data['ADX'] = np.abs(data['PDI'] - data['MDI']) / (data['PDI'] + data['MDI']) * 100
        # STOCHASTIC
        windows3 = [5]
        for window in windows3:
            data['percent_k'] = (data['close'] - data['close'].rolling(window).min()) / (data['close'].rolling(window).max() - data['close'].rolling(window).min())
        windows4 = [3]
        for window in windows4:
            data['percent_d'] = data['percent_k'].rolling(window).mean()
        # MACD
        data['ema12'] = data['close'].ewm(12).mean()
        data['ema26'] = data['close'].ewm(26).mean()
        data['MACD'] = data['ema12'] - data['ema26']
        data['SIGNAL'] = data['MACD'].ewm(9).mean()
        # RSI
        windows5 = [14]
        data['U'] = np.where(data['close'].diff(1) > 0, data['close'].diff(1), 0)
        data['D'] = np.where(data['close'].diff(1) < 0, data['close'].diff(1) * (-1), 0)
        for window in windows5:
            data['RSI'] = data['U'].rolling(window).mean() / (data['U'].rolling(window).mean() + data['D'].rolling(window).mean())
        # Momentum
        data['Momentum'] = np.zeros(len(data))
        data.loc[10:, 'Momentum'] = (data.loc[10:, 'close'].copy().values / data.loc[:len(data)-11, 'close'].copy().values) * 100

        # 주가, 거래량 전 대비 비율
        data['open_lastopen_ratio'] = np.zeros(len(data))
        data.loc[1:, 'open_lastopen_ratio'] = (data.loc[1:, 'open'].copy().values - data.loc[:len(data)-2, 'open'].copy().values) / data.loc[:len(data)-2, 'open'].copy().values
        data['high_lasthigh_ratio'] = np.zeros(len(data))
        data.loc[1:, 'high_lasthigh_ratio'] = (data.loc[1:, 'high'].copy().values - data.loc[:len(data)-2, 'high'].copy().values) / data.loc[:len(data)-2, 'high'].copy().values
        data['low_lastlow_ratio'] = np.zeros(len(data))
        data.loc[1:, 'low_lastlow_ratio'] = (data.loc[1:, 'low'].copy().values - data.loc[:len(data)-2, 'low'].copy().values) / data.loc[:len(data)-2, 'low'].copy().values
        data['close_lastclose_ratio'] = np.zeros(len(data))
        data.loc[1:, 'close_lastclose_ratio'] = (data.loc[1:, 'close'].copy().values - data.loc[:len(data)-2, 'close'].copy().values) / data.loc[:len(data)-2, 'close'].copy().values
        data['volume_lastvolume_ratio'] = np.zeros(len(data))
        data.loc[1:, 'volume_lastvolume_ratio'] = (data.loc[1:, 'volume'].copy().values - data.loc[:len(data)-2, 'volume'].copy().values) / data.loc[:len(data)-2, 'volume'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
        data['next_close_ratio'] = np.zeros(len(data))
        data.loc[:len(data)-2, 'next_close_ratio'] = (data.loc[1:, 'close'].copy().values - data.loc[:len(data)-2, 'close'].copy().values) / data.loc[:len(data)-2, 'close'].copy().values * 100
    if ver == 'ossp_lstm':
        # 주가, 거래량 이동 평균
        windows0 = [10]  # 이동평균선 5분짜리만 사용 필요하다면 windows = [5, 10, 20, 60, 120] 추가 가능
        for window in windows0:
            data['open_ma{}'.format(window)] = data['open'].rolling(window).mean()
            data['high_ma{}'.format(window)] = data['high'].rolling(window).mean()
            data['low_ma{}'.format(window)] = data['low'].rolling(window).mean()
            data['close_ma{}'.format(window)] = data['close'].rolling(window).mean()
            data['volume_ma{}'.format(window)] = data['volume'].rolling(window).mean()
            # 주가, 거래량 이동 평균 비율
            data['open_ma%d_ratio' % window] = (data['open'] - data['open_ma%d' % window]) / data['open_ma%d' % window]
            data['high_ma%d_ratio' % window] = (data['high'] - data['high_ma%d' % window]) / data['high_ma%d' % window]
            data['low_ma%d_ratio' % window] = (data['low'] - data['low_ma%d' % window]) / data['low_ma%d' % window]
            data['close_ma%d_ratio' % window] = (data['close'] - data['close_ma%d' % window]) / data[
                'close_ma%d' % window]
            data['volume_ma%d_ratio' % window] = (data['volume'] - data['volume_ma%d' % window]) / data[
                'volume_ma%d' % window]
        windows1 = [20]
        # BollingerBand
        for window in windows1:
            # 중심선 # 20개 표준편차 # 하한선 # 상한선
            data['close_ma{}'.format(window)] = data['close'].rolling(window).mean()
            data['close_std{}'.format(window)] = data['close'].rolling(window).std()
            data['down_line'] = data['close_ma{}'.format(window)] - data['close_std{}'.format(window)] * 2
            data['upper_line'] = data['close_ma{}'.format(window)] + data['close_std{}'.format(window)] * 2
            data['percent_b'] = (data['close'] - data['down_line']) / (data['upper_line'] - data['down_line'])
            data['Band_width'] = (data['upper_line'] - data['down_line']) / data['close_ma{}'.format(window)]
        # DMI
        data['PDM'] = np.zeros(len(data))
        data.loc[1:, 'PDM'] = np.abs(
            data.loc[1:, 'high'].copy().values - data.loc[:len(data) - 2, 'high'].copy().values)
        data['MDM'] = np.zeros(len(data))
        data.loc[1:, 'MDM'] = np.abs(data.loc[1:, 'low'].copy().values - data.loc[:len(data) - 2, 'low'].copy().values)
        data['TR'] = np.zeros(len(data))
        data.loc[1:, 'TR'] = np.maximum(np.abs(data.loc[1:, 'high'].copy().values - data.loc[1:, 'low'].copy().values),
                                        np.abs(data.loc[1:, 'high'].copy().values - data.loc[:len(data) - 2,
                                                                                    'close'].copy().values),
                                        np.abs(data.loc[1:, 'low'].copy().values - data.loc[:len(data) - 2,
                                                                                   'close'].copy().values))
        windows2 = [10]
        for window in windows2:
            data['PDI'] = data['PDM'].rolling(window).mean() / data['TR'].rolling(window).mean()
            data['MDI'] = data['MDM'].rolling(window).mean() / data['TR'].rolling(window).mean()
        data['ADX'] = np.abs(data['PDI'] - data['MDI']) / (data['PDI'] + data['MDI']) * 100
        # STOCHASTIC
        windows3 = [5]
        for window in windows3:
            data['percent_k'] = (data['close'] - data['close'].rolling(window).min()) / (
                        data['close'].rolling(window).max() - data['close'].rolling(window).min())
        windows4 = [3]
        for window in windows4:
            data['percent_d'] = data['percent_k'].rolling(window).mean()
        # MACD
        data['ema12'] = data['close'].ewm(12).mean()
        data['ema26'] = data['close'].ewm(26).mean()
        data['MACD'] = data['ema12'] - data['ema26']
        data['SIGNAL'] = data['MACD'].ewm(9).mean()
        # RSI
        windows5 = [14]
        data['U'] = np.where(data['close'].diff(1) > 0, data['close'].diff(1), 0)
        data['D'] = np.where(data['close'].diff(1) < 0, data['close'].diff(1) * (-1), 0)
        for window in windows5:
            data['RSI'] = data['U'].rolling(window).mean() / (
                        data['U'].rolling(window).mean() + data['D'].rolling(window).mean())
        # Momentum
        data['Momentum'] = np.zeros(len(data))
        data.loc[10:, 'Momentum'] = (data.loc[10:, 'close'].copy().values / data.loc[:len(data) - 11,
                                                                            'close'].copy().values) * 100

        # 주가, 거래량 전 대비 비율
        data['open_lastopen_ratio'] = np.zeros(len(data))
        data.loc[1:, 'open_lastopen_ratio'] = (data.loc[1:, 'open'].copy().values - data.loc[:len(data) - 2,
                                                                                    'open'].copy().values) / data.loc[
                                                                                                             :len(
                                                                                                                 data) - 2,
                                                                                                             'open'].copy().values
        data['high_lasthigh_ratio'] = np.zeros(len(data))
        data.loc[1:, 'high_lasthigh_ratio'] = (data.loc[1:, 'high'].copy().values - data.loc[:len(data) - 2,
                                                                                    'high'].copy().values) / data.loc[
                                                                                                             :len(
                                                                                                                 data) - 2,
                                                                                                             'high'].copy().values
        data['low_lastlow_ratio'] = np.zeros(len(data))
        data.loc[1:, 'low_lastlow_ratio'] = (data.loc[1:, 'low'].copy().values - data.loc[:len(data) - 2,
                                                                                 'low'].copy().values) / data.loc[
                                                                                                         :len(data) - 2,
                                                                                                         'low'].copy().values
        data['close_lastclose_ratio'] = np.zeros(len(data))
        data.loc[1:, 'close_lastclose_ratio'] = (data.loc[1:, 'close'].copy().values - data.loc[:len(data) - 2,
                                                                                       'close'].copy().values) / data.loc[
                                                                                                                 :len(
                                                                                                                     data) - 2,
                                                                                                                 'close'].copy().values
        data['volume_lastvolume_ratio'] = np.zeros(len(data))
        data.loc[1:, 'volume_lastvolume_ratio'] = (data.loc[1:, 'volume'].copy().values - data.loc[:len(data) - 2,
                                                                                          'volume'].copy().values) / data.loc[
                                                                                                                     :len(
                                                                                                                         data) - 2,
                                                                                                                     'volume'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
        data['next_close_ratio'] = np.zeros(len(data))
        data.loc[:len(data) - 2, 'next_close_ratio'] = (data.loc[1:, 'close'].copy().values - data.loc[:len(data) - 2,
                                                                                              'close'].copy().values) / data.loc[
                                                                                                                        :len(
                                                                                                                            data) - 2,
                                                                                                                        'close'].copy().values * 100
    if ver == 'test_h':
        windows = [5, 10]  # 이동평균선 5분짜리만 사용 필요하다면 windows = [5, 10, 20, 60, 120] 추가 가능
        for window in windows:
            data['mado_ma{}'.format(window)] = data['total_mado'].rolling(window).mean()
            data['masu_ma{}'.format(window)] = data['total_masu'].rolling(window).mean()

            data['mado_ma%d_ratio' % window] = (data['total_mado'] - data['mado_ma%d' % window]) / data[
                'mado_ma%d' % window]
            data['masu_ma%d_ratio' % window] = (data['total_masu'] - data['masu_ma%d' % window]) / data[
                'masu_ma%d' % window]

        data['mado_lastmado_ratio'] = np.zeros(len(data))
        data.loc[1:, 'mado_lastmado_ratio'] = (data.loc[1:, 'total_mado'].copy().values - data.loc[:len(data) - 2,
                                                                                          'total_mado'].copy().values) / data.loc[
                                                                                                                         :len(
                                                                                                                             data) - 2,
                                                                                                                         'total_mado'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
        data['masu_lastmasu_ratio'] = np.zeros(len(data))
        data.loc[1:, 'masu_lastmasu_ratio'] = (data.loc[1:, 'total_masu'].copy().values - data.loc[:len(data) - 2,
                                                                                          'total_masu'].copy().values) / data.loc[
                                                                                                                         :len(
                                                                                                                             data) - 2,
                                                                                                                         'total_masu'].copy().replace(
            to_replace=0, method='ffill').replace(to_replace=0, method='bfill').values
        data['mado_allrate'] = (data['total_mado'] / (data['total_mado'] + data['total_masu']))
        data['masu_allrate'] = (data['total_masu'] / (data['total_mado'] + data['total_masu']))
        for numa in range(10):
            i = numa + 1
            data['mado_%dw' % i] = (data['mado_%d' % i] / data['total_mado'])
        for numb in range(10):
            j = numb + 1
            data['masu_%dw' % j] = (data['masu_%d' % j] / data['total_masu'])
    if ver == 'hoga_t':
        gap = data['mado_price'][0] - data['masu_price'][0]
        if (gap <= 0):
            return None
        step = pow(10, int(math.log10(gap)))
        # 1. 호가 잔량 전체 비율
        tempmm = data[COLUMNS_CHART_DATA_MM]
        data['total_max'] = tempmm.max(axis=1)
        for numa in range(10):
            i = numa + 1
            data['mado_%dw' % i] = (data['mado_%d' % i] / data['total_max'])
        for numb in range(10):
            j = numb + 1
            data['masu_%dw' % j] = (data['masu_%d' % j] / data['total_max'])

        # 2. 주식 전체 매도 매수량
        data['mado_allrate'] = (data['total_mado'] / (data['total_mado'] + data['total_masu']))
        data['masu_allrate'] = (data['total_masu'] / (data['total_mado'] + data['total_masu']))

        # 3. 가격 이동평균, 격차
        windows = [5, 10]  # 이동평균선 5분짜리만 사용 필요하다면 windows = [5, 10, 20, 60, 120] 추가 가능
        for window in windows:
            data['mado_ma{}'.format(window)] = data['mado_price'].rolling(window).mean()
            data['masu_ma{}'.format(window)] = data['masu_price'].rolling(window).mean()
            data['mado_ma{}_sub'.format(window)] = (data['mado_ma{}'.format(window)] - data['mado_price']) / step
            data['mado_ma{}_last'.format(window)] = np.zeros(len(data))
            data.loc[1:, 'mado_ma{}_last'.format(window)] = \
                (data.loc[1:, 'mado_ma{}'.format(window)].copy().values -
                 data.loc[:len(data) - 2, 'mado_ma{}'.format(window)].copy().values) / step
        # 4. 출력 데이터
        data['next_5'] = np.zeros(len(data))
        data.loc[:len(data) - 5, 'next_5'] = \
            (data.loc[4:, 'mado_price'].copy().values -
             data.loc[:len(data) - 5, 'mado_price'].copy().values) / (step * 10)

    return data

def load_data(fpath, ver, start_time=None, end_time=None):
    if ver == 'c1':
        data = pd.read_csv(fpath, sep='\t', names=COLUMNS_CHART_DATA_C, header=None)
    if ver == 'f1':
        data = pd.read_csv(fpath, sep='\t', names=COLUMNS_CHART_DATA_N, header=None)
    if ver == 'a1':
        data = pd.read_csv(fpath, sep='\t', names=COLUMNS_CHART_DATA, header=None)
    if ver == 'u1':
        data = pd.read_csv(fpath, sep='\t', names=COLUMNS_CHART_DATA_U, header=None)
    if ver == 'x1':
        data = pd.read_csv(fpath, sep='\t', names=COLUMNS_CHART_DATA_X, header=None)
    if ver == 'z1':
        data = pd.read_csv(fpath, sep='\t', names=COLUMNS_CHART_DATA_Z, header=None)
    if ver == 'y1':
        data = pd.read_csv(fpath, sep='\t', names=COLUMNS_CHART_DATA_Y, header=None)
    if ver == 'y2':
        data = pd.read_csv(fpath, sep='\t', names=COLUMNS_CHART_DATA_Y, header=None)
    if ver == 'y3':
        data = pd.read_csv(fpath, sep='\t', names=COLUMNS_CHART_DATA_Y, header=None)
    if ver == 'z3':
        data = pd.read_csv(fpath, sep='\t', names=COLUMNS_CHART_DATA_Z3, header=None)
    if ver == 'dv':
        data = pd.read_csv(fpath, sep='\t', names=COLUMNS_CHART_DATA_D, header=None)
    if ver == 'h1':
        data = pd.read_csv(fpath, sep='\t', names=COLUMNS_CHART_DATA_H, header=None)
    if ver == 'h2':
        data = pd.read_csv(fpath, sep='\t', names=COLUMNS_CHART_DATA_H2, header=None)
    if ver == 'h3':
        data = pd.read_csv(fpath, sep='\t', names=COLUMNS_CHART_DATA_H2, header=None)
    if ver == 'ossp_all':
        data = pd.read_csv(fpath, sep='\t', names=COLUMNS_CHART_DATA_N, header=None)
    if ver == 'ossp_lstm':
        data = pd.read_csv(fpath, sep='\t', names=COLUMNS_CHART_DATA_N, header=None)
    if ver == 'test_h':
        data = pd.read_csv(fpath, sep='\t', names=COLUMNS_CHART_DATA_H, header=None)
    if ver == 'hoga_t':
        data = pd.read_csv(fpath, sep='\t', names=COLUMNS_CHART_DATA_H, header=None)
    data = data.sort_values(by='time')
    data.reset_index(drop=True, inplace=True)
    # 데이터 전처리
    data = preprocess(data, ver=ver)
    if data is None:
        return None, None

    # 기간 필터링 - 학습에 사용할 데이터 20190101090000 ~ 20191212153000 / 검증에 사용할 데이터
    #    data['date'] = data['date'].str.replace('-', '')
    # 필터링한 기간에 따른 index조절
    # 이렇게 하면 분봉조회로 가져온 데이터는 역순으로 담겨있기 때문에
    # 시간순으로 다시 재배치(크기순 배치)
    # 결측값 제거 - rolling(window)연산 시 window만큼의 행은 NaN으로 나타남(자동삭제 가능)
    if start_time is None and end_time is None:
        pass
    else:
        data = data[(data['time'] >= int(start_time)) & (data['time'] <= int(end_time))]
    data = data.dropna()

    # 차트 데이터 분리
    #chart_data = data[COLUMNS_CHART_DATA_L] #date 무의미
    # 신 차트 데이터 그냥 close만 있음
    if ver == 'h1':
        chart_data = data[COLUMNS_CHART_DATA_M]
    elif ver == 'h2':
        chart_data = data[COLUMNS_CHART_DATA_H2_1]
    elif ver == 'h3':
        chart_data = data[COLUMNS_CHART_DATA_H2_1]
    elif ver == 'ossp_all':
        #chart_data = data[COLUMNS_CHART_DATA_OSSP_ALL]
        chart_data = data[COLUMNS_CHART_DATA_N]
    elif ver == 'test_h':
        chart_data = data[COLUMNS_CHART_DATA_TEST_H]
    elif ver == 'hoga_t':
        chart_data = data[COLUMNS_CHART_DATA_M]
    else:
        chart_data = data[COLUMNS_CHART_DATA_K]
    # 학습 데이터 분리
    training_data = None
    if ver == 'v1':
        training_data = data[COLUMNS_TRAINING_DATA_V1]
    elif ver == 'v1.rich':
        training_data = data[COLUMNS_TRAINING_DATA_V1_RICH]
    elif ver == 'v2':
        data.loc[:, ['per', 'pbr', 'roe']] = data[['per', 'pbr', 'roe']].apply(lambda x: x / 100)
        training_data = data[COLUMNS_TRAINING_DATA_V2]
        training_data = training_data.apply(np.tanh)
    elif ver == 'a1':
        training_data = data[COLUMNS_TRAINING_DATA_A1]
    elif ver == 'f1':
        training_data = data[COLUMNS_TRAINING_DATA_F1]
    ######################
    elif ver == 'c1':
        training_data = data[COLUMNS_TRAINING_DATA_C1]
    elif ver == 'u1':
        training_data = data[COLUMNS_TRAINING_DATA_U1]
    elif ver == 'x1':
        training_data = data[COLUMNS_TRAINING_DATA_X1]
    elif ver == 'y1':
        training_data = data[COLUMNS_TRAINING_DATA_Y1]
    elif ver == 'y2':
        training_data = data[COLUMNS_TRAINING_DATA_Y2]
    elif ver == 'y3':
        training_data = data[COLUMNS_TRAINING_DATA_Y3]
    elif ver == 'z1':
        training_data = data[COLUMNS_TRAINING_DATA_Z1]
    elif ver == 'z3':
        training_data = data[COLUMNS_TRAINING_DATA_Z3]
    elif ver == 'dv':
        training_data = data[COLUMNS_TRAINING_DATA_DV]
    elif ver == 'h1':
        training_data = data[COLUMNS_TRAINING_DATA_H1]
    elif ver == 'h2':
        training_data = data[COLUMNS_TRAINING_DATA_H2]
    elif ver == 'h3':
        training_data = data[COLUMNS_TRAINING_DATA_H3]
    elif ver == 'ossp_all':
        training_data = data[COLUMNS_TRAINING_DATA_OSSP_ALL]
    ##################
    elif ver == 'ossp_lstm':
        pass
    elif ver == 'test_h':
        training_data = data[COLUMNS_TRAINING_DATA_H1]
    elif ver == 'hoga_t':
        training_data = data[COLUMNS_TRAINING_DATA_HT]
    else:
        raise Exception('Invalid version.')
    #print(chart_data)
    #print(training_data)

    if ver == 'ossp_lstm':
        chart_data = None
        training_data = None
        chart_data = data[COLUMNS_CHART_DATA_OSSP_ALL]
        training_data = data[COLUMNS_TRAINING_DATA_OSSP_ALL]
        training_data, chart_data = make_dataset(training_data, chart_data, 5)

    chart_data = chart_data.astype(np.float32)
    training_data = training_data.astype(np.float32)
    return chart_data, training_data

def calculating_law_data(fpath, savepath, suppath):
    data = pd.read_csv(fpath, sep='\t', names=COLUMNS_CHART_DATA_U, header=None)
    # 시간 순서대로 변형
    data = data.sort_values(by='time')
    data.reset_index(drop=True, inplace=True)
    data_list = data.values.tolist()
    calcul_data = []
    file = open(suppath, "r", encoding="utf8")
    sup_data_list = []
    lines = file.readlines()
    for line in lines:
        sup_data_list.append(line.strip())
    file.close()
    # sup_data_list[0] = 미입력 volume / sup_datalist[1] = 초기 매수량 / sup_datalist[2] 초기 매도량
    #print(sup_data_list)
    # a = 매수체결량 b = 매도체결량
    suma = 0
    sumb = 0
    count = 0
    # data_list[index][2] = 체결거래량(a + b) data_list[index][3] = 체결강도(a / b) * 100
    for semilist in data_list:
        if count == 0:
            curb = (semilist[2] - (float(sup_data_list[2]) * (semilist[3] / 100)) + float(sup_data_list[1]) - float(sup_data_list[0])) / (1 + semilist[3] / 100)
            cura = semilist[2] - curb - float(sup_data_list[0])
        else:
            curb = (suma + semilist[2] - (sumb * (semilist[3] / 100))) / (1 + semilist[3] / 100)
            cura = semilist[2] - curb
        temp_data = []
        temp_data.append(str(semilist[0]))
        temp_data.append(semilist[1])
        temp_data.append(cura)
        temp_data.append(curb)
        temp_data.append(semilist[3])
        calcul_data.append(temp_data.copy())
        suma += cura
        sumb += curb
        count += 1
    f = open(savepath, "w", encoding="utf8")
    for k in range(len(calcul_data)):
        f.write("%s\t%s\t%s\t%s\t%s\n" % (str(calcul_data[k][0]), str(calcul_data[k][1]), str(calcul_data[k][2]), str(calcul_data[k][3]), str(calcul_data[k][4])))
    f.close()

def seperate_code(fpath):
    file = open(fpath, "r", encoding="utf8")
    folderpath = "files/"
    onefile = open(folderpath + "bigvol.txt", "w", encoding="utf8")
    twofile = open(folderpath + "testvol.txt", "w", encoding="utf8")
    lines = file.readlines()
    count = 0
    for line in lines:
        if count % 2 == 0:
            onefile.write("%s\n" % (line.strip()))
        else:
            twofile.write("%s\n" % (line.strip()))
        count += 1
    file.close()
    onefile.close()
    twofile.close()

if __name__ == "__main__":
    #seperate_code("files/20200904.txt")
    chart_data, training_data = load_data("files/20210701/0901_002410.txt", ver='hoga_t')
    chart_data.reset_index(drop=True, inplace=True)
    chart_data.to_csv("files/testdata/chart_data_0901_002410.txt", sep='\t')
    training_data.reset_index(drop=True, inplace=True)
    training_data.to_csv("files/testdata/training_data_0901_002410.txt", sep='\t')
    # 이제 law_data를 한 폴더(날짜)에 모아놓고, 이름을 '131370.txt'로 지정
    # 이때 각 날짜별로 'bigvol.txt'의 파일로  당일거래대금 기준 상위 20개의 종목코드를 저장해놓음
    # today_date = "20200827"
    # fpath = "files/" + today_date + "/bigvol.txt"
    # file = open(fpath, "r", encoding="utf8")
    # code_list = []
    # lines = file.readlines()
    # for line in lines:
    #     code_list.append(line.strip())
    # file.close()
    # for code in code_list:
    #     lpath = "files/" + today_date + "/" + code + ".txt"
    #     #converting_law_text_data(lpath)
    #     load_data(lpath, 'u1')

    # today_date = "20200902"
    # fpath = "files/" + today_date + "/bigvol.txt"
    # file = open(fpath, "r", encoding="utf8")
    # code_list = []
    # lines = file.readlines()
    # for line in lines:
    #     code_list.append(line.strip())
    # file.close()
    # for code in code_list:
    #     lpath = "files/" + today_date + "/" + code + ".txt"
    #     savepath = "files/" + today_date + "/" + code + "_z.txt"
    #     suppath = "files/" + today_date + "/sup_data/" + code + ".txt"
    #     calculating_law_data(fpath=lpath, savepath=savepath, suppath=suppath)
    #     #load_data(lpath, 'u1')