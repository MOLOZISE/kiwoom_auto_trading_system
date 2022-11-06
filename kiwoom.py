import os
import sys
import datetime as dt
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from PyQt5.QtTest import *
from config.kiwoomType import *
from config.log_class import *
from config.slack import *
import copy
import pandas as pd
import config.settings
import config.data_manager
import math
import numpy as np

import random

def softmax(a):
    exp_a = np.exp(a)
    sum_exp_a = np.sum(exp_a)
    y = exp_a / sum_exp_a

    return y

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

COLUMNS_CHART_DATA = [
    'next_5'
]

COLUMNS_TRAIN_DATA = [
    'mado_1w', 'mado_2w', 'mado_3w', 'mado_4w', 'mado_5w',
    'mado_6w', 'mado_7w', 'mado_8w', 'mado_9w', 'mado_10w',
    'masu_1w', 'masu_2w', 'masu_3w', 'masu_4w', 'masu_5w',
    'masu_6w', 'masu_7w', 'masu_8w', 'masu_9w', 'masu_10w',
    'mado_allrate', 'masu_allrate',
    'mado_ma5_sub', 'mado_ma10_sub',
    'mado_ma5_last', 'mado_ma10_last'
]

COLUMNS_CHART_DATA_H2 = ['stock_code', 'time', 'mado_price', 'masu_price', 'total_mado', 'total_masu',
                        'mado_1', 'mado_2', 'mado_3', 'mado_4', 'mado_5', 'mado_6', 'mado_7', 'mado_8', 'mado_9', 'mado_10',
                        'masu_1', 'masu_2', 'masu_3', 'masu_4', 'masu_5', 'masu_6', 'masu_7', 'masu_8', 'masu_9', 'masu_10',
                         '5_next_price']

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        self.realType = RealType()
        self.logging = Logging()

        self.logging.logger.debug("Kiwoom() class start.")

        ##### event loop를 실행하기 위한 변수 모음
        self.login_event_loop = QEventLoop() # 로그인 요청용 이벤트 루프
        self.detail_account_info_event_loop = QEventLoop() # 예수금 요청용 이벤트루프
        self.calculator_event_loop = QEventLoop() # 종목 데이터 수집용 이벤트 루프

        ########### 전체 종목 관리
        self.all_stock_dict = {}

        ####### 계좌 관련된 변수
        self.account_stock_dict = {}
        self.not_account_stock_dict = {}
        self.account_num = 00000000 #계좌번호 변수
        self.deposit = 0  # 예수금
        self.use_money = 0  # 실제 투자에 사용할 금액

        self.use_money_percent = 0.5  # 예수금에서 실제 사용할 비율
        self.output_deposit = 0  # 출력가능 금액
        self.total_profit_loss_money = 0  # 총평가손익금액
        self.total_profit_loss_rate = 0.0  # 총수익률(%)
        ########################################

        ######## 종목 정보 가져오기
        self.portfolio_stock_dict = {}
        self.jango_dict = {}

        ########### 종목 분석 용
        self.calcul_data = []
        self.code = None
        self.enormous_code_list = []
        self.temp_30min_data = []
        self.input_data = []
        self.temp_enormous_code_dict = {}

        ########## 호가 매매
        self.ten_cal_data = []
        self.ten_cal_dict = {}

        ######## 매매
        self.cal_30_dict = {}

        ####### 요청 스크린 번호
        self.screen_my_info = "2000"  # 계좌 관련한 스크린 번호
        self.screen_calculation_stock = "4000"  # 계산용 스크린 번호
        self.screen_real_stock = "5000"  # 종목별 할당할 스크린 번호
        self.screen_meme_stock = "6000"  # 종목별 할당할 주문용스크린 번호
        self.screen_start_stop_real = "1000"  # 장 시작/종료 실시간 스크린번호
        ######################################## 새로운 추가
        self.screen_invest_stock = "7000" # 당일 거래량 상위 50 종목 코드들 스크린 번호
        self.screen_invest_meme_stock = "8000" # 당일 거래량 상위 50 종목 코드들 주문용스크린 번호
        self.invest_dict = {} # 종목코드 + 투자 금액 + 포트폴리오 가치 + 주식 수 등 저장

        ############ 초기 세팅 함수들 바로 실행 (필수)
        self.get_ocx_instance() # OCX 방식을 파이썬에 사용할 수 있게 반환해 주는 함수 실행
        self.event_slots() # 키움과 연결하기 위한 시그널 / 슬롯 모음
        self.real_event_slot()  # 실시간 이벤트 시그널 / 슬롯 연결
        
        self.signal_login_commConnect() # 로그인
        self.get_account_info() # 로그인 후 키움 객체에 계좌번호 저장

        self.detail_account_info()  # 예수금상세현황요청 / 사용할 돈 분배 (use_money)
        self.detail_account_mystock()  # 계좌평가잔고내역 / 총매입금액, 총평가손익금액, 총수익률 출력 / 가진 종목들을 account_stock_dict 사전에 저장
        QTimer.singleShot(5000, self.not_concluded_account)  # 5초 뒤에 미체결 종목들 가져오기 실행 / 실시간미체결내역요청 / 미체결 종목들을 not_account_stock_dict 사전에 저장
        QTest.qWait(10000)
        self.logging.logger.debug("미체결 후 screen_number_setting")
        #self.read_code() #포트폴리오의 종목을 미리 받기 위해서(즉 안해도 됨)
        #self.screen_number_setting() #계좌평가잔고내역(detail_account_mystock()), 미체결내역(not_concluded_account), 포트폴리오내역(read.code())들에게 스크린번호 + 주문번호 부여
        self.dynamicCall("DisconnectRealData(QString)", "3000")
        self.dynamicCall("DisconnectRealData(QString)", "3001")
        self.dynamicCall("DisconnectRealData(QString)", "3002")
        self.dynamicCall("DisconnectRealData(QString)", "3003")
        self.dynamicCall("DisconnectRealData(QString)", "6000")
        QTest.qWait(5000)
        ################# 실시간 수신 관련 함수
        # 현재 장시간인지 확인 - 3시 30분 장 종료 외에는 로깅만 됨
        # 3시 30분 이후에 구동 시 SetRealReg가 안 먹는듯??
        # 3시 30분 장 종료 시 -> 4초후 전일거래량상위요청 ->

        # self.logging.logger.debug("실시간 수신 dynamicCall 시작")
        # self.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen_start_stop_real, '', self.realType.REALTYPE['장시작시간']['장운영구분'], "0")
        # self.logging.logger.debug("실시간 수신 dynamicCall 완료")

        ############# 일시적으로 쓰는 코드 주식분봉조회요청
        # self.logging.logger.debug("datacollect_fnc 시작")
        #self.datacollect_fnc()
        #self.logging.logger.debug("datacollect_fnc 완료")

        # 포트폴리오 주식 사전의 종목 코드들을 실시간 정보 데이터를 받음
        # for code in self.portfolio_stock_dict.keys():
        #     screen_num = self.portfolio_stock_dict[code]['스크린번호']
        #     fids = self.realType.REALTYPE['주식체결']['체결시간']
        #     self.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen_num, code, fids, "1")

        # invest_dict의 종목 코드들 선정
        #self.logging.logger.debug("오늘의 당일거래량순위 50 받고 저장")
        #self.get_today_stock_kiwoom_db()

        ##### 15:00 주식장이 끝나고 당일 거래량 50위의 5분봉을 당일 날짜의 090000 ~ 150000까지 받음
        ############# 일시적으로 쓰는 코드 전일거래량상위요청 -> 완료
        #self.logging.logger.debug("get_hot_stock_kiwoom_db 시작")
        #self.get_hot_stock_kiwoom_db()
        # self.logging.logger.debug("get_hot_stock_kiwoom_db 완료")

        # 기존의 방식(주석처리) = 선정한 종목코드 20개에 대하여 일정 기간 동안의 데이터를 수집 후 학습
        # 개선된 방식에서 get_code_list를 변형하였으므로 사용불가
        # self.start_date = "20200601"
        self.end_date = "20211103" # 오늘날짜(정확히는 전일 날짜나 등..)
        self.cur_date = self.end_date   # 5분봉을 날짜별로 가져올 때 현재 얼만큼 가져왔는 지 가늠할 수 있도록
        self.collect_cur_date = self.end_date
        ############ 당일거래량상위요청
        self.logging.logger.debug("get_today_stock_kiwoom_db 시작")

        #self.porjdatacollect_fnc()
        #exit(0)

        ######### 전일거래량상위요청
        #self.get_hot_stock_kiwoom_db()
        #self.datacollectplus_day()
        #self.datacollectplus_new_data_day()
        #self.datacollectplus_upgrade()
        #self.datacollectplus_fnc()
        #self.supdatacollect()
        # 11월 24일 데이터 수집하기


        # self.get_today_stock_code_db()
        # self.logging.logger.debug("20개 종목 선정 종료")
        # #
        # # invest_dict의 종목 코드들에게 스크린 번호 지정
        # self.logging.logger.debug("스크린 넘버 세팅")
        # self.today_screen_number_setting()

        # # invest_dict의 종목 코드들도 실시간 정보 데이터를 받음
        # for code in self.invest_dict.keys():
        #     screen_num = self.invest_dict[code]['스크린번호']
        #     fids = self.realType.REALTYPE['주식체결']['체결시간']
        #     self.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen_num, code, fids, "1")

        #
        ## 5분 -> 10분으로 느긋... -> 1분으로 빠르게
        # while(flag):
        #     nowh = datetime.now().today().hour
        #     nowm = datetime.now().today().minute
        #     if nowh >= 15:
        #         # 15시가 되면 오늘의 모든 것들을 판매함
        #         #self.lastorder()
        #         flag = False
        #     elif nowh < 9:
        #         QTest.qWait(1000)
        #     # 다르다라는 것은 시간이 바뀌었다는 뜻
        #     elif iffirst: # 초기 한정 한번만 해줌
        #         before_h = nowh
        #         before_m = nowm
        #         self.get_5min_data()
        #         iffirst = False
        #     elif before_h != nowh:
        #         if (before_m + 1) - 60 == nowm:
        #             before_h = nowh
        #             before_m = nowm
        #             self.get_5min_data()
        #         else:
        #             QTest.qWait(1000)
        #     elif nowm - before_m == 1:
        #         before_h = nowh
        #         before_m = nowm
        #         self.get_5min_data()
        #     else:
        #         #self.logging.logger.debug("1초 기다리기")
        #         QTest.qWait(1000)

        # code_list = self.get_code_list_by_mytxt()  # 1202 파일에 1 ~ 20 위 선정함
        # self.logging.logger.debug("txt 종목 갯수 %s " % len(code_list))
        flag = True
        before_m = -5 # 무조건 -5부터 시작해야함
        before_h = 9 # 무조건 9시부터 시작해야함
        before_m_30 = -5  # 무조건 -5부터 시작해야함
        before_h_30 = 9  # 무조건 9시부터 시작해야함
        iffirst = True
        self.ordercount = 0
        self.totalorder = 0
        while (flag):
            nowh = datetime.now().today().hour
            nowm = datetime.now().today().minute
            if nowh <= 9:
                nowhstr = "0" + str(nowh)
            else:
                nowhstr = str(nowh)
            if nowm <= 9:
                nowmstr = "0" + str(nowm)
            else:
                nowmstr = str(nowm)
            self.cur_time = nowhstr + nowmstr
            if nowh >= 15:
                # 15시가 되면 오늘의 모든 것들을 판매
                flag = False
                for code in self.cal_30_dict.keys():
                    if (self.cal_30_dict[code]['주식개수'] != 0):
                        order_success = self.dynamicCall(
                            "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                            ["신규매도", self.cal_30_dict[code]['주문용스크린번호'], self.account_num, 2, code,
                             int(self.cal_30_dict[code]['주식개수']), "",
                             self.realType.SENDTYPE['거래구분']['시장가'], ""])
                        if order_success == 0:
                            self.logging.logger.debug("매도주문 전달 성공")
                            self.cal_30_dict[code]['주식개수'] -= int(self.cal_30_dict[code]['주식개수'])
                        else:
                            self.logging.logger.debug("매도주문 전달 실패")
            elif nowh < 9:
                QTest.qWait(1000)
            # 다르다라는 것은 시간이 바뀌었다는 뜻
            elif iffirst:  # 초기 한정 한번만 해줌
                before_h = nowh
                before_m = nowm
                before_h_30 = nowh
                before_m_30 = nowm
                # 거래량 급증 + 여러 조건 상위 10개 종목 코드
                self.get_enormous_code()
                self.torch_get_data_and_analysis()
                iffirst = False
            elif before_h_30 != nowh:
                if (before_m_30 + 30) - 60 == nowm:
                    before_h_30 = nowh
                    before_m_30 = nowm
                    # 거래량 급증 + 여러 조건 상위 10개 종목 코드
                    self.get_enormous_code()
                else:
                    QTest.qWait(1000)
            elif nowm - before_m_30 == 30:
                before_h_30 = nowh
                before_m_30 = nowm
                # 거래량 급증 + 여러 조건 상위 10개 종목 코드
                self.get_enormous_code()
            else:
                QTest.qWait(1000)
            if before_h != nowh:
                if (before_m + 5) - 60 == nowm:
                    before_h = nowh
                    before_m = nowm
                    ####################
                    self.torch_get_data_and_analysis()
                else:
                    QTest.qWait(1000)
            elif nowm - before_m == 5:
                before_h = nowh
                before_m = nowm
                ###########
                self.torch_get_data_and_analysis()
            else:
                QTest.qWait(1000)

        # while(flag):
        #     nowh = datetime.now().today().hour
        #     nowm = datetime.now().today().minute
        #     if nowh >= 15:
        #         # 15시가 되면 오늘의 모든 것들을 판매함
        #         #self.lastorder()
        #         flag = False
        #     elif nowh < 9:
        #         QTest.qWait(1000)
        #     # 다르다라는 것은 시간이 바뀌었다는 뜻
        #     elif iffirst: # 초기 한정 한번만 해줌
        #         before_h = nowh
        #         before_m = nowm
        #         self.get_5min_data()
        #         iffirst = False
        #     elif before_h != nowh:
        #         if (before_m + 1) - 60 == nowm:
        #             before_h = nowh
        #             before_m = nowm
        #             self.get_5min_data()
        #         else:
        #             QTest.qWait(1000)
        #     elif nowm - before_m == 1:
        #         before_h = nowh
        #         before_m = nowm
        #         self.get_5min_data()
        #     else:
        #         #self.logging.logger.debug("1초 기다리기")
        #         QTest.qWait(1000)

        # #데이터 수집기 #
        #### 신경망 파라미터 불러오기
        # self.weights = []
        # self.biaseds = []
        # temp_bundle_list = []
        # fpath = "kiwoom/modelparameterxxt.txt"
        # file = open(fpath, 'r', encoding='utf8')
        # lines = file.readlines()
        # temp_list = []
        # count = 1
        # last_count = 0
        # # print(len(lines))
        # for line in lines:  # line 0900 종목 코드 10개
        #     ls = line.split("\t")
        #     for item in ls:
        #         if (item == "\n"):
        #             continue
        #         temp_list.append(item)
        #     if (count >= 259):  # last
        #         if (last_count == 31):
        #             self.weights.append(temp_list.copy())
        #             temp_list.clear()
        #         if (last_count == 32):
        #             self.biaseds.append(temp_list.copy())
        #         last_count = last_count + 1
        #         continue
        #     if (count <= 26 or (((count - 27) >= 1) and ((count - 27) % 33 != 0))):
        #         temp_bundle_list.append(temp_list.copy())
        #     else:
        #         self.weights.append(temp_bundle_list.copy())
        #         self.biaseds.append(temp_list.copy())
        #         temp_bundle_list.clear()
        #     temp_list.clear()
        #     count = count + 1

        #### 신경망 파라미터 불러오기
        # self.weights = []
        # self.biaseds = []
        # temp_bundle_list = []
        # fpath = "kiwoom/paramst.txt"
        # file = open(fpath, 'r', encoding='utf8')
        # lines = file.readlines()
        # temp_list = []
        # count = 1
        # last_count = 0
        # # print(len(lines))
        # for line in lines:  # line 0900 종목 코드 10개
        #     ls = line.split("\t")
        #     for item in ls:
        #         if (item == "\n"):
        #             continue
        #         # temp_list 첫번째 줄
        #         temp_list.append(item)
        #     temp_bundle_list.append(temp_list.copy())
        #     if (count == 514):
        #         self.weights.append(temp_bundle_list.copy())
        #         temp_bundle_list.clear()
        #     elif (count == 516):
        #         self.biaseds.append(temp_bundle_list.copy())
        #         temp_bundle_list.clear()
        #     elif (count == 517):
        #         pass
        #         # weights.append(temp_bundle_list.copy())
        #         # temp_bundle_list.clear()
        #     elif (count == 518):
        #         pass
        #         # biaseds.append(temp_bundle_list.copy())
        #         # temp_bundle_list.clear()
        #     if (count % 64 == 0) and ((count / 64) % 2 == 1):  # layer weight
        #         self.weights.append(temp_bundle_list.copy())
        #         temp_bundle_list.clear()
        #     elif (count % 64 == 0) and ((count / 64) % 2 == 0):  # layer biased
        #         self.biaseds.append(temp_bundle_list.copy())
        #         temp_bundle_list.clear()
        #     temp_list.clear()
        #     count = count + 1
        #
        # self.logging.logger.debug("데이터 수집 시작 전")
        # flag = True
        # before_m = -5 # 무조건 -5부터 시작해야함
        # before_h = 9 # 무조건 9시부터 시작해야함
        # before_m_30 = -5  # 무조건 -5부터 시작해야함
        # before_h_30 = 9  # 무조건 9시부터 시작해야함
        # iffirst = True
        # self.ordercount = 0
        # self.totalorder = 0

        #self.datacollect_fnc()
        ## 5분 -> 10분으로 느긋... -> 1분으로 빠르게
        # while(flag):
        #     nowh = datetime.now().today().hour
        #     nowm = datetime.now().today().minute
        #     if nowh >= 15:
        #         # 15시가 되면 오늘의 모든 것들을 판매함
        #         #self.lastorder()
        #         flag = False
        #     elif nowh < 9:
        #         QTest.qWait(1000)
        #     # 다르다라는 것은 시간이 바뀌었다는 뜻
        #     elif iffirst: # 초기 한정 한번만 해줌
        #         before_h = nowh
        #         before_m = nowm
        #         self.get_5min_data()
        #         iffirst = False
        #     elif before_h != nowh:
        #         if (before_m + 1) - 60 == nowm:
        #             before_h = nowh
        #             before_m = nowm
        #             self.get_5min_data()
        #         else:
        #             QTest.qWait(1000)
        #     elif nowm - before_m == 1:
        #         before_h = nowh
        #         before_m = nowm
        #         self.get_5min_data()
        #     else:
        #         #self.logging.logger.debug("1초 기다리기")
        #         QTest.qWait(1000)


        ######################################## 실시간 호가잔량
        # 3/17에는 시험용으로 정적인 종목코드 10개 정도로 해보기 -> 시간 등 여러 문제도 충분히 가능하다고 생각
        # 3/18 시험이 잘되면 동적인 종목코드로 해보기
        # 종목들을 txt파일로 저장해야 함 그래야 나중에 각 txt파일로 접근 가능

        # test_code_list = ["005930", "051910", "122630", "950220", "036630", "041190", "000660", "096770", "096040", "252670"]
        # tempint = 0
        # for code in test_code_list:
        #     tempscreencode = "100" + str(tempint)
        #     self.dynamicCall("SetRealReg(QString, QString, QString, QString)", tempscreencode, code, "41", "0")
        #     tempint = tempint + 1

        #self.cur_time = ""
        # # 090000 ~ 150000
        # ############## 데이터 수집기 while문
        ## 2021 07 20 이전 하던대로
        # while(flag):
        #     nowh = datetime.now().today().hour
        #     nowm = datetime.now().today().minute
        #     if nowh <= 9:
        #         nowhstr = "0" + str(nowh)
        #     else:
        #         nowhstr = str(nowh)
        #     if nowm <= 9:
        #         nowmstr = "0" + str(nowm)
        #     else:
        #         nowmstr = str(nowm)
        #     self.cur_time = nowhstr + nowmstr
        #     if nowh >= 15:
        #         # 15시가 되면 오늘의 모든 것들을 판매함
        #         self.lastorder()
        #         flag = False
        #         for i in range(10):
        #             tempscreencode = "100" + str(i)
        #             self.dynamicCall("DisconnectRealData(QString)", tempscreencode)
        #         self.enormous_code_list.clear()
        #     elif nowh < 9:
        #         QTest.qWait(1000)
        #     # 다르다라는 것은 시간이 바뀌었다는 뜻
        #     elif iffirst: # 초기 한정 한번만 해줌
        #         before_h = nowh
        #         before_m = nowm
        #         # self.get_5min_data()
        #         self.connectanddisconnecting()
        #         iffirst = False
        #     elif before_h != nowh:
        #         if (before_m + 1) - 60 == nowm:
        #             before_h = nowh
        #             before_m = nowm
        #             #self.get_5min_data()
        #             self.connectanddisconnecting()
        #         else:
        #             QTest.qWait(1000)
        #     elif nowm - before_m == 1:
        #         before_h = nowh
        #         before_m = nowm
        #         #self.get_5min_data()
        #         self.connectanddisconnecting()
        #     else:
        #         #self.logging.logger.debug("1초 기다리기")
        #         QTest.qWait(1000)

        ############ 2021 0827 데이터 분석을 위한 변형

        # flag = True
        # before_m = -5  # 무조건 -5부터 시작해야함
        # before_h = 9  # 무조건 9시부터 시작해야함
        # iffirst = True
        # update_minute = 10
        # while (flag):
        #     nowh = datetime.now().today().hour
        #     nowm = datetime.now().today().minute
        #     if nowh <= 9:
        #         nowhstr = "0" + str(nowh)
        #     else:
        #         nowhstr = str(nowh)
        #     if nowm <= 9:
        #         nowmstr = "0" + str(nowm)
        #     else:
        #         nowmstr = str(nowm)
        #     self.cur_time = nowhstr + nowmstr
        #     if nowh >= 15:
        #         # 15시가 되면 오늘의 모든 것들을 판매함
        #         #self.lastorder()
        #         flag = False
        #         for i in range(10):
        #             tempscreencode = "100" + str(i)
        #             self.dynamicCall("DisconnectRealData(QString)", tempscreencode)
        #         self.enormous_code_list.clear()
        #     elif nowh < 9:
        #         QTest.qWait(1000)
        #     # 다르다라는 것은 시간이 바뀌었다는 뜻
        #     elif iffirst:  # 초기 한정 한번만 해줌
        #         before_h = nowh
        #         before_m = nowm
        #         # self.get_5min_data()
        #         self.connectanddisconnecting()
        #         iffirst = False
        #     elif before_h != nowh:
        #         if (before_m + update_minute) - 60 == nowm:
        #             before_h = nowh
        #             before_m = nowm
        #             # self.get_5min_data()
        #             self.connectanddisconnecting()
        #         else:
        #             QTest.qWait(1000)
        #     elif nowm - before_m == update_minute:
        #         before_h = nowh
        #         before_m = nowm
        #         # self.get_5min_data()
        #         self.connectanddisconnecting()
        #     else:
        #         # self.logging.logger.debug("1초 기다리기")
        #         QTest.qWait(1000)

        #2021 10 30 추가본
        ### 거래량 급증 상위 10개를 계속 추가해가면서 관리함
        # while (flag):
        #     nowh = datetime.now().today().hour
        #     nowm = datetime.now().today().minute
        #     if nowh <= 9:
        #         nowhstr = "0" + str(nowh)
        #     else:
        #         nowhstr = str(nowh)
        #     if nowm <= 9:
        #         nowmstr = "0" + str(nowm)
        #     else:
        #         nowmstr = str(nowm)
        #     self.cur_time = nowhstr + nowmstr
        #     if nowh >= 15:
        #         # 15시가 되면 오늘의 모든 것들을 판매함
        #         # self.lastorder()
        #         flag = False
        #         # for idx, code in enumerate(self.enormous_code_list):
        #         #     tempscreencode = "300" + str(idx)
        #         #     self.dynamicCall("DisconnectRealData(QString)", tempscreencode)
        #         self.enormous_code_list.clear()
        #     elif nowh < 9:
        #         QTest.qWait(1000)
        #     # 다르다라는 것은 시간이 바뀌었다는 뜻
        #     elif iffirst:  # 초기 한정 한번만 해줌
        #         before_h = nowh
        #         before_m = nowm
        #         before_h_30 = nowh
        #         before_m_30 = nowm
        #         # 거래량 급증 + 여러 조건 상위 10개 종목 코드
        #         self.get_enormous_code()
        #         iffirst = False
        #     elif before_h_30 != nowh:
        #         if (before_m_30 + 30) - 60 == nowm:
        #             before_h_30 = nowh
        #             before_m_30 = nowm
        #             # 거래량 급증 + 여러 조건 상위 10개 종목 코드
        #             self.get_enormous_code()
        #         else:
        #             QTest.qWait(1000)
        #     elif nowm - before_m_30 == 30:
        #
        #         before_h_30 = nowh
        #         before_m_30 = nowm
        #         # 거래량 급증 + 여러 조건 상위 10개 종목 코드
        #         self.get_enormous_code()
        #     else:
        #         QTest.qWait(1000)
        #     if before_h != nowh:
        #         if (before_m + 1) - 60 == nowm:
        #             before_h = nowh
        #             before_m = nowm
        #             folderpath = "files/" + self.cur_date
        #             if not os.path.isdir(folderpath):
        #                 os.mkdir(folderpath)
        #             filepath = folderpath + "/" + self.cur_date + ".txt"
        #             f = open(filepath, "a", encoding="utf8")
        #             f.write("%s\t" % (str(self.cur_time)))
        #             for code in (self.enormous_code_list):
        #                 f.write("%s\t" % (str(code)))
        #             f.write("\n")
        #             f.close()
        #             # 종목 코드 별 수집 및 판단
        #             self.get_data_and_analysis()
        #         else:
        #             QTest.qWait(1000)
        #     elif nowm - before_m == 1:
        #         before_h = nowh
        #         before_m = nowm
        #         # self.get_5min_data()
        #         #self.volume_accu()
        #         folderpath = "files/" + self.cur_date
        #         if not os.path.isdir(folderpath):
        #             os.mkdir(folderpath)
        #         filepath = folderpath + "/" + self.cur_date + ".txt"
        #         f = open(filepath, "a", encoding="utf8")
        #         f.write("%s\t" % (str(self.cur_time)))
        #         for code in (self.enormous_code_list):
        #             f.write("%s\t" % (str(code)))
        #         f.write("\n")
        #         f.close()
        #         # 종목 코드 별 수집 및 판단
        #         self.get_data_and_analysis()
        #     else:
        #         QTest.qWait(1000)

        ### 거래량 급증 상위 10개를 계속 추가해가면서 관리함
        #### 호가잔량
        # self.temp_len_code = 0
        # while (flag):
        #     nowh = datetime.now().today().hour
        #     nowm = datetime.now().today().minute
        #     if nowh <= 9:
        #         nowhstr = "0" + str(nowh)
        #     else:
        #         nowhstr = str(nowh)
        #     if nowm <= 9:
        #         nowmstr = "0" + str(nowm)
        #     else:
        #         nowmstr = str(nowm)
        #     self.cur_time = nowhstr + nowmstr
        #     if nowh >= 15:
        #         # 15시가 되면 오늘의 모든 것들을 판매함
        #         self.lastorder()
        #         flag = False
        #         # for idx, code in enumerate(self.enormous_code_list):
        #         #     tempscreencode = "300" + str(idx)
        #         #     self.dynamicCall("DisconnectRealData(QString)", tempscreencode)
        #         self.ten_cal_dict.clear()
        #         self.enormous_code_list.clear()
        #     elif nowh < 9:
        #         QTest.qWait(1000)
        #     # 다르다라는 것은 시간이 바뀌었다는 뜻
        #     elif iffirst:  # 초기 한정 한번만 해줌
        #         before_h = nowh
        #         before_m = nowm
        #         before_h_30 = nowh
        #         before_m_30 = nowm
        #         # self.get_5min_data()
        #         self.volume_accu()
        #         iffirst = False
        #     elif before_h_30 != nowh:
        #         if (before_m_30 + 10) - 10 == nowm:
        #             # before_h = nowh
        #             # before_m = nowm
        #             before_h_30 = nowh
        #             before_m_30 = nowm
        #             # self.get_5min_data()
        #             self.volume_accu()
        #         else:
        #             QTest.qWait(1000)
        #     elif nowm - before_m_30 == 10:
        #         # before_h = nowh
        #         # before_m = nowm
        #         before_h_30 = nowh
        #         before_m_30 = nowm
        #         # self.get_5min_data()
        #         self.volume_accu()
        #     else:
        #         # self.logging.logger.debug("1초 기다리기")
        #         QTest.qWait(1000)
        #     if before_h != nowh:
        #         if (before_m + 1) - 60 == nowm:
        #             before_h = nowh
        #             before_m = nowm
        #             # self.get_5min_data()
        #             # self.volume_accu()
        #             folderpath = "files/" + self.cur_date
        #             if not os.path.isdir(folderpath):
        #                 os.mkdir(folderpath)
        #             filepath = folderpath + "/" + self.cur_date + ".txt"
        #             f = open(filepath, "a", encoding="utf8")
        #             f.write("%s\t" % (str(self.cur_time)))
        #             for code in (self.enormous_code_list):
        #                 f.write("%s\t" % (str(code)))
        #             f.write("\n")
        #             f.close()
        #         else:
        #             QTest.qWait(1000)
        #     elif nowm - before_m == 1:
        #         before_h = nowh
        #         before_m = nowm
        #         # self.get_5min_data()
        #         #self.volume_accu()
        #         folderpath = "files/" + self.cur_date
        #         if not os.path.isdir(folderpath):
        #             os.mkdir(folderpath)
        #         filepath = folderpath + "/" + self.cur_date + ".txt"
        #         f = open(filepath, "a", encoding="utf8")
        #         f.write("%s\t" % (str(self.cur_time)))
        #         for code in (self.enormous_code_list):
        #             f.write("%s\t" % (str(code)))
        #         f.write("\n")
        #         f.close()
        #     else:
        #         QTest.qWait(1000)

        #### 데이터 수집 문제의 요인
        # 1. 상위 n위의 개수 정하기
        # 2. m분 전과 비교
        # 1분일 때는 상위 7개 이므로 유효할 수 있음 -> 분석에서 1 ~ 20위 중 7위까지만으로 직접확인
        # 1분 전과 비교, 3분 전과 비교가 유효한 차이를 벌릴 수도 있음 -> 직접해봐야 암
        # 1/25에는 1분 7개 1분전과 비교
        # 1/26에는 1분 7개 3분전과 비교
        # 1/27에는 3분 20개 1분전과 비교
        # 1/28에는 3분 20개 3분전과 비교
        # 1/29에는 5분 30개 1분전과 비교
        # 2/1에는 1분 7개 5분전과 비교
        # 2/2에는 1분 7개 전일과 비교
        # 2/3에는 3분 20개 전일과 비교
        # 2/4에는 5분 30개 전일과 비교
        # 2/9에는 3분 20개 전일과 비교
        # 2/10에는 5분 30개 전일과 비교
        # 2/15 1분 7개 1분전 순매수잔량순 상위
        # 2/16 1분 7개 1분전 순매도잔량순 상위 14
        # 2/17 1분 7개 1분전 거래량 급증 14 5분 0.6의 효과
        # 2/18 3분 20개 3분전 거래량 급증 14
        # 2/19 1분 7개 1분전 거래량 급증 14 + 가격 5천원이상
        # 2/22 1분 7개 1분전 거래량 급증 14 코스피+코스닥
        # 2/23 3분마다 20개 1분전 거래량 급증 14 코스피+코스닥
        # 2/24 1분 7개 1분전 거래량 급증 14 코스피+코스닥
        # 2/25 3분마다 20개 1분전 거래량 급증 14 코스피+코스닥
        # 2/24 1분 7개 1분전 거래량 급증 14 코스피+코스닥
        # 3/2 1분 7개 1분전 거래량 급증 14 코스피+코스닥
        # 3/3 # 3/2 1분 7개 1분전 거래량 급증 14 코스피+코스닥 ~~~

        ########################################### 현재까지 얻어낸 데이터들로
        # start_date = "20210316"
        # end_date = "20210316"
        # d1 = dt.date(int(start_date[0:4]), int(start_date[4:6]), int(start_date[6:8]))
        # d2 = dt.date(int(end_date[0:4]), int(end_date[4:6]), int(end_date[6:8]))
        # delta = d2 - d1
        # self.text_dict = {}
        # self.target_date = ""
        # self.minute_gap = 5
        # self.current_time = ""
        # for i in range(delta.days + 1):
        #     target_date = str(d1 + dt.timedelta(days=i)).replace('-', '')
        #     test_date = os.path.join('files/{}/{}.txt'.format("dnn_data", target_date))
        #     if not os.path.isfile(test_date):
        #         continue
        #     self.target_date = target_date
        #     self.load_data(test_date=test_date) #### 텍스트 파일 가져와서, 딕셔너리에 넣음
        #     self.get_end_data(target_date=target_date) #### 위 텍스트 파일로부터 추출한 딕셔너리 종목의 test_date 날짜의 15:00 가격을 가져와서 딕셔너리에 저장
        #     self.save_data(test_date=test_date, target_date=target_date) #### 작업 종료 후 다시 딕셔너리에 넣었던 순서대로 + n분 후 데이터 대신 15시의 가격을 넣음
        #     self.text_dict.clear()
        # 첫번째 현재 선택할 종목들 리스트로 받기
        # enormous_code_list에 get_5min_datalist()에서 얻어낸 종목 15개가 들어감
        # 현재 있는 "관리" 종목 사전에 있는 데이터들 완성 시키기
        # 5분마다 반복get_5min_data()

        ### 시간이 1분이 지나있을 수 있음
        # self.temp_len_code = 0
        # while (flag):
        #     nowh = datetime.now().today().hour
        #     nowm = datetime.now().today().minute
        #     if nowh <= 9:
        #         nowhstr = "0" + str(nowh)
        #     else:
        #         nowhstr = str(nowh)
        #     if nowm <= 9:
        #         nowmstr = "0" + str(nowm)
        #     else:
        #         nowmstr = str(nowm)
        #     self.cur_time = nowhstr + nowmstr
        #     if nowh >= 15:
        #         # 15시가 되면 오늘의 모든 것들을 판매함
        #         self.lastorder()
        #         flag = False
        #         # for idx, code in enumerate(self.enormous_code_list):
        #         #     tempscreencode = "300" + str(idx)
        #         #     self.dynamicCall("DisconnectRealData(QString)", tempscreencode)
        #         self.ten_cal_dict.clear()
        #         self.enormous_code_list.clear()
        #     elif nowh < 9:
        #         QTest.qWait(1000)
        #     # 다르다라는 것은 시간이 바뀌었다는 뜻
        #     elif iffirst:  # 초기 한정 한번만 해줌
        #         before_h = nowh
        #         before_m = nowm
        #         before_h_30 = nowh
        #         before_m_30 = nowm
        #         self.get_before10min_datalist()
        #         iffirst = False
        #     elif before_h_30 != nowh:
        #         if (before_m_30 + 10) - 10 == nowm:
        #             before_h_30 = nowh
        #             before_m_30 = nowm
        #             self.get_before10min_datalist()
        #         else:
        #             QTest.qWait(1000)
        #     elif nowm - before_m_30 == 10:
        #         before_h_30 = nowh
        #         before_m_30 = nowm
        #         self.get_before10min_datalist()
        #     else:
        #         QTest.qWait(1000)
        #     if before_h != nowh:
        #         if (before_m + 1) - 60 <= nowm:
        #             before_h = nowh
        #             before_m = nowm
        #             # self.get_5min_data()
        #             # self.volume_accu()
        #             folderpath = "files/" + self.cur_date
        #             if not os.path.isdir(folderpath):
        #                 os.mkdir(folderpath)
        #             filepath = folderpath + "/" + self.cur_date + ".txt"
        #             f = open(filepath, "a", encoding="utf8")
        #             f.write("%s\t" % (str(self.cur_time)))
        #             for code in (self.enormous_code_list):
        #                 f.write("%s\t" % (str(code)))
        #             f.write("\n")
        #             f.close()
        #             #### 1분마다 각 종목 조회 및 계산 및 buy
        #             self.onemin_calcul()
        #         else:
        #             QTest.qWait(1000)
        #     elif nowm - before_m >= 1:
        #         before_h = nowh
        #         before_m = nowm
        #         folderpath = "files/" + self.cur_date
        #         if not os.path.isdir(folderpath):
        #             os.mkdir(folderpath)
        #         filepath = folderpath + "/" + self.cur_date + ".txt"
        #         f = open(filepath, "a", encoding="utf8")
        #         f.write("%s\t" % (str(self.cur_time)))
        #         for code in (self.enormous_code_list):
        #             f.write("%s\t" % (str(code)))
        #         f.write("\n")
        #         f.close()
        #         self.onemin_calcul()
        #     else:
        #         QTest.qWait(1000)

        self.logging.logger.debug("모든 동작 완료")
        self.dynamicCall("DisconnectRealData(QString)", "3000")
        self.dynamicCall("DisconnectRealData(QString)", "3001")
        self.dynamicCall("DisconnectRealData(QString)", "3002")
        self.dynamicCall("DisconnectRealData(QString)", "3003")
        self.dynamicCall("DisconnectRealData(QString)", "6000")
        exit(0)

        # self.slack.notification(1
        #     pretext="주식자동화 프로그램 동작",
        #     title="주식 자동화 프로그램 동작",
        #     fallback="주식 자동화 프로그램 동작",
        #     text="주식 자동화 프로그램이 동작 되었습니다."
        # )

    def torch_get_data_and_analysis(self):
        # 1. code_list에서 종목 for문
        # 2. 30분 봉 데이터 수신 -> 계산으로 input_data를 가져옴
        # 3. input_data 인자로 rltrader 실행 및 up down 예측
        # 4. 예측에 따라 매수, 매도 결정
        for code in self.enormous_code_list:
            # 30분 데이터 수신
            self.proj30min_kiwoom_db(code=code)
            # 데이터 -> input_data 생성
            input_data = self.proj30min_calcul()
            # input_data 인자로 up down 예측
            # 바깥으로 나가서 다른 폴더의 경로 사용
            filepath = "C:/Users/suk14/PycharmProjects/rltrader"
            fpath = os.path.join(filepath, 'PROJ/calcul_data.txt')
            saving_data = open(fpath, "w", encoding="utf8")
            # state를 file에 저장
            for content in input_data:
                saving_data.write("%s\t" % (content))
            saving_data.close()
            # input_data의 10개 항목이 저장됨
            # 다른 가상환경의 calculate.py 함수 실행
            # 궁금점 : 그 py가 끝날때까지 기다리는가?? (놀랍게도... 기다려줌)
            self.logging.logger.debug("os command start")
            # 정확히는 get_action이 rltrader의 projcalcul.py을 실행함
            self.get_action()
            # rltrader files의 행동결과 받아오기
            filepath = "C:/Users/suk14/PycharmProjects/rltrader/PROJ/result_data.txt"
            f = open(filepath, "r", encoding="utf8")
            action = f.read()
            f.close()
            action.strip()
            act = int(action)
            self.logging.logger.debug("os command done and action")
            # 예측에 따라서 매수, 매도 실행
            if act == 0: # 매도
                if (self.cal_30_dict[code]['주식개수'] != 0):
                    order_success = self.dynamicCall(
                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                        ["신규매도", self.cal_30_dict[code]['주문용스크린번호'], self.account_num, 2, code,
                         int(self.cal_30_dict[code]['주식개수']), "",
                         self.realType.SENDTYPE['거래구분']['시장가'], ""])
                    if order_success == 0:
                        self.logging.logger.debug("매도주문 전달 성공")
                        self.cal_30_dict[code]['주식개수'] -= int(self.cal_30_dict[code]['주식개수'])
                    else:
                        self.logging.logger.debug("매도주문 전달 실패")
            elif act == 1: # 매수
                # 매수금액
                current_price = self.temp_30min_data[0][5]
                masu_amount = int(10000000/current_price)
                if (self.cal_30_dict[code]['주식개수'] == 0):
                    order_success = self.dynamicCall(
                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                        ["신규매수", self.cal_30_dict[code]['주문용스크린번호'], self.account_num, 1, code, masu_amount, "",
                    self.realType.SENDTYPE['거래구분']['시장가'], ""])
                    if order_success == 0:
                        self.logging.logger.debug("매수주문 전달 성공")
                        self.cal_30_dict[code]['주식개수'] += int(masu_amount)
                    else:
                        self.logging.logger.debug("매수주문 전달 실패")
            else:
                pass

    def get_enormous_code(self):
        # 거래량 급증 + 여러 조건 상위 10개 종목 코드를 self.enormous_code_list에 넣기
        # 0. 현재 데이터 기반 code_list 선정
        # 1. 옛날 code_list 중에서 현재 code_list에 포함되지 않을 종목들 전부 팔기
        # 2. code_list 갈아끼우기
        before_code_list = self.enormous_code_list.copy()
        self.enormous_code_list.clear()
        self.get_30min_datalist()
        for code in before_code_list:
            if code not in self.enormous_code_list:
                # 현재 가진 것에 대한 매도
                if (self.cal_30_dict[code]['주식개수'] != 0):
                    order_success = self.dynamicCall(
                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                        ["신규매도", self.cal_30_dict[code]['주문용스크린번호'], self.account_num, 2, code,
                         int(self.cal_30_dict[code]['주식개수']), "",
                         self.realType.SENDTYPE['거래구분']['시장가'], ""])
                    if order_success == 0:
                        self.logging.logger.debug("매도주문 전달 성공")
                        self.cal_30_dict[code]['주식개수'] -= int(self.cal_30_dict[code]['주식개수'])
                    else:
                        self.logging.logger.debug("매도주문 전달 실패")
                # 사전에서 삭제
                del self.cal_30_dict[code]
        for code in self.enormous_code_list:
            if code not in self.cal_30_dict:
                self.cal_30_dict.update({code: {}})
                self.cal_30_dict[code].update({"주식개수": 0})
                self.cal_30_dict[code].update({"주문용스크린번호": str(6000)})

    def get_action(self):
        os.chdir("C:/Users/suk14/PycharmProjects/rltrader")
        exam_string = "python projcalcul.py"
        os.system("conda activate rltraderproj && " + exam_string)
        # 원래대로 돌아오기
        # os.system("conda deactivate")
        os.chdir("C:/Users/suk14/PycharmProjects/week1")
        os.system("conda activate tra32")
        # self.logging.logger.debug("os command get action finish")

    def proj30min_calcul(self):
        temp_data_list = []
        data = self.temp_30min_data.copy()
        # 현재 데이터 data[0][1 ~ 6] 날짜, 시고저종거
        # 29분 전 데이터 data[29][1 ~ 6]
        # input data
        # COLUMNS_TRAINING_DATA = [
        #     'ch_5_ratio', 'ch_10_ratio', 'ch_15_ratio', 'ch_20_ratio', 'ch_25_ratio', 'ch_30_ratio',
        #     'high_start_ratio', 'low_start_ratio', 'end_start_ratio',
        #     'vol_30_weight',
        #     'answer' -> answer 제외
        # ]
        for i in range(6):
            temp = 0.0
            temp = (((data[0][3] + data[0][4]) / 2) - ((data[i*5+4][3] + data[i*5+4][4]) / 2)) / ((data[i*5+4][3] + data[i*5+4][4]) / 2)
            temp_data_list.append(temp)
        high_start_ratio = (data[0][3] - data[0][2]) / data[0][2]
        low_start_ratio = (data[0][4] - data[0][2]) / data[0][2]
        end_start_ratio = (data[0][5] - data[0][2]) / data[0][2]
        total_vol = 0
        for i in range(len(data)):
            total_vol += data[i][6]
        vol_30_weight = data[0][6] / total_vol

        temp_data_list.append(high_start_ratio)
        temp_data_list.append(low_start_ratio)
        temp_data_list.append(end_start_ratio)
        temp_data_list.append(vol_30_weight)

        return temp_data_list

    def onemin_calcul(self):
        for code in self.enormous_code_list:
            self.ppo_onemin_kiwoom_db(code=code)

    def volume_accu(self):
        #self.enormous_code_list.clear()
        self.get_beforeday_min_datalist() # 10개 종목코드가 enormous_code_list에 들어감

    def connectanddisconnecting(self):
        self.enormous_code_list.clear()
        self.get_5min_datalist() # 10개 종목코드가 enormous_code_list에 들어감
        for idx, code in enumerate(self.enormous_code_list):
            tempscreencode = "100" + str(idx)
            self.dynamicCall("DisconnectRealData(QString)", tempscreencode)
            self.logging.logger.debug(
                "%s / %s : Stock Code : %s is registered " % (idx + 1, len(self.enormous_code_list), code))
            self.dynamicCall("SetRealReg(QString, QString, QString, QString)", tempscreencode, code, "41", "0")
        ######################## 20210707 정확히는 수집과는 연관 없음
        # if(self.ten_cal_dict != {}):
        #     for code in self.ten_cal_dict.keys():
        #         if(self.ten_cal_dict[code]['주식개수'] != 0):
        #             order_success = self.dynamicCall(
        #                 "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
        #                 ["신규매도", self.ten_cal_dict[code]['주문용스크린번호'], self.account_num, 2, code, int(self.ten_cal_dict[code]['주식개수']), "",
        #                  self.realType.SENDTYPE['거래구분']['시장가'], ""])
        #             if order_success == 0:
        #                 self.logging.logger.debug("매도주문 전달 성공")
        #                 #self.ten_cal_dict[code]['주식개수'] -= int(self.ten_cal_dict[code]['주식개수'])
        #             else:
        #                 self.logging.logger.debug("매도주문 전달 실패")
        # self.ten_cal_dict.clear()
        # input_data = []
        # cal_data = []
        # for i in range(len(self.enormous_code_list)):
        #     self.ten_cal_dict[self.enormous_code_list[i]] = {}
        #     self.ten_cal_dict[self.enormous_code_list[i]].update({"계산데이터": []})
        #     self.ten_cal_dict[self.enormous_code_list[i]].update({"입력데이터": []})
        #     self.ten_cal_dict[self.enormous_code_list[i]].update({"주식개수": 0})
        #     self.ten_cal_dict[self.enormous_code_list[i]].update({"실제주식개수": 0})
        #     self.ten_cal_dict[self.enormous_code_list[i]].update({"주문용스크린번호": str(9000+i)})

    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1") # 레지스트리에 저장된 API 모듈 불러오기

    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot) # 로그인 관련 이벤트
        self.OnReceiveTrData.connect(self.trdata_slot)  # 트랜잭션 요청 관련 이벤트
        self.OnReceiveMsg.connect(self.msg_slot)

    def real_event_slot(self):
        self.OnReceiveRealData.connect(self.realdata_slot)  # 실시간 이벤트 연결
        self.OnReceiveChejanData.connect(self.chejan_slot) # 종목 주문체결 관련한 이벤트

    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect()") # 로그인 요청 시그널
        self.login_event_loop.exec_() # 이벤트 루프 실행

    def login_slot(self, err_code):
        self.logging.logger.debug(errors(err_code)[1])
        # 로그인 처리 완료 시 이벤트 루프 종료
        self.login_event_loop.exit()

    def get_account_info(self):
        account_list = self.dynamicCall("GetLoginInfo(QString)", "ACCNO") # 계좌번호 반환
        account_num = account_list.split(';')[0] # a;b;c -> [a, b, c]
        self.account_num = account_num
        self.logging.logger.debug("계좌번호 : %s" % account_num)

    def detail_account_info(self, sPrevNext="0"):
        self.logging.logger.debug("예수금상세현황요청")
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "예수금상세현황요청", "opw00001", sPrevNext, self.screen_my_info)
        self.detail_account_info_event_loop.exec_()

    def detail_account_mystock(self, sPrevNext="0"):
        self.logging.logger.debug("계좌평가잔고내역요청")
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "계좌평가잔고내역요청", "opw00018", sPrevNext, self.screen_my_info)
        self.detail_account_info_event_loop.exec_()

    def not_concluded_account(self, sPrevNext="0"):
        self.logging.logger.debug("실시간미체결요청")
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "체결구분", "1")
        self.dynamicCall("SetInputValue(QString, QString)", "매매구분", "0")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "실시간미체결요청", "opt10075", sPrevNext, self.screen_my_info)
        self.detail_account_info_event_loop.exec_()

    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        if sRQName == "예수금상세현황요청":
            deposit = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "예수금")
            self.deposit = int(deposit)

            use_money = float(self.deposit) * self.use_money_percent
            self.use_money = int(use_money)
            self.use_money = self.use_money / 4

            output_deposit = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "출금가능금액")
            self.output_deposit = int(output_deposit)

            self.logging.logger.debug("예수금 : %s" % self.output_deposit)

            self.stop_screen_cancel(self.screen_my_info)

            self.detail_account_info_event_loop.exit()
        elif sRQName == "계좌평가잔고내역요청":
            total_buy_money = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총매입금액")
            self.total_buy_money = int(total_buy_money)
            total_profit_loss_money = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가손익금액")
            self.total_profit_loss_money = int(total_profit_loss_money)
            total_profit_loss_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총수익률(%)")
            self.total_profit_loss_rate = float(total_profit_loss_rate)

            self.logging.logger.debug("계좌평가잔고내역요청 싱글데이터 : %s - %s - %s" % (total_buy_money, total_profit_loss_money, total_profit_loss_rate))

            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목번호")  # 출력 : A039423 // 알파벳 A는 장내주식, J는 ELW종목, Q는 ETN종목
                code = code.strip()[1:]
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")  # 출럭 : 한국기업평가
                stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "보유수량")  # 보유수량 : 000000000000010
                buy_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입가")  # 매입가 : 000000000054100
                learn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "수익률(%)")  # 수익률 : -000000001.94
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")  # 현재가 : 000000003450
                total_chegual_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입금액")
                possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매매가능수량")

                self.logging.logger.debug("종목코드: %s - 종목명: %s - 보유수량: %s - 매입가:%s - 수익률: %s - 현재가: %s" % (
                    code, code_nm, stock_quantity, buy_price, learn_rate, current_price))

                if code in self.account_stock_dict:  # dictionary 에 해당 종목이 있나 확인
                    pass
                else:
                    self.account_stock_dict[code] = {}

                code_nm = code_nm.strip()
                stock_quantity = int(stock_quantity.strip())
                buy_price = int(buy_price.strip())
                learn_rate = float(learn_rate.strip())
                current_price = int(current_price.strip())
                total_chegual_price = int(total_chegual_price.strip())
                possible_quantity = int(possible_quantity.strip())

                self.account_stock_dict[code].update({"종목명": code_nm})
                self.account_stock_dict[code].update({"보유수량": stock_quantity})
                self.account_stock_dict[code].update({"매입가": buy_price})
                self.account_stock_dict[code].update({"수익률(%)": learn_rate})
                self.account_stock_dict[code].update({"현재가": current_price})
                self.account_stock_dict[code].update({"매입금액": total_chegual_price})
                self.account_stock_dict[code].update({'매매가능수량': possible_quantity})

            self.logging.logger.debug("sPreNext : %s" % sPrevNext)
            self.logging.logger.debug("계좌에 가지고 있는 종목은 %s " % rows)

            if sPrevNext == "2":
                self.detail_account_mystock(sPrevNext="2")
            else:
                self.detail_account_info_event_loop.exit()
        elif sRQName == "실시간미체결요청":
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목코드")
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                order_no = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문번호")
                order_status = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문상태")  # 접수,확인,체결
                order_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문수량")
                order_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문가격")
                order_gubun = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문구분")  # -매도, +매수, -매도정정, +매수정정
                not_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "미체결수량")
                ok_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결량")

                code = code.strip()
                code_nm = code_nm.strip()
                order_no = int(order_no.strip())
                order_status = order_status.strip()
                order_quantity = int(order_quantity.strip())
                order_price = int(order_price.strip())
                order_gubun = order_gubun.strip().lstrip('+').lstrip('-')
                not_quantity = int(not_quantity.strip())
                ok_quantity = int(ok_quantity.strip())

                if order_no in self.not_account_stock_dict:
                    pass
                else:
                    self.not_account_stock_dict[order_no] = {}

                self.not_account_stock_dict[order_no].update({'종목코드': code})
                self.not_account_stock_dict[order_no].update({'종목명': code_nm})
                self.not_account_stock_dict[order_no].update({'주문번호': order_no})
                self.not_account_stock_dict[order_no].update({'주문상태': order_status})
                self.not_account_stock_dict[order_no].update({'주문수량': order_quantity})
                self.not_account_stock_dict[order_no].update({'주문가격': order_price})
                self.not_account_stock_dict[order_no].update({'주문구분': order_gubun})
                self.not_account_stock_dict[order_no].update({'미체결수량': not_quantity})
                self.not_account_stock_dict[order_no].update({'체결량': ok_quantity})

                self.logging.logger.debug("미체결 종목 : %s "  % self.not_account_stock_dict[order_no])

            self.detail_account_info_event_loop.exit()
        # elif sRQName == "주식일봉차트조회":
        #     code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
        #     code = code.strip()
        #     cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
        #     self.logging.logger.debug("남은 일자 수 %s" % cnt)
        #
        #     for i in range(cnt):
        #         data = []
        #
        #         current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")  # 출력 : 000070
        #         value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")  # 출력 : 000070
        #         trading_value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래대금")  # 출력 : 000070
        #         date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")  # 출력 : 000070
        #         start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가")  # 출력 : 000070
        #         high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가")  # 출력 : 000070
        #         low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가")  # 출력 : 000070
        #
        #         data.append("")
        #         data.append(current_price.strip())
        #         data.append(value.strip())
        #         data.append(trading_value.strip())
        #         data.append(date.strip())
        #         data.append(start_price.strip())
        #         data.append(high_price.strip())
        #         data.append(low_price.strip())
        #         data.append("")
        #
        #         self.calcul_data.append(data.copy())
        #
        #     if sPrevNext == "2":
        #         self.day_kiwoom_db(code=code, sPrevNext=sPrevNext)
        #
        #     else:
        #         self.logging.logger.debug("총 일수 %s" % len(self.calcul_data))
        #
        #         pass_success = False
        #
        #         # 120일 이평선을 그릴만큼의 데이터가 있는지 체크
        #         if self.calcul_data == None or len(self.calcul_data) < 120:
        #             pass_success = False
        #
        #         else:
        #
        #             # 120일 이평선의 최근 가격 구함
        #             total_price = 0
        #             for value in self.calcul_data[:120]:
        #                 total_price += int(value[1])
        #             moving_average_price = total_price / 120
        #
        #             # 오늘자 주가가 120일 이평선에 걸쳐있는지 확인
        #             bottom_stock_price = False
        #             check_price = None
        #             if int(self.calcul_data[0][7]) <= moving_average_price and moving_average_price <= int(
        #                     self.calcul_data[0][6]):
        #                 self.logging.logger.debug("오늘 주가 120이평선 아래에 걸쳐있는 것 확인")
        #                 bottom_stock_price = True
        #                 check_price = int(self.calcul_data[0][6])
        #
        #             # 과거 일봉 데이터를 조회하면서 120일 이평선보다 주가가 계속 밑에 존재하는지 확인
        #             prev_price = None
        #             if bottom_stock_price == True:
        #
        #                 moving_average_price_prev = 0
        #                 price_top_moving = False
        #                 idx = 1
        #                 while True:
        #
        #                     if len(self.calcul_data[idx:]) < 120:  # 120일치가 있는지 계속 확인
        #                         self.logging.logger.debug("120일치가 없음")
        #                         break
        #
        #                     total_price = 0
        #                     for value in self.calcul_data[idx:120+idx]:
        #                         total_price += int(value[1])
        #                     moving_average_price_prev = total_price / 120
        #
        #                     if moving_average_price_prev <= int(self.calcul_data[idx][6]) and idx <= 20:
        #                         self.logging.logger.debug("20일 동안 주가가 120일 이평선과 같거나 위에 있으면 조건 통과 못함")
        #                         price_top_moving = False
        #                         break
        #
        #                     elif int(self.calcul_data[idx][7]) > moving_average_price_prev and idx > 20:  # 120일 이평선 위에 있는 구간 존재
        #                         self.logging.logger.debug("120일치 이평선 위에 있는 구간 확인됨")
        #                         price_top_moving = True
        #                         prev_price = int(self.calcul_data[idx][7])
        #                         break
        #
        #                     idx += 1
        #
        #                 # 해당부분 이평선이 가장 최근의 이평선 가격보다 낮은지 확인
        #                 if price_top_moving == True:
        #                     if moving_average_price > moving_average_price_prev and check_price > prev_price:
        #                         self.logging.logger.debug("포착된 이평선의 가격이 오늘자 이평선 가격보다 낮은 것 확인")
        #                         self.logging.logger.debug("포착된 부분의 저가가 오늘자 주가의 고가보다 낮은지 확인")
        #                         pass_success = True
        #
        #         if pass_success == True:
        #             self.logging.logger.debug("조건부 통과됨")
        #
        #             code_nm = self.dynamicCall("GetMasterCodeName(QString)", code)
        #
        #             f = open("files/condition_stock.txt", "a", encoding="utf8")
        #             f.write("%s\t%s\t%s\n" % (code, code_nm, str(self.calcul_data[0][1])))
        #             f.close()
        #
        #         elif pass_success == False:
        #             self.logging.logger.debug("조건부 통과 못함")
        #
        #         self.calcul_data.clear()
        #         self.calculator_event_loop.exit()
        elif sRQName == "주식일봉차트조회":
            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            code = code.strip()
            self.logging.logger.debug("종목 이름 %s" % code)
            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            self.logging.logger.debug("남은 분봉수 %s" % cnt)

            for i in range(cnt):
                data = []
                date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")  # 출력 : 20200622090000
                start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가")  # 출력 : 10850
                high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가")  # 출력 : 10900
                low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가")  # 출력 : 10700
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")  # 출력 : 10850
                volume = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")  # 출력 : 15
                #시고저종에 전부 -, +가 붙을 수 있으므로 제거
                data.append("")
                data.append(date.strip())
                data.append(start_price.strip().lstrip('+').lstrip('-'))
                data.append(high_price.strip().lstrip('+').lstrip('-'))
                data.append(low_price.strip().lstrip('+').lstrip('-'))
                data.append(current_price.strip().lstrip('+').lstrip('-'))
                data.append(volume.strip())
                data.append("")
                #임시 data["", 체결시간(20200622090000), 시가(+-10850), 고가(+-10900), 저가(+-10700), 종가 = 현재가(+-10850), 거래량(15), ""]
                self.calcul_data.append(data.copy())

            # 3분봉
            # 한 번 call에 900개까지 (0 ~ 899)
            # 임의의 데이터 수 : 900 * 8 = 7200 = 120 * 60 = 60일치 = 32(batch_size) * 225
            # 약 day_count / 20 달의 3분봉데이터를 저장
            # 하루가 120개
            # 일주일은 600개
            # 학습기가 내리는 판단은 120번...
            # 1분봉
            # 하루에 09:00 ~ 15:30 -> 6시간 30분 ->
            # 하루에 360개...로 착각
            # 실제로는 09:00 ~ 15:19까지가 정상적인 거래
            # 넉넉잡아 09:00 ~ 15:00까지로 제한해도 좋을듯
            # 데이터 수 : 360 * 20 = 7200 = 900 * 8
            # 20일 == 1달(영업일 기준 대략)

            day_count = 200
            update_count = int(day_count * 1)
            # calcul_data에 7200개가 들어갈 때까지 반복
            if (sPrevNext == "2") & (len(self.calcul_data) < update_count):
                self.logging.logger.debug("현재 분봉수 %s" % len(self.calcul_data))
                self.OSSPday_kiwoom_db(code=code, sPrevNext=sPrevNext)
            else:
                #calcul_data에 7200까지 적재하거나 그것보다 적은 분봉데이터인경우
                self.logging.logger.debug("총 분봉수 %s" % len(self.calcul_data))
                filepath = "ppo/day/" + code + "_" + "day_data.txt"
                f = open(filepath, "w", encoding="utf8")
                for k in range(len(self.calcul_data)):
                    f.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (str(self.calcul_data[k][1]), str(self.calcul_data[k][2]), str(self.calcul_data[k][3]),str(self.calcul_data[k][4]),str(self.calcul_data[k][5]),str(self.calcul_data[k][6])))
                f.close()
                self.calcul_data.clear()
                self.calculator_event_loop.exit()
        elif sRQName == "PROJDATACOLLECT주식분봉차트조회":
            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            code = code.strip()
            self.logging.logger.debug("종목 이름 %s" % code)
            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            self.logging.logger.debug("남은 분봉수 %s" % cnt)

            for i in range(cnt):
                data = []
                date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결시간")  # 출력 : 20200622090000
                start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가")  # 출력 : 10850
                high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가")  # 출력 : 10900
                low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가")  # 출력 : 10700
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")  # 출력 : 10850
                volume = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")  # 출력 : 15
                #시고저종에 전부 -, +가 붙을 수 있으므로 제거
                data.append("")
                data.append(date.strip())
                data.append(start_price.strip().lstrip('+').lstrip('-'))
                data.append(high_price.strip().lstrip('+').lstrip('-'))
                data.append(low_price.strip().lstrip('+').lstrip('-'))
                data.append(current_price.strip().lstrip('+').lstrip('-'))
                data.append(volume.strip())
                data.append("")
                #임시 data["", 체결시간(20200622090000), 시가(+-10850), 고가(+-10900), 저가(+-10700), 종가 = 현재가(+-10850), 거래량(15), ""]
                self.calcul_data.append(data.copy())

            # 3분봉
            # 한 번 call에 900개까지 (0 ~ 899)
            # 임의의 데이터 수 : 900 * 8 = 7200 = 120 * 60 = 60일치 = 32(batch_size) * 225
            # 약 day_count / 20 달의 3분봉데이터를 저장
            # 하루가 120개
            # 일주일은 600개
            # 학습기가 내리는 판단은 120번...
            # 1분봉
            # 하루에 09:00 ~ 15:30 -> 6시간 30분 ->
            # 하루에 360개...로 착각
            # 실제로는 09:00 ~ 15:19까지가 정상적인 거래
            # 넉넉잡아 09:00 ~ 15:00까지로 제한해도 좋을듯
            # 데이터 수 : 360 * 20 = 7200 = 900 * 8
            # 20일 == 1달(영업일 기준 대략)

            day_count = 2
            update_count = int(day_count * 360)
            # calcul_data에 7200개가 들어갈 때까지 반복
            if (sPrevNext == "2") & (len(self.calcul_data) < update_count):
                self.logging.logger.debug("현재 분봉수 %s" % len(self.calcul_data))
                self.projdata_kiwoom_db(code=code, sPrevNext=sPrevNext)
            else:
                #calcul_data에 7200까지 적재하거나 그것보다 적은 분봉데이터인경우
                self.logging.logger.debug("총 분봉수 %s" % len(self.calcul_data))
                for a in range(len(self.calcul_data)):
                    datestr = self.calcul_data[a][1][8:]
                    if(datestr > "150000" or datestr < "090000"):
                        continue
                    elif(datestr == "150000"):
                        folderpath = "kiwoom/PROJ/" + self.calcul_data[a][1][:8]
                        if not os.path.isdir(folderpath):
                            os.mkdir(folderpath)
                        filepath = folderpath + "/" + code + "_" + "min_data.txt"
                        f = open(filepath, "w", encoding="utf8")
                        f.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (
                        str(self.calcul_data[a][1]), str(self.calcul_data[a][2]), str(self.calcul_data[a][3]),
                        str(self.calcul_data[a][4]), str(self.calcul_data[a][5]), str(self.calcul_data[a][6])))
                        f.close()
                    else:
                        folderpath = "kiwoom/PROJ/" + self.calcul_data[a][1][:8]
                        if not os.path.isdir(folderpath):
                            os.mkdir(folderpath)
                        filepath = folderpath + "/" + code + "_" + "min_data.txt"
                        f = open(filepath, "a", encoding="utf8")
                        f.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (str(self.calcul_data[a][1]), str(self.calcul_data[a][2]), str(self.calcul_data[a][3]),str(self.calcul_data[a][4]),str(self.calcul_data[a][5]),str(self.calcul_data[a][6])))
                        f.close()
                # filepath = "kiwoom/PROJ/" + self.cur_date + "/" + code + "_" + "min_data.txt"
                # f = open(filepath, "w", encoding="utf8")
                # for k in range(len(self.calcul_data)):
                #     f.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (str(self.calcul_data[k][1]), str(self.calcul_data[k][2]), str(self.calcul_data[k][3]),str(self.calcul_data[k][4]),str(self.calcul_data[k][5]),str(self.calcul_data[k][6])))
                # f.close()

                self.calcul_data.clear()
                self.calculator_event_loop.exit()
        elif sRQName == "PROJ30분봉차트조회":
            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            code = code.strip()
            self.logging.logger.debug("종목 이름 %s" % code)
            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            self.logging.logger.debug("남은 분봉수 %s" % cnt)

            for i in range(30):
                data = []
                date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                        "체결시간")  # 출력 : 20200622090000
                start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                               "시가")  # 출력 : 10850
                high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                              "고가")  # 출력 : 10900
                low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                             "저가")  # 출력 : 10700
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                 "현재가")  # 출력 : 10850
                volume = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                          "거래량")  # 출력 : 15
                # 시고저종에 전부 -, +가 붙을 수 있으므로 제거
                data.append("")
                data.append(date.strip())
                data.append(start_price.strip().lstrip('+').lstrip('-'))
                data.append(high_price.strip().lstrip('+').lstrip('-'))
                data.append(low_price.strip().lstrip('+').lstrip('-'))
                data.append(current_price.strip().lstrip('+').lstrip('-'))
                data.append(volume.strip())
                data.append("")
                # 임시 data["", 체결시간(20200622090000), 시가(+-10850), 고가(+-10900), 저가(+-10700), 종가 = 현재가(+-10850), 거래량(15), ""]
                self.temp_30min_data.append(data.copy())

            self.calculator_event_loop.exit()
        elif sRQName == "PPO주식분봉차트조회":
            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            code = code.strip()
            self.logging.logger.debug("종목 이름 %s" % code)
            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            cnt = 11
            self.logging.logger.debug("남은 분봉수 %s" % cnt)
            ###### 과거의 10개의 데이터를 토대로 판단(현재의 데이터는 계속 수정되기 때문)
            for i in range(cnt):
                data = []
                date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결시간")  # 출력 : 20200622090000
                start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가")  # 출력 : 10850
                high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가")  # 출력 : 10900
                low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가")  # 출력 : 10700
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")  # 출력 : 10850
                volume = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")  # 출력 : 15
                #시고저종에 전부 -, +가 붙을 수 있으므로 제거
                data.append("")
                data.append(date.strip())
                data.append(start_price.strip().lstrip('+').lstrip('-'))
                data.append(high_price.strip().lstrip('+').lstrip('-'))
                data.append(low_price.strip().lstrip('+').lstrip('-'))
                data.append(current_price.strip().lstrip('+').lstrip('-'))
                data.append(volume.strip())
                data.append("")
                #임시 data["", 체결시간(20200622090000), 시가(+-10850), 고가(+-10900), 저가(+-10700), 종가 = 현재가(+-10850), 거래량(15), ""]
                self.calcul_data.append(data.copy())
            self.calcul_data.reverse()
            print(self.calcul_data)
            ###### 9시 11분 이전인 경우
            if(self.calcul_data[0][1] <= (str(self.cur_date) + "000000")):
                self.calcul_data.clear()
                self.calculator_event_loop.exit()
            else:
                temp_cal_data = []
                open_lastclose_ratio = (float(self.calcul_data[9][2]) - float(self.calcul_data[8][5])) / \
                                       (float(self.calcul_data[8][5])) * 100
                high_lastclose_ratio = (float(self.calcul_data[9][3]) - float(self.calcul_data[8][5])) / \
                                       (float(self.calcul_data[8][5])) * 100
                low_lastclose_ratio = (float(self.calcul_data[9][4]) - float(self.calcul_data[8][5])) / \
                                       (float(self.calcul_data[8][5])) * 100
                close_lastclose_ratio = (float(self.calcul_data[9][5]) - float(self.calcul_data[8][5])) / \
                                       (float(self.calcul_data[8][5])) * 100
                volume_lastclose_ratio = (float(self.calcul_data[9][6]) - float(self.calcul_data[8][6])) / \
                                       (float(self.calcul_data[8][6])) * 100
                open_average = 0
                for i in range(5):
                    open_average += int(self.calcul_data[i + 5][2])
                open_ma5 = float(open_average / 5)
                open_ma5_ratio = (int(self.calcul_data[9][2]) - open_ma5) / open_ma5 * 100
                high_average = 0
                for i in range(5):
                    high_average += int(self.calcul_data[i + 5][3])
                high_ma5 = float(high_average / 5)
                high_ma5_ratio = (int(self.calcul_data[9][3]) - high_ma5) / high_ma5 * 100
                low_average = 0
                for i in range(5):
                    low_average += int(self.calcul_data[i + 5][4])
                low_ma5 = float(low_average / 5)
                low_ma5_ratio = (int(self.calcul_data[9][4]) - low_ma5) / low_ma5 * 100
                close_average = 0
                for i in range(5):
                    close_average += int(self.calcul_data[i + 5][5])
                close_ma5 = float(close_average / 5)
                close_ma5_ratio = (int(self.calcul_data[9][5]) - close_ma5) / close_ma5 * 100
                volume_average = 0
                for i in range(5):
                    volume_average += int(self.calcul_data[i + 5][6])
                volume_ma5 = float(volume_average / 5)
                volume_ma5_ratio = (int(self.calcul_data[9][6]) - volume_ma5) / volume_ma5 * 100
                open_average_10 = 0
                for i in range(10):
                    open_average_10 += int(self.calcul_data[i][2])
                open_ma10 = float(open_average_10 / 5)
                open_ma10_ratio = (int(self.calcul_data[9][2]) - open_ma10) / open_ma10 * 100
                high_average_10 = 0
                for i in range(10):
                    high_average_10 += int(self.calcul_data[i][3])
                high_ma10 = float(high_average_10 / 5)
                high_ma10_ratio = (int(self.calcul_data[9][3]) - high_ma10) / high_ma10 * 100
                low_average_10 = 0
                for i in range(10):
                    low_average_10 += int(self.calcul_data[i][4])
                low_ma10 = float(low_average_10 / 5)
                low_ma10_ratio = (int(self.calcul_data[9][4]) - low_ma10) / low_ma10 * 100
                close_average_10 = 0
                for i in range(10):
                    close_average_10 += int(self.calcul_data[i][5])
                close_ma10 = float(close_average_10 / 5)
                close_ma10_ratio = (int(self.calcul_data[9][5]) - close_ma10) / close_ma10 * 100
                volume_average_10 = 0
                for i in range(10):
                    volume_average_10 += int(self.calcul_data[i][6])
                volume_ma10 = float(volume_average_10 / 5)
                volume_ma10_ratio = (int(self.calcul_data[9][6]) - volume_ma10) / volume_ma10 * 100
                # mado_ma5_sub masu_ma5_sub
                temp_cal_data.append(open_lastclose_ratio)
                temp_cal_data.append(high_lastclose_ratio)
                temp_cal_data.append(low_lastclose_ratio)
                temp_cal_data.append(close_lastclose_ratio)
                temp_cal_data.append(volume_lastclose_ratio)
                temp_cal_data.append(open_ma5_ratio)
                temp_cal_data.append(high_ma5_ratio)
                temp_cal_data.append(low_ma5_ratio)
                temp_cal_data.append(close_ma5_ratio)
                temp_cal_data.append(volume_ma5_ratio)
                temp_cal_data.append(open_ma10_ratio)
                temp_cal_data.append(high_ma10_ratio)
                temp_cal_data.append(low_ma10_ratio)
                temp_cal_data.append(close_ma10_ratio)
                temp_cal_data.append(volume_ma10_ratio)
                ###### 연산
                for i in range(len(self.weights)):  # 0 ~ 8
                    temp_weight = np.array(self.weights[i], dtype=np.float64).T
                    temp_biased = np.array(self.biaseds[i], dtype=np.float64).T
                    if i == (len(self.weights) - 1):
                        temp_cal_data = (np.dot(temp_cal_data, temp_weight) + temp_biased)
                    else:
                        temp_cal_data = np.tanh(np.dot(temp_cal_data, temp_weight) + temp_biased)
                #### for문 이후 temp_cal_data는 결과값임
                #print(temp_cal_data[0])
                prob = softmax(temp_cal_data[0])
                #print(prob)
                a = random.choices([0, 1], prob, k=1)
                print(a[0])
                trading_stocks = a[0] # action 0 is buy 1 is sell
                # action = float(action / 10)  # 0.0 ~ 0.9로의 변환
                # testsample = copy.deepcopy(self.invest_dict[code])
                # num_stocks = int(action * int((testsample["포트폴리오가치"] / testsample["현재가"])))
                # trading_stocks = num_stocks - testsample["주식개수"]
                stocks = int(1000000 / int(current_price.strip().lstrip('+').lstrip('-')))
                mado_stocks = int(self.ten_cal_dict[code]['주식개수'])
                real_mado_stocks = int(self.ten_cal_dict[code]['실제주식개수'])
                if trading_stocks == 0:  # 매수를 해야하는 상황
                    if (mado_stocks == 0):
                        print(prob)
                        self.ordercount += 1
                        if (self.ordercount >= 80):
                            self.dynamicCall("DisconnectRealData(QString)", "6000")  # 스크린 연결 끊기
                            self.totalorder += self.ordercount
                            self.ordercount = 0
                        order_success = self.dynamicCall(
                            "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                            ["신규매수", self.ten_cal_dict[code]['주문용스크린번호'], self.account_num, 1, code, stocks, "",
                             self.realType.SENDTYPE['거래구분']['시장가'], ""])
                        if order_success == 0:
                            self.logging.logger.debug("매수주문 전달 성공")
                            self.ten_cal_dict[code]['주식개수'] += int(stocks)
                        else:
                            self.logging.logger.debug("매수주문 전달 실패")
                elif trading_stocks == 1:  # 매도를 해야하는 상황 # int
                    if (real_mado_stocks > 0):
                        print(prob)
                        self.ordercount += 1
                        if (self.ordercount >= 80):
                            self.dynamicCall("DisconnectRealData(QString)", "6000")  # 스크린 연결 끊기
                            self.totalorder += self.ordercount
                            self.ordercount = 0
                        order_success = self.dynamicCall(
                            "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                            ["신규매도", self.ten_cal_dict[code]['주문용스크린번호'], self.account_num, 2, code,
                             real_mado_stocks, "",
                             self.realType.SENDTYPE['거래구분']['시장가'], ""])
                        if order_success == 0:
                            self.logging.logger.debug("매도주문 전달 성공")
                            self.ten_cal_dict[code]['주식개수'] -= int(real_mado_stocks)
                        else:
                            self.logging.logger.debug("매도주문 전달 실패")
                        # QTest.qWait(5000) # 5초정도 기다림
                else:  # 0.5 ~ 0.7은 굳이 매도를 하거나 매수를 할 필요는 없으므로 -> 수수료 줄이기
                    pass
                self.calcul_data.clear()
                self.calculator_event_loop.exit()
        # elif sRQName == "주식5분봉차트조회":
        #     code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
        #     code = code.strip()
        #     #self.logging.logger.debug("종목코드 : %s" % code)
        #     # 기존 input_data clear()
        #     input_data = []
        #     for i in range(10): # 10개의 데이터 받기
        #         data = []
        #         start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가")  # 출력 : 10850
        #         high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가")  # 출력 : 10900
        #         low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가")  # 출력 : 10700
        #         current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")  # 출력 : 10850
        #         volume = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")  # 출력 : 15
        #         # 시고저종에 전부 -, +가 붙을 수 있으므로 제거
        #         data.append("")
        #         data.append(int(start_price.strip().lstrip('+').lstrip('-')))
        #         data.append(int(high_price.strip().lstrip('+').lstrip('-')))
        #         data.append(int(low_price.strip().lstrip('+').lstrip('-')))
        #         data.append(int(current_price.strip().lstrip('+').lstrip('-')))
        #         data.append(int(volume.strip()))
        #         data.append("")
        #         # 임시 data["", 체결시간(20200622090000), 시가(+-10850), 고가(+-10900), 저가(+-10700), 종가 = 현재가(+-10850), 거래량(15), ""]
        #         self.calcul_data.append(data.copy())
        #     # open_lastclose_ratio, high_lastclose_ratio, low_lastclose_ratio, close_lastclose_ratio, volume_lastvolume_ratio
        #     # open_ma5_ratio, open_ma10_ratio / high 5 10, low 5, 10, close 5, 10 volume 5, 10
        #     #calcul_data[0][1] # 1번째의 시가(제일 최근의)
        #
        #     open_lastclose_ratio = (self.calcul_data[0][1] - self.calcul_data[1][4]) / self.calcul_data[1][4]
        #     high_lastclose_ratio = (self.calcul_data[0][2] - self.calcul_data[1][4]) / self.calcul_data[1][4]
        #     low_lastclose_ratio = (self.calcul_data[0][3] - self.calcul_data[1][4]) / self.calcul_data[1][4]
        #     close_lastclose_ratio = (self.calcul_data[0][4] - self.calcul_data[1][4]) / self.calcul_data[1][4]
        #     volume_lastclose_ratio = (self.calcul_data[0][5] - self.calcul_data[1][5]) / self.calcul_data[1][5]
        #     open_average = float(0)
        #     high_average = float(0)
        #     low_average = float(0)
        #     close_average = float(0)
        #     volume_average = float(0)
        #     for i in range(5):
        #         open_average += self.calcul_data[i][1]
        #         high_average += self.calcul_data[i][2]
        #         low_average += self.calcul_data[i][3]
        #         close_average += self.calcul_data[i][4]
        #         volume_average += self.calcul_data[i][5]
        #     open_average = open_average / 5
        #     high_average = high_average / 5
        #     low_average = low_average / 5
        #     close_average = close_average / 5
        #     volume_average = volume_average / 5
        #     open_ma5_ratio = (self.calcul_data[0][1] - open_average) / open_average
        #     high_ma5_ratio = (self.calcul_data[0][2] - high_average) / high_average
        #     low_ma5_ratio = (self.calcul_data[0][3] - low_average) / low_average
        #     close_ma5_ratio = (self.calcul_data[0][4] - close_average) / close_average
        #     volume_ma5_ratio = (self.calcul_data[0][5] - volume_average) / volume_average
        #     open_average = float(0)
        #     high_average = float(0)
        #     low_average = float(0)
        #     close_average = float(0)
        #     volume_average = float(0)
        #     for i in range(10):
        #         open_average += self.calcul_data[i][1]
        #         high_average += self.calcul_data[i][2]
        #         low_average += self.calcul_data[i][3]
        #         close_average += self.calcul_data[i][4]
        #         volume_average += self.calcul_data[i][5]
        #     open_average = open_average / 10
        #     high_average = high_average / 10
        #     low_average = low_average / 10
        #     close_average = close_average / 10
        #     volume_average = volume_average / 10
        #     open_ma10_ratio = (self.calcul_data[0][1] - open_average) / open_average
        #     high_ma10_ratio = (self.calcul_data[0][2] - high_average) / high_average
        #     low_ma10_ratio = (self.calcul_data[0][3] - low_average) / low_average
        #     close_ma10_ratio = (self.calcul_data[0][4] - close_average) / close_average
        #     volume_ma10_ratio = (self.calcul_data[0][5] - volume_average) / volume_average
        #
        #     input_data = [open_lastclose_ratio, high_lastclose_ratio, low_lastclose_ratio, close_lastclose_ratio, volume_lastclose_ratio,
        #                         open_ma5_ratio, open_ma10_ratio, high_ma5_ratio, high_ma10_ratio, low_ma5_ratio, low_ma10_ratio,
        #                        close_ma5_ratio, close_ma10_ratio, volume_ma5_ratio, volume_ma10_ratio]
        #     # 새로운 데이터로 업데이트 후에 현재의 포트폴리오 가치 대비 기준 포트폴리오 가치가 많이(-2 ~ 3%) 난다면 기준포트폴리오가치를 현재의 포트폴리오가치로 치환
        #     # 아니면 유지하여 언젠가 차이가 날 때까지 기준포트폴리오 가치를 일단은 고정시킴
        #     self.logging.logger.debug("업데이트 바로 직전")
        #     self.invest_dict[code].update({"현재가": self.calcul_data[0][4]})
        #     self.invest_dict[code].update({"입력데이터": input_data})
        #     # invest_dict에 지금 현재가에 따른 포트폴리오가치 변경 및 기준포트폴리오가치 변경
        #     portfolio_value = self.calcul_data[0][4] * self.invest_dict[code]["주식개수"] + self.invest_dict[code]["운용금액"]
        #     self.invest_dict[code].update({"포트폴리오가치": portfolio_value})
        #     base_pv_ratio = (self.invest_dict[code]['포트폴리오가치'] - self.invest_dict[code]['기준포트폴리오가치']) / self.invest_dict[code]['기준포트폴리오가치']
        #     if base_pv_ratio > 0.03 or base_pv_ratio < -0.02:
        #         self.invest_dict[code].update({"기준포트폴리오가치": portfolio_value})
        #     self.logging.logger.debug("업데이트 완료")
        #     self.calcul_data.clear()
        #     self.calculator_event_loop.exit()
        elif sRQName == "전일거래량상위요청":
            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            self.logging.logger.debug("남은 종목들 수 %s" % cnt)
            for i in range(cnt):
                data = []
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목코드")  # 출력 : 종목코드
                data.append("")
                data.append(code.strip())
                data.append("")
                self.calcul_data.append(data.copy())
            f = open("files/selected/bigvolumedata.txt", "w", encoding="utf8")
            for k in range(len(self.calcul_data)):
                f.write("%s\n" % str(self.calcul_data[k][1]))
            f.close()
            self.calcul_data.clear()
            self.calculator_event_loop.exit()
        elif sRQName == "당일거래량상위요청":
            #cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            #self.logging.logger.debug("남은 종목들 수 %s" % cnt)
            # 상위 50개의 종목 코드를 받음(왜냐하면.. 5억 / 50이 천만이니까..
            # file한번 싹지우기
            folderpath = "ppo/" + self.cur_date
            if not os.path.isdir(folderpath):
                os.mkdir(folderpath)
            filepath = folderpath + "/" + self.cur_date + ".txt"
            f = open(filepath, "w", encoding="utf8")
            f.close()
            f = open(filepath, "a", encoding="utf8")
            for i in range(50):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목코드")  # 출력 : 종목코드
                code = code.strip()
                self.logging.logger.debug("종목코드 : %s" % code)
                f.write("%s\n" % (code))
            f.close()
            # 10개로 조정
            # 20개로 조정
            self.calculator_event_loop.exit()
        # elif sRQName == "당일투자종목선정":
        #     #cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
        #     #self.logging.logger.debug("남은 종목들 수 %s" % cnt)
        #     # 상위 50개의 종목 코드를 받음(왜냐하면.. 5억 / 50이 천만이니까..
        #     # file한번 싹지우기
        #     file = open("files/selected/invest_code.txt", "w", encoding="utf8")
        #     file.close()
        #     # 10개로 조정
        #     # 20개로 조정
        #     # 13개로 조정 4.3 * 13
        #     for i in range(20):
        #         code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목코드")  # 출력 : 종목코드
        #         code = code.strip()
        #         self.logging.logger.debug("종목코드 : %s" % code)
        #         if code in self.invest_dict:  # dictionary 에 해당 종목이 있나 확인
        #             pass
        #         else:
        #             self.invest_dict[code] = {}
        #         # 초기 자금 세팅 + 상태 세팅
        #         invest_money = int(10000000)
        #         num_stocks = int(0)
        #         portfolio_value = float(10000000)
        #         base_portfolio_value = float(10000000)
        #         input_data = []
        #         self.invest_dict[code].update({"운용금액": invest_money})
        #         self.invest_dict[code].update({"주식개수": num_stocks})
        #         self.invest_dict[code].update({"포트폴리오가치": portfolio_value})
        #         self.invest_dict[code].update({"기준포트폴리오가치": base_portfolio_value})
        #         self.invest_dict[code].update({"입력데이터": input_data})
        #         # 주식거래 종료 후 아래의 코드로 50개의 종목 코드 저장
        #         file1 = open("files/selected/invest_code.txt", "a", encoding="utf8")
        #         file1.write("%s\n" % (code))
        #         file1.close()
        #     self.calculator_event_loop.exit()
        # elif sRQName == "체결강도1분단위조회":
        #     # code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
        #     # code = code.strip()
        #     code = self.code
        #     self.logging.logger.debug("종목코드 : %s" % code)
        #     # 기존 input_data clear()
        #     input_data = []
        #     for i in range(10): # 10개의 데이터 받기
        #         data = []
        #         current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")  # 출력 : 10850 or -10850
        #         accu_volume = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "누적거래량")  # 출력 : 12343125
        #         chegeul = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결강도")  # 출력 : 79.35
        #         # 시고저종에 전부 -, +가 붙을 수 있으므로 제거
        #         data.append("")
        #         data.append(float(current_price.strip().lstrip('+').lstrip('-')))
        #         data.append(float(accu_volume.strip().lstrip('+').lstrip('-')))
        #         data.append(float(chegeul.strip().lstrip('+').lstrip('-')))
        #         data.append("")
        #         # 임시 data["", 체결시간(20200622090000), 시가(+-10850), 고가(+-10900), 저가(+-10700), 종가 = 현재가(+-10850), 거래량(15), ""]
        #         self.calcul_data.append(data.copy())
        #     # open_lastclose_ratio, high_lastclose_ratio, low_lastclose_ratio, close_lastclose_ratio, volume_lastvolume_ratio
        #     # open_ma5_ratio, open_ma10_ratio / high 5 10, low 5, 10, close 5, 10 volume 5, 10
        #     #calcul_data[0][1] # 1번째의 시가(제일 최근의)
        #     close_lastclose_ratio = (self.calcul_data[0][1] - self.calcul_data[1][1]) / self.calcul_data[1][1]
        #     accvol_lastaccvol_ratio = (self.calcul_data[0][2] - self.calcul_data[1][2]) / self.calcul_data[1][2]
        #     chegeul_lastchegeul_ratio = (self.calcul_data[0][3] - self.calcul_data[1][3]) / self.calcul_data[1][3]
        #     close_average = float(0)
        #     accvol_average = float(0)
        #     chegeul_average = float(0)
        #     for i in range(5):
        #         close_average += self.calcul_data[i][1]
        #         accvol_average += self.calcul_data[i][2]
        #         chegeul_average += self.calcul_data[i][3]
        #     close_average = close_average / 5
        #     accvol_average = accvol_average / 5
        #     chegeul_average = chegeul_average / 5
        #     close_ma5_ratio = (self.calcul_data[0][1] - close_average) / close_average
        #     accvol_ma5_ratio = (self.calcul_data[0][2] - accvol_average) / accvol_average
        #     chegeul_ma5_ratio = (self.calcul_data[0][3] - chegeul_average) / chegeul_average
        #     close_average = float(0)
        #     accvol_average = float(0)
        #     chegeul_average = float(0)
        #     for i in range(10):
        #         close_average += self.calcul_data[i][1]
        #         accvol_average += self.calcul_data[i][2]
        #         chegeul_average += self.calcul_data[i][3]
        #     close_average = close_average / 10
        #     accvol_average = accvol_average / 10
        #     chegeul_average = chegeul_average / 10
        #     close_ma10_ratio = (self.calcul_data[0][1] - close_average) / close_average
        #     accvol_ma10_ratio = (self.calcul_data[0][2] - accvol_average) / accvol_average
        #     chegeul_ma10_ratio = (self.calcul_data[0][3] - chegeul_average) / chegeul_average
        #     input_data = [close_lastclose_ratio, accvol_lastaccvol_ratio, chegeul_lastchegeul_ratio,
        #                   close_ma5_ratio, close_ma10_ratio, accvol_ma5_ratio, accvol_ma10_ratio, chegeul_ma5_ratio, chegeul_ma10_ratio
        #                   ]
        #     # 새로운 데이터로 업데이트 후에 현재의 포트폴리오 가치 대비 기준 포트폴리오 가치가 많이(-2 ~ 3%) 난다면 기준포트폴리오가치를 현재의 포트폴리오가치로 치환
        #     # 아니면 유지하여 언젠가 차이가 날 때까지 기준포트폴리오 가치를 일단은 고정시킴
        #     self.logging.logger.debug("업데이트 바로 직전")
        #     self.invest_dict[code].update({"현재가": self.calcul_data[0][1]})
        #     self.invest_dict[code].update({"입력데이터": input_data})
        #     # invest_dict에 지금 현재가에 따른 포트폴리오가치 변경 및 기준포트폴리오가치 변경
        #     portfolio_value = self.calcul_data[0][1] * self.invest_dict[code]["주식개수"] + self.invest_dict[code]["운용금액"]
        #     self.invest_dict[code].update({"포트폴리오가치": portfolio_value})
        #     base_pv_ratio = (self.invest_dict[code]['포트폴리오가치'] - self.invest_dict[code]['기준포트폴리오가치']) / self.invest_dict[code]['기준포트폴리오가치']
        #     # 기준포트폴리오가치를 갱신하지 않는 방향으로 진행함
        #     # if base_pv_ratio > 0.03 or base_pv_ratio < -0.02:
        #     #     self.invest_dict[code].update({"기준포트폴리오가치": portfolio_value})
        #     self.logging.logger.debug("업데이트 완료")
        #     self.calcul_data.clear()
        #     self.calculator_event_loop.exit()
        # elif sRQName == "체결강도추이시간별요청":
        #     code = self.code
        #     code = code.strip()
        #     self.logging.logger.debug("종목 이름 %s" % code)
        #     cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
        #     self.logging.logger.debug("남은 수 %s" % cnt)
        #     for i in range(cnt):
        #         data = []
        #         date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결시간")  # 출력 : 090000
        #         pc = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결강도")  # 출력 : 135.28
        #         # 시고저종에 전부 -, +가 붙을 수 있으므로 제거
        #         data.append("")
        #         data.append(date.strip())
        #         data.append(pc.strip().lstrip('+').lstrip('-'))
        #         data.append("")
        #         # 임시 data["", 체결시간(090000), 체결강도(150.52), ""]
        #         self.calcul_data.append(data.copy())
        #     # 09000 ~ 15:~~ 까지 전부 받아옴
        #     day_count = 20
        #     update_count = int(day_count * 360)
        #     if (sPrevNext == "2") & (len(self.calcul_data) < update_count):
        #         self.logging.logger.debug("현재 수 %s" % len(self.calcul_data))
        #         self.get_pc_conclude_kiwoom_db(code=code, sPrevNext=sPrevNext)
        #     else:
        #         self.logging.logger.debug("총 수 %s" % len(self.calcul_data))
        #         filepath = "files/" + code + "_" + "pc_data.txt"
        #         f = open(filepath, "w", encoding="utf8")
        #         for k in range(len(self.calcul_data)):
        #             f.write("%s\t%s\n" % (str(self.calcul_data[k][1]), str(self.calcul_data[k][2])))
        #         f.close()
        #         self.calcul_data.clear()
        #         self.calculator_event_loop.exit()
        # elif sRQName == "체결강도추이일별요청":
        #     continue_flag = True
        #     code = self.code
        #     code = code.strip()
        #     self.logging.logger.debug("종목 이름 %s" % code)
        #     cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
        #     self.logging.logger.debug("남은 수 %s" % cnt)
        #     for i in range(cnt):
        #         # 일일 자료 이기에 누적 거래량은 의미가 없음
        #         data = []
        #         date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")  # 출력 : 090000
        #         current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")  # 출력 : 10850 or -10850
        #         moneyvolume = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "누적거래대금")  # 출력 : 12343125
        #         chegeul = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
        #                                    "체결강도")  # 출력 : 79.35
        #         # 시고저종에 전부 -, +가 붙을 수 있으므로 제거
        #         date = date.strip()
        #         # date = "20200707090000"
        #         # real_date "20200707"
        #         # real_time "090000"
        #         # real_date = date[0:8]
        #         # real_time = date[8:]
        #         real_date = date
        #         #limit_start = "20200701"
        #         #limit_end = "20200930"
        #         limit_start = "20201001"
        #         limit_end = "20201031"
        #         # 문제점 : 날짜가 바뀌면 어떻게 할 것?? -> 당일전일체결은 날짜가 바뀌지 않음
        #         # 항상 최신의 날짜부터 받아오기 때문에, 끝 날짜보다 높은 날짜는 필요없음
        #         # if real_date > self.end_date:
        #         #     continue
        #         # 원하는 날짜의 데이터 중 9시 ~ 15시 data만 calcul_data list에 저장
        #         if real_date > limit_end:
        #             continue
        #         if real_date <= limit_start:
        #             continue_flag = False
        #         if real_date < limit_start:
        #             continue
        #         data.append("")
        #         data.append(date.strip())
        #         data.append(current_price.strip().lstrip('+').lstrip('-'))
        #         # data.append(volume.strip().lstrip('+').lstrip('-'))
        #         data.append(moneyvolume.strip().lstrip('+').lstrip('-'))
        #         data.append(chegeul.strip().lstrip('+').lstrip('-'))
        #         data.append("")
        #         # 임시 data["", 체결시간(090000), 현재가(+-10850), 거래량(15000), 체결강도(78.51), ""]
        #         self.calcul_data.append(data.copy())
        #     # 09000 ~ 15:~~ 까지 전부 받아옴
        #     if (sPrevNext == "2") & (continue_flag):
        #         self.logging.logger.debug("현재 분봉수 %s" % len(self.calcul_data))
        #         self.get_day_cheguel_kiwoom_db(code=code, sPrevNext=sPrevNext)
        #     else:
        #         self.logging.logger.debug("총 분봉수 %s" % len(self.calcul_data))
        #         #folderpath = "files/daysdata"
        #         folderpath = "files/testdaysdata"
        #         if not os.path.isdir(folderpath):
        #             os.mkdir(folderpath)
        #         filepath = folderpath + "/" + code + ".txt"
        #         f = open(filepath, "w", encoding="utf8")
        #         for k in range(len(self.calcul_data)):
        #             f.write("%s\t%s\t%s\t%s\n" % (
        #                 str(self.calcul_data[k][1]), str(self.calcul_data[k][2]), str(self.calcul_data[k][3]),
        #                 str(self.calcul_data[k][4])))
        #         f.close()
        #         self.calcul_data.clear()
        #         self.calculator_event_loop.exit()
        # elif sRQName == "주식호가요청":
        #     code = self.code
        #     code = code.strip()
        #     self.logging.logger.debug("종목 이름 %s" % code)# 일일 자료 이기에 누적 거래량은 의미가 없음
        #     data = []
        #     date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "호가잔량기준시간")  # 출력 : 090000
        #     mado = []
        #     masu = []
        #     mado_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "매도최우선호가")  # 출력 : 090000
        #     masu_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "매수최우선호가")  # 출력 : 090000
        #     tempstr = ""
        #     for i in range(10):
        #         if (i + 1) == 1:
        #             mado.append(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "매도최우선잔량"))
        #         elif (i + 1) == 6:
        #             tempstr = "매도" + str(i + 1) + "우선잔량"
        #             mado.append(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, tempstr))  # 출력 : 090000
        #         else:
        #             tempstr = "매도" + str(i + 1) + "차선잔량"
        #             mado.append(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, tempstr))
        #     for j in range(10):
        #         if (j + 1) == 1:
        #             masu.append(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "매수최우선잔량"))  # 출력 : 090000
        #         elif (j + 1) == 6:
        #             tempstr = "매수" + str(j + 1) + "우선잔량"
        #             masu.append(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, tempstr))
        #         else:
        #             tempstr = "매수" + str(j + 1) + "차선잔량"
        #             masu.append(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, tempstr))
        #     total_mado = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총매도잔량")  # 출력 : 090000
        #     total_masu = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총매수잔량")  # 출력 : 090000
        #     # 시고저종에 전부 -, +가 붙을 수 있으므로 제거
        #     date = date.strip()
        #     data.append("")
        #     data.append(date.strip())
        #     data.append(mado_price.strip().lstrip('+').lstrip('-'))
        #     data.append(masu_price.strip().lstrip('+').lstrip('-'))
        #     data.append(total_mado.strip().lstrip('+').lstrip('-'))
        #     data.append(total_masu.strip().lstrip('+').lstrip('-'))
        #     # 순서대로 최우선, 2, 3, 4, 5, 6, 7 8, 9, 10...
        #     for i in range(10):
        #         data.append(mado[i].strip().lstrip('+').lstrip('-'))
        #     for j in range(10):
        #         data.append(masu[j].strip().lstrip('+').lstrip('-'))
        #     data.append("")
        #     # 임시 data["", 체결시간(090000), 현재가(+-10850), 거래량(15000), 체결강도(78.51), ""]
        #     self.calcul_data.append(data.copy())
        #     # 09000 ~ 15:~~ 까지 전부 받아옴
        #     #self.logging.logger.debug("총 분봉수 %s" % len(self.calcul_data))
        #     folderpath = "files/" + self.cur_date
        #     if not os.path.isdir(folderpath):
        #         os.mkdir(folderpath)
        #     filepath = folderpath + "/" + code + ".txt"
        #     f = open(filepath, "a", encoding="utf8")
        #     for k in range(len(self.calcul_data)):
        #         f.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
        #                 str(self.calcul_data[k][1]), str(self.calcul_data[k][2]), str(self.calcul_data[k][3]),
        #                 str(self.calcul_data[k][4]), str(self.calcul_data[k][5]), str(self.calcul_data[k][6]),
        #                 str(self.calcul_data[k][7]), str(self.calcul_data[k][8]), str(self.calcul_data[k][9]),
        #                 str(self.calcul_data[k][10]), str(self.calcul_data[k][11]), str(self.calcul_data[k][12]),
        #                 str(self.calcul_data[k][13]), str(self.calcul_data[k][14]), str(self.calcul_data[k][15]),
        #                 str(self.calcul_data[k][16]), str(self.calcul_data[k][17]), str(self.calcul_data[k][18]),
        #                 str(self.calcul_data[k][19]), str(self.calcul_data[k][20]), str(self.calcul_data[k][21]),
        #                 str(self.calcul_data[k][22]), str(self.calcul_data[k][23]), str(self.calcul_data[k][24]),
        #                 str(self.calcul_data[k][25])))
        #     f.close()
        #     self.calcul_data.clear()
        #     self.calculator_event_loop.exit()
        elif sRQName == "거래량급증요청":
            for i in range(10): # 7개 1분 5분
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                        "종목코드")  # 출력 : 종목코드
                code = code.strip()
                if code is "":
                    break
#                if (i >= 3 and i <= 7):
                self.enormous_code_list.append(code)
            folderpath = "files/" + self.cur_date
            if not os.path.isdir(folderpath):
                os.mkdir(folderpath)
            filepath = folderpath + "/" + self.cur_date + ".txt"
            f = open(filepath, "a", encoding="utf8")
            f.write("%s\t" % (str(self.cur_time)))
            for code in (self.enormous_code_list):
                f.write("%s\t" % (str(code)))
            f.write("\n")
            f.close()
            self.calculator_event_loop.exit()
        elif sRQName == "PROJ거래량급증요청":
            for i in range(10):  # 7개 1분 5분
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                        "종목코드")  # 출력 : 종목코드
                code = code.strip()
                if code is "":
                    break
                #                if (i >= 3 and i <= 7):
                self.enormous_code_list.append(code)
        elif sRQName == "거래량이전일급증요청":
            for code in self.enormous_code_list:
                if self.ten_cal_dict[code]["주식개수"] == 0:
                    self.dynamicCall("SetRealRemove(QString, QString)", str(int(self.ten_cal_dict[code]["스크린번호"])), code)
                    del self.ten_cal_dict[code]
                    self.enormous_code_list.remove(code)
            for i in range(10):  # 7개 1분 5분
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                        "종목코드")  # 출력 : 종목코드
                code = code.strip()
                if code is "":
                    break
                #                if (i >= 3 and i <= 7):
                if code in self.enormous_code_list:
                    continue
                self.enormous_code_list.append(code)
                tempscreencode = str(3000 + (self.temp_len_code % 90))
                #self.dynamicCall("DisconnectRealData(QString)", tempscreencode)
                self.logging.logger.debug(
                    "%s / %s : Stock Code : %s is registered " % (self.temp_len_code + 1, len(self.enormous_code_list), code))
                self.dynamicCall("SetRealReg(QString, QString, QString, QString)", tempscreencode, code, "41", "0")
                self.ten_cal_dict[code] = {}
                self.ten_cal_dict[code].update({"계산데이터": []})
                self.ten_cal_dict[code].update({"입력데이터": []})
                self.ten_cal_dict[code].update({"주식개수": 0})
                self.ten_cal_dict[code].update({"실제주식개수": 0})
                self.ten_cal_dict[code].update({"스크린번호": str(int(tempscreencode))})
                self.ten_cal_dict[code].update({"주문용스크린번호": str(6000)})
                self.temp_len_code += 1
                self.calculator_event_loop.exit()
        elif sRQName == "거래량10분급증요청":
            for code in self.enormous_code_list:
                if self.ten_cal_dict[code]["주식개수"] == 0:
                    del self.ten_cal_dict[code]
                    self.enormous_code_list.remove(code)
            for i in range(10):  # 7개 1분 5분
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                        "종목코드")  # 출력 : 종목코드
                code = code.strip()
                if code is "":
                    break
                #                if (i >= 3 and i <= 7):
                if code in self.enormous_code_list:
                    continue
                self.enormous_code_list.append(code)
                tempscreencode = str(3000 + (self.temp_len_code % 90))
                self.logging.logger.debug(
                    "%s / %s : Stock Code : %s is registered " % (self.temp_len_code + 1, len(self.enormous_code_list), code))
                self.ten_cal_dict[code] = {}
                self.ten_cal_dict[code].update({"주식개수": 0})
                self.ten_cal_dict[code].update({"실제주식개수": 0})
                self.ten_cal_dict[code].update({"스크린번호": str(int(tempscreencode))})
                self.ten_cal_dict[code].update({"주문용스크린번호": str(6000)})
                self.temp_len_code += 1
                self.calculator_event_loop.exit()
        # elif sRQName == "호가잔량급증요청":
        #     for i in range(7):
        #         code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
        #                                 "종목코드")  # 출력 : 종목코드
        #         code = code.strip()
        #         if code is "":
        #             break
        #         self.enormous_code_list.append(code)
        #     self.calculator_event_loop.exit()
        # elif sRQName == "호가잔량상위요청":
        #     for i in range(7):
        #         code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
        #                                 "종목코드")  # 출력 : 종목코드
        #         code = code.strip()
        #         if code is "":
        #             break
        #         self.enormous_code_list.append(code)
        #     self.calculator_event_loop.exit()
        # elif sRQName == "주식기본정보요청":
        #     self.logging.logger.debug("주식기본정보 요청 전")
        #     code = self.code
        #     code = code.strip()
        #     current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "매수최우선호가")  # 출력 : 090000
        #     current_price = current_price.strip().lstrip('+').lstrip('-')
        #     self.temp_enormous_code_dict[code].update({"현재가":current_price})
        #     self.logging.logger.debug("주식기본정보 요청 후")
        #     self.calculator_event_loop.exit()
        # elif sRQName == "주식5분호가요청":
        #     code = self.code
        #     code = code.strip()
        #     self.logging.logger.debug("종목 이름 %s" % code)# 일일 자료 이기에 누적 거래량은 의미가 없음
        #     data = []
        #     date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "호가잔량기준시간")  # 출력 : 090000
        #     mado = []
        #     masu = []
        #     mado_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "매도최우선호가")  # 출력 : 090000
        #     masu_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "매수최우선호가")  # 출력 : 090000
        #     tempstr = ""
        #     if mado_price == 0:
        #         mado_price = masu_price
        #     for i in range(10):
        #         if (i + 1) == 1:
        #             mado.append(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "매도최우선잔량"))
        #         elif (i + 1) == 6:
        #             tempstr = "매도" + str(i + 1) + "우선잔량"
        #             mado.append(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, tempstr))  # 출력 : 090000
        #         else:
        #             tempstr = "매도" + str(i + 1) + "차선잔량"
        #             mado.append(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, tempstr))
        #     for j in range(10):
        #         if (j + 1) == 1:
        #             masu.append(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "매수최우선잔량"))  # 출력 : 090000
        #         elif (j + 1) == 6:
        #             tempstr = "매수" + str(j + 1) + "우선잔량"
        #             masu.append(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, tempstr))
        #         else:
        #             tempstr = "매수" + str(j + 1) + "차선잔량"
        #             masu.append(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, tempstr))
        #     total_mado = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총매도잔량")  # 출력 : 090000
        #     total_masu = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총매수잔량")  # 출력 : 090000
        #     # 시고저종에 전부 -, +가 붙을 수 있으므로 제거
        #     date = date.strip()
        #     data.append("")
        #     data.append(date.strip())
        #     data.append(mado_price.strip().lstrip('+').lstrip('-'))
        #     data.append(masu_price.strip().lstrip('+').lstrip('-'))
        #     data.append(total_mado.strip().lstrip('+').lstrip('-'))
        #     data.append(total_masu.strip().lstrip('+').lstrip('-'))
        #     # 순서대로 최우선, 2, 3, 4, 5, 6, 7 8, 9, 10...
        #     for i in range(10):
        #         data.append(mado[i].strip().lstrip('+').lstrip('-'))
        #     for j in range(10):
        #         data.append(masu[j].strip().lstrip('+').lstrip('-'))
        #     data.append("")
        #     # 임시 data["", 체결시간(090000), 현재가(+-10850), 거래량(15000), 체결강도(78.51), ""]
        #     self.logging.logger.debug("데이터 사전에 저장 전")
        #     if code not in self.temp_enormous_code_dict:
        #         self.temp_enormous_code_dict.update({code: {}})
        #     self.temp_enormous_code_dict[code].update({"data_set": data.copy()})
        #     self.logging.logger.debug("데이터 사전 저장 완료")
        #     self.calculator_event_loop.exit()
        # elif sRQName == "일별거래상세요청":
        #     continue_flag = True
        #     code = self.code
        #     code = code.strip()
        #     self.logging.logger.debug("종목 이름 %s" % code)
        #     cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
        #     self.logging.logger.debug("남은 수 %s" % cnt)
        #     for i in range(cnt):
        #         # 일일 자료 이기에 누적 거래량은 의미가 없음
        #         data = []
        #         date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
        #                                 "일자")  # 출력 : 090000
        #         current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
        #                                          "종가")  # 출력 : 10850 or -10850
        #         volume = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
        #                                        "거래량")  # 출력 : 12343125
        #         bef_volume = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
        #                                        "장전거래량")  # 출력 : 12343125
        #         aft_volume = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
        #                                        "장후거래량")  # 출력 : 12343125
        #         moneyvolume = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
        #                                   "거래대금")  # 출력 : 12343125
        #         bef_moneyvolume = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
        #                                        "장전거래대금")  # 출력 : 12343125
        #         aft_moneyvolume = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
        #                                        "장후거래대금")  # 출력 : 12343125
        #         bef_volume_weight = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
        #                                   "장전거래비중")  # 출력 : 12343125
        #         aft_volume_weight = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
        #                                              "장후거래비중")  # 출력 : 12343125
        #         bef_moneyvolume_weight = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
        #                                   "장전거래대금비중")  # 출력 : 12343125
        #
        #         aft_moneyvolume_weight = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
        #                                              "장후거래대금비중")  # 출력 : 12343125
        #         # 시고저종에 전부 -, +가 붙을 수 있으므로 제거
        #         date = date.strip()
        #         # date = "20200707090000"
        #         # real_date "20200707"
        #         # real_time "090000"
        #         # real_date = date[0:8]
        #         # real_time = date[8:]
        #         real_date = date
        #         # limit_start = "20200701"
        #         # limit_end = "20200930"
        #         limit_start = "20201001"
        #         limit_end = "20201031"
        #         # 문제점 : 날짜가 바뀌면 어떻게 할 것?? -> 당일전일체결은 날짜가 바뀌지 않음
        #         # 항상 최신의 날짜부터 받아오기 때문에, 끝 날짜보다 높은 날짜는 필요없음
        #         # if real_date > self.end_date:
        #         #     continue
        #         # 원하는 날짜의 데이터 중 9시 ~ 15시 data만 calcul_data list에 저장
        #         if real_date > limit_end:
        #             continue
        #         if real_date <= limit_start:
        #             continue_flag = False
        #         if real_date < limit_start:
        #             continue
        #         data.append("")
        #         data.append(date.strip())
        #         data.append(current_price.strip().lstrip('+').lstrip('-'))
        #         data.append(volume.strip().lstrip('+').lstrip('-'))
        #         data.append(bef_volume.strip().lstrip('+').lstrip('-'))
        #         data.append(aft_volume.strip().lstrip('+').lstrip('-'))
        #         data.append(moneyvolume.strip().lstrip('+').lstrip('-'))
        #         data.append(bef_moneyvolume.strip().lstrip('+').lstrip('-'))
        #         data.append(aft_moneyvolume.strip().lstrip('+').lstrip('-'))
        #         data.append(bef_volume_weight.strip().lstrip('+').lstrip('-'))
        #         data.append(aft_volume_weight.strip().lstrip('+').lstrip('-'))
        #         data.append(bef_moneyvolume_weight.strip().lstrip('+').lstrip('-'))
        #         data.append(aft_moneyvolume_weight.strip().lstrip('+').lstrip('-'))
        #         data.append("")
        #         # 임시 data["", 체결시간(090000), 현재가(+-10850), 거래량(15000), 체결강도(78.51), ""]
        #         self.calcul_data.append(data.copy())
        #     # 09000 ~ 15:~~ 까지 전부 받아옴
        #     if (sPrevNext == "2") & (continue_flag):
        #         self.logging.logger.debug("현재 분봉수 %s" % len(self.calcul_data))
        #         self.get_day_new_data_kiwoom_db(code=code, sPrevNext=sPrevNext)
        #     else:
        #         self.logging.logger.debug("총 분봉수 %s" % len(self.calcul_data))
        #         # folderpath = "files/daysdata"
        #         #folderpath = "files/daysnewdata"
        #         folderpath = "files/daysnewtestdata"
        #         if not os.path.isdir(folderpath):
        #             os.mkdir(folderpath)
        #         filepath = folderpath + "/" + code + ".txt"
        #         f = open(filepath, "w", encoding="utf8")
        #         for k in range(len(self.calcul_data)):
        #             f.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
        #                 str(self.calcul_data[k][1]), str(self.calcul_data[k][2]), str(self.calcul_data[k][3]),
        #                 str(self.calcul_data[k][4]), str(self.calcul_data[k][5]), str(self.calcul_data[k][6]),
        #                 str(self.calcul_data[k][7]), str(self.calcul_data[k][8]), str(self.calcul_data[k][9]),
        #                 str(self.calcul_data[k][10]), str(self.calcul_data[k][11]), str(self.calcul_data[k][12])))
        #         f.close()
        #         self.calcul_data.clear()
        #         self.calculator_event_loop.exit()
        # elif sRQName == "텍스트일별거래상세요청": ### 잠정 폐쇄
        #     code = self.code
        #     code = code.strip()
        #     self.logging.logger.debug("종목 이름 %s" % code)
        #     cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
        #     self.logging.logger.debug("남은 수 %s" % cnt)
        #     # 일일 자료 이기에 누적 거래량은 의미가 없음
        #     current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종가")  # 출력 : 10850 or -10850
        #     self.text_dict[code].update({"종가" : current_price.strip().lstrip('+').lstrip('-')})
        #     # 임시 data["", 체결시간(090000), 현재가(+-10850), 거래량(15000), 체결강도(78.51), ""]
        #     self.calculator_event_loop.exit()
        # elif sRQName == "텍스트주식분봉차트조회":
        #     current_time = self.current_time
        #     code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
        #     code = code.strip()
        #     self.logging.logger.debug("종목 이름 %s" % code)
        #     cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
        #     self.logging.logger.debug("남은 분봉수 %s" % cnt)
        #     current_price = 0
        #     next_flag = False
        #     for i in range(cnt):
        #         date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결시간")  # 출력 : 20200622090000
        #         date = date.strip()
        #         # date = "20200707090000"
        #         # real_date "20200707"
        #         # real_hour "09"
        #         # real_min = "00"
        #         real_date = str(date[0:8])
        #         real_hour = int(date[8:10])
        #         real_min = int(date[10:12])
        #         #self.logging.logger.debug("%s %d %d" % (real_date, real_hour, real_min))
        #         # 원하는 날짜의 데이터 중 9시 ~ 15시 data만 calcul_data list에 저장
        #         if real_date != self.target_date:
        #             continue
        #         cur_hour = int(current_time[0:2])
        #         cur_min = int(current_time[2:4])
        #         #self.logging.logger.debug("%d %d " % (cur_hour, cur_min))
        #         if real_hour == cur_hour + 1:
        #             if (cur_min + self.minute_gap) - 60 >= real_min: ## 10분 후임 (58 + 10) - 60 >= 9
        #                 current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")  # 출력 : 10850
        #                 break
        #         elif real_hour == cur_hour:
        #             if real_min - cur_min <= self.minute_gap: ## (18 - 8) <= 10
        #                 current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")  # 출력 : 10850
        #                 break
        #         else:
        #             continue
        #     if current_price == 0:
        #         next_flag = True
        #     if (sPrevNext == "2") & (next_flag):
        #         self.text_query_data(code=code, sPrevNext=sPrevNext)
        #     else:
        #         self.text_dict[current_time].update({"종가": current_price.strip().lstrip('+').lstrip('-')})
        #         self.calculator_event_loop.exit()
        # elif sRQName == "주식5분봉일일차트조회":
        #     continue_flag = True
        #     code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
        #     code = code.strip()
        #     self.logging.logger.debug("종목 이름 %s" % code)
        #     cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
        #     self.logging.logger.debug("남은 분봉수 %s" % cnt)
        #     for i in range(cnt):
        #         data = []
        #         date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
        #                                 "체결시간")  # 출력 : 20200622090000
        #         start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
        #                                        "시가")  # 출력 : 10850
        #         high_price = self.dynamicCall("GetCommData(QSring, QString, int, QString)", sTrCode, sRQName, i,
        #                                       "고가")  # 출력 : 10900
        #         low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
        #                                      "저가")  # 출력 : 10700
        #         current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
        #                                          "현재가")  # 출력 : 10850
        #         volume = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
        #                                   "거래량")  # 출력 : 15
        #         # 시고저종에 전부 -, +가 붙을 수 있으므로 제거
        #         date = date.strip()
        #         # date = "20200707090000"
        #         # real_date "20200707"
        #         # real_time "090000"
        #         real_date = date[0:8]
        #         real_time = date[8:]
        #         limit_start = "090000"
        #         limit_end = "150000"
        #         # 문제점 : 날짜가 바뀌면 어떻게 할 것??
        #         # 항상 최신의 날짜부터 받아오기 때문에, 끝 날짜보다 높은 날짜는 필요없음
        #         if real_date > self.end_date:
        #             continue
        #         # 원하는 날짜의 데이터 중 9시 ~ 15시 data만 calcul_data list에 저장
        #         if real_time > limit_end or real_time < limit_start:
        #             continue
        #         # 현재의 데이터는 일단 end_date와 똑같고, 이 경우 real_date가 여기까지 오려면 동일해야함
        #         # 그러므로 동일하지 않으면, 앞에 모든 행동이 끝났고, 새로운 날짜의 차례라는 것
        #         if self.cur_date != real_date:
        #             self.logging.logger.debug("총 분봉수 %s" % len(self.calcul_data))
        #             folderpath = "files/" + code
        #             if not os.path.isdir(folderpath):
        #                 os.mkdir(folderpath)
        #             filepath = "files/" + code +"/" + code + "_" + self.cur_date + "_" + "fivemin_data.txt"
        #             f = open(filepath, "w", encoding="utf8")
        #             for k in range(len(self.calcul_data)):
        #                 f.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (
        #                     str(self.calcul_data[k][1]), str(self.calcul_data[k][2]), str(self.calcul_data[k][3]),
        #                     str(self.calcul_data[k][4]), str(self.calcul_data[k][5]), str(self.calcul_data[k][6])))
        #             f.close()
        #             self.calcul_data.clear()
        #             # real_date가 시작 날짜 이전의 데이터로 넘어갈 수도 있기 때문에
        #             # 이 경우 for문 종료 및 continue_flag 해제
        #             if real_date < self.start_date:
        #                 continue_flag = False
        #                 break
        #             # 끝 날짜의 모든 기록 종료 후 calcul_data 초기화 및 cur_date 변경
        #             self.cur_date = real_date
        #         data.append("")
        #         data.append(date.strip())
        #         data.append(start_price.strip().lstrip('+').lstrip('-'))
        #         data.append(high_price.strip().lstrip('+').lstrip('-'))
        #         data.append(low_price.strip().lstrip('+').lstrip('-'))
        #         data.append(current_price.strip().lstrip('+').lstrip('-'))
        #         data.append(volume.strip())
        #         data.append("")
        #         # 임시 data["", 체결시간(20200622090000), 시가(+-10850), 고가(+-10900), 저가(+-10700), 종가 = 현재가(+-10850), 거래량(15), ""]
        #         self.calcul_data.append(data.copy())
        #
        #     if (sPrevNext == "2") & (continue_flag):
        #         self.logging.logger.debug("현재 분봉수 %s" % len(self.calcul_data))
        #         self.fivemin_oneday_kiwoom_db(code=code, sPrevNext=sPrevNext)
        #     else:
        #         # self.cur_date가 도는 동안 변형되므로 다시 초기화
        #         self.cur_date = self.end_date
        #         self.calculator_event_loop.exit()
        # elif sRQName == "당일전일체결요청":
        #     continue_flag = True
        #     #code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
        #     #code = code.strip()
        #     code = self.code
        #     self.logging.logger.debug("종목 이름 %s" % code)
        #     cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
        #     self.logging.logger.debug("남은 분봉수 %s" % cnt)
        #     for i in range(cnt):
        #         data = []
        #         time = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시간")  # 출력 : 090000
        #         current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")  # 출력 : 10850 or -10850
        #         #volume = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결거래량")  # 출력 : 15
        #         accu_volume = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "누적거래량")  # 출력 : 12343125
        #         chegeul = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결강도")  # 출력 : 79.35
        #         # 시고저종에 전부 -, +가 붙을 수 있으므로 제거
        #         time = time.strip()
        #         # date = "20200707090000"
        #         # real_date "20200707"
        #         # real_time "090000"
        #         #real_date = date[0:8]
        #         #real_time = date[8:]
        #         real_time = time
        #         limit_start = "090000"
        #         limit_end = "150000"
        #         # 문제점 : 날짜가 바뀌면 어떻게 할 것?? -> 당일전일체결은 날짜가 바뀌지 않음
        #         # 항상 최신의 날짜부터 받아오기 때문에, 끝 날짜보다 높은 날짜는 필요없음
        #         # if real_date > self.end_date:
        #         #     continue
        #         # 원하는 날짜의 데이터 중 9시 ~ 15시 data만 calcul_data list에 저장
        #         if real_time > limit_end:
        #             continue
        #         if real_time <= limit_start:
        #             continue_flag = False
        #         if real_time < limit_start:
        #             continue
        #         data.append("")
        #         data.append(time.strip())
        #         data.append(current_price.strip().lstrip('+').lstrip('-'))
        #         #data.append(volume.strip().lstrip('+').lstrip('-'))
        #         data.append(accu_volume.strip().lstrip('+').lstrip('-'))
        #         data.append(chegeul.strip().lstrip('+').lstrip('-'))
        #         data.append("")
        #         # 임시 data["", 체결시간(090000), 현재가(+-10850), 거래량(15000), 체결강도(78.51), ""]
        #         self.calcul_data.append(data.copy())
        #     if (sPrevNext == "2") & (continue_flag):
        #         self.logging.logger.debug("현재 분봉수 %s" % len(self.calcul_data))
        #         self.onemin_chegeul_kiwoom_db(code=code, sPrevNext=sPrevNext)
        #     else:
        #         self.logging.logger.debug("총 분봉수 %s" % len(self.calcul_data))
        #         folderpath = "files/" + self.cur_date
        #         if not os.path.isdir(folderpath):
        #             os.mkdir(folderpath)
        #         filepath = folderpath + "/" + code + ".txt"
        #         f = open(filepath, "w", encoding="utf8")
        #         for k in range(len(self.calcul_data)):
        #             f.write("%s\t%s\t%s\t%s\n" % (
        #                 str(self.calcul_data[k][1]), str(self.calcul_data[k][2]), str(self.calcul_data[k][3]),
        #                 str(self.calcul_data[k][4])))
        #         f.close()
        #         self.calcul_data.clear()
        #         self.calculator_event_loop.exit()
        # elif sRQName == "최초누락거래량확인":
        #     continue_flag = True
        #     #code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
        #     #code = code.strip()
        #     code = self.code
        #     self.logging.logger.debug("종목 이름 %s" % code)
        #     cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
        #     self.logging.logger.debug("남은 수 %s" % cnt)
        #     for i in range(cnt):
        #         data = []
        #         time = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시간")  # 출력 : 090000
        #         volume = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결거래량")  # 출력 : 15
        #         priormado = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "우선매도호가단위")  # 출력 : 12343125
        #         # 시고저종에 전부 -, +가 붙을 수 있으므로 제거
        #         volume = volume.strip()
        #         priormado = priormado.strip().lstrip('+').lstrip('-')
        #         if not float(priormado) == 0:
        #             self.beforevol = volume
        #         elif float(volume) <= 0:
        #             self.sumalphab += abs(float(volume))
        #         elif float(volume) >= 0:
        #             self.sumalphaa += abs(float(volume))
        #         else:
        #             self.logging.logger.debug("에러발생")
        #     if (sPrevNext == "2"):
        #         self.chegeul_calcul_kiwoom_db(code=code, sPrevNext=sPrevNext)
        #     else:
        #         self.logging.logger.debug("%s %s %s" % (str(self.beforevol), str(self.sumalphaa), str(self.sumalphab)))
        #         folderpath = "files/" + self.cur_date + "/sup_data"
        #         if not os.path.isdir(folderpath):
        #             os.mkdir(folderpath)
        #         filepath = folderpath + "/" + code + ".txt"
        #         f = open(filepath, "w", encoding="utf8")
        #         f.write("%s\n%s\n%s\n" % (str(self.beforevol), str(self.sumalphaa), str(self.sumalphab)))
        #         f.close()
        #         self.calcul_data.clear()
        #         self.calculator_event_loop.exit()
        elif sRQName == "주식분봉차트조회":
            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            code = code.strip()
            self.logging.logger.debug("종목 이름 %s" % code)
            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            self.logging.logger.debug("남은 분봉수 %s" % cnt)

            for i in range(cnt):
                data = []
                date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                        "체결시간")  # 출력 : 20200622090000
                start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                               "시가")  # 출력 : 10850
                high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                              "고가")  # 출력 : 10900
                low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                             "저가")  # 출력 : 10700
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                 "현재가")  # 출력 : 10850
                volume = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                          "거래량")  # 출력 : 15
                # 시고저종에 전부 -, +가 붙을 수 있으므로 제거
                data.append("")
                data.append(date.strip())
                data.append(start_price.strip().lstrip('+').lstrip('-'))
                data.append(high_price.strip().lstrip('+').lstrip('-'))
                data.append(low_price.strip().lstrip('+').lstrip('-'))
                data.append(current_price.strip().lstrip('+').lstrip('-'))
                data.append(volume.strip())
                data.append("")
                # 임시 data["", 체결시간(20200622090000), 시가(+-10850), 고가(+-10900), 저가(+-10700), 종가 = 현재가(+-10850), 거래량(15), ""]
                self.calcul_data.append(data.copy())

            # 3분봉
            # 한 번 call에 900개까지 (0 ~ 899)
            # 임의의 데이터 수 : 900 * 8 = 7200 = 120 * 60 = 60일치 = 32(batch_size) * 225
            # 약 day_count / 20 달의 3분봉데이터를 저장
            # 하루가 120개
            # 일주일은 600개
            # 학습기가 내리는 판단은 120번...
            # 1분봉
            # 하루에 09:00 ~ 15:30 -> 6시간 30분 ->
            # 하루에 360개...로 착각
            # 실제로는 09:00 ~ 15:19까지가 정상적인 거래
            # 넉넉잡아 09:00 ~ 15:00까지로 제한해도 좋을듯
            # 데이터 수 : 360 * 20 = 7200 = 900 * 8
            # 20일 == 1달(영업일 기준 대략)

            day_count = 30
            update_count = int(day_count * 360)
            # calcul_data에 7200개가 들어갈 때까지 반복
            if (sPrevNext == "2") & (len(self.calcul_data) < update_count):
                self.logging.logger.debug("현재 분봉수 %s" % len(self.calcul_data))
                self.onemin_kiwoom_db(code=code, sPrevNext=sPrevNext)
            else:
                # calcul_data에 7200까지 적재하거나 그것보다 적은 분봉데이터인경우
                self.logging.logger.debug("총 분봉수 %s" % len(self.calcul_data))
                filepath = "kiwoom/ppo_learning/" + self.cur_date + "/" + code + "_" + "min_data.txt"
                f = open(filepath, "w", encoding="utf8")
                for k in range(len(self.calcul_data)):
                    f.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (
                    str(self.calcul_data[k][1]), str(self.calcul_data[k][2]), str(self.calcul_data[k][3]),
                    str(self.calcul_data[k][4]), str(self.calcul_data[k][5]), str(self.calcul_data[k][6])))
                f.close()
                self.calcul_data.clear()
                self.calculator_event_loop.exit()
        elif sRQName == "PROJ분별호가조회":
            pass

    def stop_screen_cancel(self, sScrNo=None):
        self.dynamicCall("DisconnectRealData(QString)", sScrNo) # 스크린번호 연결 끊기

    def get_code_list_by_market(self, market_code):
        '''
        종목코드 리스트 받기
        #0:장내, 10:코스닥

        :param market_code: 시장코드 입력
        :return:
        '''
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market_code)
        code_list = code_list.split(';')[:-1]
        return code_list

    def calculator_fnc(self):
        '''
        종목 분석관련 함수 모음
        :return:
        '''

        code_list = self.get_code_list_by_market("0")
        self.logging.logger.debug("장내시장 갯수 %s " % len(code_list))

        for idx, code in enumerate(code_list):
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock)  # 스크린 연결 끊기
            self.logging.logger.debug("%s / %s : Jangnaemarket Stock Code : %s is updating... " % (idx + 1, len(code_list), code))
            self.day_kiwoom_db(code=code)

    def get_code_list_by_txt(self):
        #텍스트로 각 행당 0열에 주식코드가 있다(이 텍스트는 전일거래량상위요청에서 얻어낸 것)
        code_list = []
        # 9시 10분 파일 기준
        #filepath = "files/selected/" + self.collect_cur_date + ".txt"
        # 3시 30분 파일 기준
        #filepath = "files/selected/" + self.collect_cur_date + "_learning.txt"
        filepath = "files/20210727/20210727.txt"
        # 없는 경우 넘어감
        if not os.path.isfile(filepath):
            return code_list
        f = open(filepath, "r", encoding="utf8")
        lines = f.readlines()
        for line in lines:
            code_list.append(line.strip())
        f.close()
        return code_list

    def get_code_list_by_sampletxt(self):
        #텍스트로 각 행당 0열에 주식코드가 있다(이 텍스트는 전일거래량상위요청에서 얻어낸 것)
        code_list = []
        # 9시 10분 파일 기준
        #filepath = "files/selected/" + self.collect_cur_date + ".txt"
        # 3시 30분 파일 기준
        #filepath = "files/selected/" + self.collect_cur_date + "_learning.txt"
        # folderpath = "ppo/" + self.cur_date
        # filepath = folderpath + "/" + self.cur_date + ".txt"
        folderpath = "kiwoom/ppo_learning/" + self.cur_date
        if not os.path.isdir(folderpath):
            os.mkdir(folderpath)
        filepath = folderpath + "/" + self.cur_date + "_27_rotate_50.txt"
        # 없는 경우 넘어감
        if not os.path.isfile(filepath):
            return code_list
        f = open(filepath, "r", encoding="utf8")
        lines = f.readlines()
        for line in lines:
            #code_list = line.strip().split("\t")
            code_list.append(line.strip())
        f.close()
        return code_list

    def get_code_list_by_daysampletxt(self):
        #텍스트로 각 행당 0열에 주식코드가 있다(이 텍스트는 전일거래량상위요청에서 얻어낸 것)
        code_list = []
        # 9시 10분 파일 기준
        #filepath = "files/selected/" + self.collect_cur_date + ".txt"
        # 3시 30분 파일 기준
        #filepath = "files/selected/" + self.collect_cur_date + "_learning.txt"
        filepath = "ppo/daysample.txt"
        # 없는 경우 넘어감
        if not os.path.isfile(filepath):
            return code_list
        f = open(filepath, "r", encoding="utf8")
        lines = f.readlines()
        for line in lines:
            code_list.append(line.strip())
        f.close()
        return code_list

    def get_code_list_by_daytxt(self):
        #텍스트로 각 행당 0열에 주식코드가 있다(이 텍스트는 전일거래량상위요청에서 얻어낸 것)
        code_list = []
        # 9시 10분 파일 기준
        filepath = "files/selected/" + self.collect_cur_date + ".txt"
        # 3시 30분 파일 기준
        #filepath = "files/selected/" + "eight_ten_three_month_big.txt"
        # 없는 경우 넘어감
        if not os.path.isfile(filepath):
            return code_list
        f = open(filepath, "r", encoding="utf8")
        lines = f.readlines()
        for line in lines:
            code_list.append(line.strip())
        f.close()
        return code_list

    def get_code_list_by_mytxt(self):
        #텍스트로 각 행당 0열에 주식코드가 있다(이 텍스트는 전일거래량상위요청에서 얻어낸 것)
        code_list = []
        # 9시 10분 파일 기준
        #filepath = "files/selected/" + self.collect_cur_date + ".txt"
        # 3시 30분 파일 기준
        #filepath = "files/selected/" + "eight_ten_three_month_big.txt"
        filepath = "files/selected/20201202.txt"
        # 없는 경우 넘어감
        if not os.path.isfile(filepath):
            return code_list
        f = open(filepath, "r", encoding="utf8")
        lines = f.readlines()
        for line in lines:
            code_list.append(line.strip())
        f.close()
        return code_list

    def datacollect_fnc(self):
        '''
        상위 50개의 거래량 종목들을 받고
        종목 분석관련 함수 모음
        :return:
        '''

        code_list = self.get_code_list_by_txt()
        self.logging.logger.debug("txt 종목 갯수 %s " % len(code_list))

        for idx, code in enumerate(code_list):
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock)  # 스크린 연결 끊기
            self.logging.logger.debug("%s / %s : Stock Code : %s is updating... " % (idx + 1, len(code_list), code))
            self.onemin_kiwoom_db(code=code)
            #self.OSSPday_kiwoom_db(code=code)

    def get_code_list_by_temp(self):
        # 텍스트로 각 행당 0열에 주식코드가 있다(이 텍스트는 전일거래량상위요청에서 얻어낸 것)
        code_list = []
        # 9시 10분 파일 기준
        # filepath = "files/selected/" + self.collect_cur_date + ".txt"
        # 3시 30분 파일 기준
        # filepath = "files/selected/" + self.collect_cur_date + "_learning.txt"
        filepath = "kiwoom/temp_code_list.txt"
        # 없는 경우 넘어감
        if not os.path.isfile(filepath):
            return code_list
        f = open(filepath, "r", encoding="utf8")
        lines = f.readlines()
        for line in lines:
            code_list.append(line.strip())
        f.close()
        return code_list

    def porjdatacollect_fnc(self):
        code_list = self.get_code_list_by_temp()
        self.logging.logger.debug("txt 종목 갯수 %s " % len(code_list))
        for idx, code in enumerate(code_list):
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock)  # 스크린 연결 끊기
            self.logging.logger.debug("%s / %s : Stock Code : %s is updating... " % (idx + 1, len(code_list), code))
            self.projdata_kiwoom_db(code=code)

    def datacollect_sample(self):
        code_list = self.get_code_list_by_sampletxt() # txt -> codelist
        self.logging.logger.debug("txt 종목 갯수 %s " % len(code_list))

        for idx, code in enumerate(code_list):
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock)  # 스크린 연결 끊기
            self.logging.logger.debug("%s / %s : Stock Code : %s is updating... " % (idx + 1, len(code_list), code))
            self.onemin_kiwoom_db(code=code)

    def datacollectplus_fnc(self):
        code_list = self.get_code_list_by_txt()
        self.logging.logger.debug("txt 종목 갯수 %s " % len(code_list))
        for idx, code in enumerate(code_list):
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock)  # 스크린 연결 끊기
            self.logging.logger.debug(
                "%s / %s : Stock Code : %s is updating... " % (idx + 1, len(code_list), code))
            self.code = code
            self.fivemin_oneday_kiwoom_db(code=code)

    def datacollectplus_upgrade(self):
        code_list = self.get_code_list_by_txt()
        self.logging.logger.debug("txt 종목 갯수 %s " % len(code_list))

        for idx, code in enumerate(code_list):
            self.logging.logger.debug(
                "%s / %s : Stock Code : %s is updating... " % (idx + 1, len(code_list), code))
            # 9시 10분 기준 (사실 필요없음)
            filepath = "files/" + self.collect_cur_date + "/" + code + ".txt"
            # 3시 30분 기준 (있으면 좋음)
            #filepath = "files/" + self.collect_cur_date + "/" + code + ".txt"
            # 이미 있으면 넘어감
            if os.path.isfile(filepath):
                continue
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock)  # 스크린 연결 끊기
            self.code = code
            self.onemin_chegeul_kiwoom_db(code=code)

    def datacollectplus_day(self):
        code_list = self.get_code_list_by_daytxt()
        self.logging.logger.debug("txt 종목 갯수 %s " % len(code_list))

        for idx, code in enumerate(code_list):
            self.logging.logger.debug(
                "%s / %s : Stock Code : %s is updating... " % (idx + 1, len(code_list), code))
            # 9시 10분 기준 (사실 필요없음)
            #filepath = "files/daysdata/" + code + ".txt"
            filepath = "files/testdaysdata/" + code + ".txt"
            # 이미 있으면 넘어감
            if os.path.isfile(filepath):
                continue
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock)  # 스크린 연결 끊기
            self.code = code
            self.get_day_cheguel_kiwoom_db(code=code)

    def datacollectplus_new_data_day(self):
        code_list = self.get_code_list_by_daytxt()
        self.logging.logger.debug("txt 종목 갯수 %s " % len(code_list))

        for idx, code in enumerate(code_list):
            self.logging.logger.debug(
                "%s / %s : Stock Code : %s is updating... " % (idx + 1, len(code_list), code))
            # 9시 10분 기준 (사실 필요없음)
            #filepath = "files/daysdata/" + code + ".txt"
            #filepath = "files/daysnewdata/" + code + ".txt"
            filepath = "files/daysnewtestdata/" + code + ".txt"
            # 이미 있으면 넘어감
            if os.path.isfile(filepath):
                continue
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock)  # 스크린 연결 끊기
            self.code = code
            self.get_day_new_data_kiwoom_db(code=code)

    def datacollectplus_hogas(self, code_list):
        for idx, code in enumerate(code_list):
            self.logging.logger.debug(
                "%s / %s : Stock Code : %s is updating... " % (idx + 1, len(code_list), code))
            # 9시 10분 기준 (사실 필요없음)
            #filepath = "files/daysdata/" + code + ".txt"
            #filepath = "files/testdaysdata/" + code + ".txt"
            # 이미 있으면 넘어감
            #filepath = "files/" + self.collect_cur_date + "/" + code + ".txt"
            # if os.path.isfile(filepath):
            #     continue
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock)  # 스크린 연결 끊기
            self.code = code
            self.get_day_hogas_kiwoom_db(code=code)

    def supdatacollect(self):
        code_list = self.get_code_list_by_txt()
        self.logging.logger.debug("txt 종목 갯수 %s " % len(code_list))
        for idx, code in enumerate(code_list):
            self.beforevol = 0
            self.sumalphaa = 0  # 매수체결량 (+)
            self.sumalphab = 0  # 매도체결량 (-)
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock)  # 스크린 연결 끊기
            self.logging.logger.debug(
                "%s / %s : Stock Code : %s is updating... " % (idx + 1, len(code_list), code))
            self.code = code
            self.chegeul_calcul_kiwoom_db(code=code)

    def day_kiwoom_db(self, code=None, date=None, sPrevNext="0"):
        QTest.qWait(3600) #3.6초마다 딜레이를 준다.
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
        if date != None:
            self.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식일봉차트조회", "opt10081", sPrevNext, self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
        self.calculator_event_loop.exec_()

    def OSSPday_kiwoom_db(self, code=None, date=None, sPrevNext="0"):
        QTest.qWait(3600) #3.6초마다 딜레이를 준다.
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
        if date != None:
            self.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "OSSP주식일봉차트조회", "opt10081", sPrevNext, self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
        self.calculator_event_loop.exec_()

    def threemin_kiwoom_db(self, code=None, minute="10", sPrevNext="0"):
        QTest.qWait(4000)  # 3.6초(4초로 변경)마다 딜레이를 준다.
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "틱범위", minute)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식분봉차트조회", "opt10080", sPrevNext, self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
        self.calculator_event_loop.exec_()

    def onemin_kiwoom_db(self, code=None, minute="1", sPrevNext="0"):
        QTest.qWait(4000)  # 3.6초(4초로 변경)마다 딜레이를 준다.
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "틱범위", minute)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식분봉차트조회", "opt10080", sPrevNext, self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
        self.calculator_event_loop.exec_()

    def projdata_kiwoom_db(self, code=None, minute="1", sPrevNext="0"):
        QTest.qWait(4000)  # 3.6초(4초로 변경)마다 딜레이를 준다.
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "틱범위", minute)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "PROJDATACOLLECT주식분봉차트조회", "opt10080", sPrevNext, self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
        self.calculator_event_loop.exec_()

    def proj30min_kiwoom_db(self, code=None, minute="1", sPrevNext="0"):
        #QTest.qWait(4000)  # 3.6초(4초로 변경)마다 딜레이를 준다.
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "틱범위", minute)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "PROJ30분봉차트조회", "opt10080", sPrevNext, self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
        self.calculator_event_loop.exec_()

    def ppo_onemin_kiwoom_db(self, code=None, minute="1", sPrevNext="0"):
        QTest.qWait(3600)  # 3.6초(4초로 변경)마다 딜레이를 준다.
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "틱범위", minute)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "PPO주식분봉차트조회", "opt10080", sPrevNext, self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
        self.calculator_event_loop.exec_()

    def get_hot_stock_kiwoom_db(self, start_rank="0", end_rank="100", sPrevNext="0"):
        QTest.qWait(4000)  # 3.6초(4초로 변경)마다 딜레이를 준다.
        #코스피 종목 중 전일 거래대금량순으로 상위 16위까지의 종목들을 가져옴
        self.dynamicCall("SetInputValue(QString, QString)", "시장구분", "000")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "2")
        self.dynamicCall("SetInputValue(QString, QString)", "순위시작", start_rank)
        self.dynamicCall("SetInputValue(QString, QString)", "순위끝", end_rank)
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "전일거래량상위요청", "opt10031", sPrevNext, self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
        self.calculator_event_loop.exec_()

    def get_pc_conclude_kiwoom_db(self, code=None, minute="1", sPrevNext="0"):
        QTest.qWait(4000)  # 3.6초(4초로 변경)마다 딜레이를 준다.
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "틱범위", minute)
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "체결강도추이시간별요청", "opt10046", sPrevNext, self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
        self.calculator_event_loop.exec_()

    def get_day_cheguel_kiwoom_db(self, code=None, sPrevNext="0"):
        QTest.qWait(4000)  # 3.6초(4초로 변경)마다 딜레이를 준다.
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "틱범위", "1")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "체결강도추이일별요청", "opt10047", sPrevNext,
                         self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
        self.calculator_event_loop.exec_()

    def get_day_new_data_kiwoom_db(self, code=None, sPrevNext="0"):
        QTest.qWait(4000)  # 3.6초(4초로 변경)마다 딜레이를 준다.
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        #self.dynamicCall("SetInputValue(QString, QString)", "틱범위", "1")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "일별거래상세요청", "opt10015", sPrevNext,
                         self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
        self.calculator_event_loop.exec_()

    def get_day_hogas_kiwoom_db(self, code=None, sPrevNext="0"):
        QTest.qWait(3600)  # 3.6초(4초로 변경)마다 딜레이를 준다.
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        #self.dynamicCall("SetInputValue(QString, QString)", "틱범위", "1")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식호가요청", "opt10004", sPrevNext, self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
        self.calculator_event_loop.exec_()

    def get_current_price_kiwoom_db(self, code=None, sPrevNext="0"):
        QTest.qWait(3600)  # 3.6초(4초로 변경)마다 딜레이를 준다.
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        # self.dynamicCall("SetInputValue(QString, QString)", "틱범위", "1")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식기본정보요청", "opt10004", sPrevNext,
                         self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
        self.calculator_event_loop.exec_()

    def get_5min_hogas_kiwoom_db(self, code=None, sPrevNext="0"):
        QTest.qWait(3600)  # 3.6초(4초로 변경)마다 딜레이를 준다.
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        # self.dynamicCall("SetInputValue(QString, QString)", "틱범위", "1")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식5분호가요청", "opt10004", sPrevNext,
                         self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
        self.calculator_event_loop.exec_()
    ####### 거래량급증 / 호가잔량급증 / 호가잔량상위 중 종목조건 "14"로 ETN+ETF 제외 가능
    def get_5min_datalist(self):
        #QTest.qWait(3600)  # 3.6초(4초로 변경)마다 딜레이를 준다.
        # 코스피 종목 중 전일 거래대금량순으로 상위 16위까지의 종목들을 가져옴
        self.dynamicCall("SetInputValue(QString, QString)", "시장구분", "000") # 코스피 001 코스닥 101
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1") # 조회구분 1 급증량 2 급증률
        self.dynamicCall("SetInputValue(QString, QString)", "시간구분", "1") # 1은 분 2는 전일
        self.dynamicCall("SetInputValue(QString, QString)", "거래량구분", "5") # 100만 주 이상 // 5천주 이상
        self.dynamicCall("SetInputValue(QString, QString)", "시간", "10") # 1분전과 비교
        self.dynamicCall("SetInputValue(QString, QString)", "종목조건", "14") # 0 전체 1 관리 종목 제외 5 증 100제외(이것으로 할 예정)
        self.dynamicCall("SetInputValue(QString, QString)", "가격구분", "0") # 5천원이상
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "거래량급증요청", "opt10023", "0",
                         self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
        self.calculator_event_loop.exec_()

    def get_30min_datalist(self):
        # 코스피 종목 중 전일 거래대금량순으로 상위 16위까지의 종목들을 가져옴
        self.dynamicCall("SetInputValue(QString, QString)", "시장구분", "000")  # 코스피 001 코스닥 101
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")  # 조회구분 1 급증량 2 급증률
        self.dynamicCall("SetInputValue(QString, QString)", "시간구분", "1")  # 1은 분 2는 전일
        self.dynamicCall("SetInputValue(QString, QString)", "거래량구분", "5")  # 100만 주 이상 // 5천주 이상
        self.dynamicCall("SetInputValue(QString, QString)", "시간", "30")  # 1분전과 비교
        self.dynamicCall("SetInputValue(QString, QString)", "종목조건", "14")  # 0 전체 1 관리 종목 제외 5 증 100제외(이것으로 할 예정)
        self.dynamicCall("SetInputValue(QString, QString)", "가격구분", "0")  # 5천원이상
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "PROJ거래량급증요청", "opt10023", "0",
                         self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
        self.calculator_event_loop.exec_()

    ####### 거래량급증 / 호가잔량급증 / 호가잔량상위 중 종목조건 "14"로 ETN+ETF 제외 가능
    def get_beforeday_min_datalist(self):
        #QTest.qWait(3600)  # 3.6초(4초로 변경)마다 딜레이를 준다.
        # 코스피 종목 중 전일 거래대금량순으로 상위 16위까지의 종목들을 가져옴
        self.dynamicCall("SetInputValue(QString, QString)", "시장구분", "000") # 코스피 001 코스닥 101
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1") # 조회구분 1 급증량 2 급증률
        self.dynamicCall("SetInputValue(QString, QString)", "시간구분", "1") # 1은 분 2는 전일
        self.dynamicCall("SetInputValue(QString, QString)", "거래량구분", "5") # 100만 주 이상 // 5천주 이상
        self.dynamicCall("SetInputValue(QString, QString)", "시간", "10") # 1분전과 비교
        self.dynamicCall("SetInputValue(QString, QString)", "종목조건", "14") # 0 전체 1 관리 종목 제외 5 증 100제외(이것으로 할 예정)
        self.dynamicCall("SetInputValue(QString, QString)", "가격구분", "0") # 5천원이상
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "거래량이전일급증요청", "opt10023", "0",
                         self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
        self.calculator_event_loop.exec_()

    def get_before10min_datalist(self):
        #QTest.qWait(3600)  # 3.6초(4초로 변경)마다 딜레이를 준다.
        # 코스피 종목 중 전일 거래대금량순으로 상위 16위까지의 종목들을 가져옴
        self.dynamicCall("SetInputValue(QString, QString)", "시장구분", "000") # 코스피 001 코스닥 101
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1") # 조회구분 1 급증량 2 급증률
        self.dynamicCall("SetInputValue(QString, QString)", "시간구분", "1") # 1은 분 2는 전일
        self.dynamicCall("SetInputValue(QString, QString)", "거래량구분", "5") # 100만 주 이상 // 5천주 이상
        self.dynamicCall("SetInputValue(QString, QString)", "시간", "10") # 1분전과 비교
        self.dynamicCall("SetInputValue(QString, QString)", "종목조건", "14") # 0 전체 1 관리 종목 제외 5 증 100제외(이것으로 할 예정)
        self.dynamicCall("SetInputValue(QString, QString)", "가격구분", "0") # 5천원이상
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "거래량10분급증요청", "opt10023", "0",
                         self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
        self.calculator_event_loop.exec_()

    def get_hogavast_datalist(self):
        QTest.qWait(3600)  # 3.6초(4초로 변경)마다 딜레이를 준다.
        # 코스피 종목 중 전일 거래대금량순으로 상위 16위까지의 종목들을 가져옴
        self.dynamicCall("SetInputValue(QString, QString)", "시장구분", "101") # 001 코스피 101 코스닥
        self.dynamicCall("SetInputValue(QString, QString)", "매매구분", "1")  # 매매구분 1 매수잔량 2 매도잔량
        self.dynamicCall("SetInputValue(QString, QString)", "정렬구분", "1")  # 정렬구분 1 급증량 2 급증률
        self.dynamicCall("SetInputValue(QString, QString)", "시간구분", "1")  # n분
        self.dynamicCall("SetInputValue(QString, QString)", "거래량구분", "5")  # 100만 주 이상 // 5천주 이상
        self.dynamicCall("SetInputValue(QString, QString)", "종목조건", "14")  # 0 전체 1 관리 종목 제외 5 증 100제외(이것으로 할 예정)
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "호가잔량급증요청", "opt10021", "0",
                         self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
        self.calculator_event_loop.exec_()

    def get_hogavastrank_datalist(self):
        QTest.qWait(3600)  # 3.6초(4초로 변경)마다 딜레이를 준다.
        # 코스피 종목 중 전일 거래대금량순으로 상위 16위까지의 종목들을 가져옴
        self.dynamicCall("SetInputValue(QString, QString)", "시장구분", "101") # 001 코스피 101 코스닥
        self.dynamicCall("SetInputValue(QString, QString)", "정렬구분", "2")  # 정렬구분 1 순매수잔량순 2 순매도잔량순 3 매수비율 4 매도비율
        self.dynamicCall("SetInputValue(QString, QString)", "거래량구분", "00100")  # 10만주 이상
        self.dynamicCall("SetInputValue(QString, QString)", "종목조건", "14")  # 0 전체 1 관리 종목 제외 5 증 100제외(이것으로 할 예정)
        self.dynamicCall("SetInputValue(QString, QString)", "신용조건", "0")  # 0 전체
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "호가잔량상위요청", "opt10020", "0",
                         self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
        self.calculator_event_loop.exec_()

    def get_5min_datalist_data(self, code_list):
        for idx, code in enumerate(code_list):
            self.logging.logger.debug(
                "%s / %s : Stock Code : %s is updating... " % (idx + 1, len(code_list), code))
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock)  # 스크린 연결 끊기
            self.code = code
            self.get_5min_hogas_kiwoom_db(code=code)

    def get_5min_data(self):
        self.logging.logger.debug("get_5min_data 시작")
        for code in self.temp_enormous_code_dict.keys():
            self.code = code
            self.get_current_price_kiwoom_db(code)
        # "관리" 사전 데이터 완성 후 파일에 저장 및 초기화
        folderpath = "files/dnn_data"
        if not os.path.isdir(folderpath):
            os.mkdir(folderpath)
        filepath = folderpath + "/" + self.cur_date + ".txt"
        f = open(filepath, "a", encoding="utf8")
        for code in self.temp_enormous_code_dict.keys():
            # 종목코드, 시간, 매도가격, 매수가격, 총매도..., "현재가"
            f.write(
                "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
                    str(code),
                    str(self.temp_enormous_code_dict[code]['data_set'][1]),
                    str(self.temp_enormous_code_dict[code]['data_set'][2]),
                    str(self.temp_enormous_code_dict[code]['data_set'][3]),
                    str(self.temp_enormous_code_dict[code]['data_set'][4]),
                    str(self.temp_enormous_code_dict[code]['data_set'][5]),
                    str(self.temp_enormous_code_dict[code]['data_set'][6]),
                    str(self.temp_enormous_code_dict[code]['data_set'][7]),
                    str(self.temp_enormous_code_dict[code]['data_set'][8]),
                    str(self.temp_enormous_code_dict[code]['data_set'][9]),
                    str(self.temp_enormous_code_dict[code]['data_set'][10]),
                    str(self.temp_enormous_code_dict[code]['data_set'][11]),
                    str(self.temp_enormous_code_dict[code]['data_set'][12]),
                    str(self.temp_enormous_code_dict[code]['data_set'][13]),
                    str(self.temp_enormous_code_dict[code]['data_set'][14]),
                    str(self.temp_enormous_code_dict[code]['data_set'][15]),
                    str(self.temp_enormous_code_dict[code]['data_set'][16]),
                    str(self.temp_enormous_code_dict[code]['data_set'][17]),
                    str(self.temp_enormous_code_dict[code]['data_set'][18]),
                    str(self.temp_enormous_code_dict[code]['data_set'][19]),
                    str(self.temp_enormous_code_dict[code]['data_set'][20]),
                    str(self.temp_enormous_code_dict[code]['data_set'][21]),
                    str(self.temp_enormous_code_dict[code]['data_set'][22]),
                    str(self.temp_enormous_code_dict[code]['data_set'][23]),
                    str(self.temp_enormous_code_dict[code]['data_set'][24]),
                    str(self.temp_enormous_code_dict[code]['data_set'][25]),
                    str(self.temp_enormous_code_dict[code]["현재가"])
                    )
            )
        f.close()
        self.logging.logger.debug("파일 저장 완료")
        self.enormous_code_list.clear()
        self.logging.logger.debug("거래량 급증 15개 요청 전")
        self.get_5min_datalist()
        #self.get_hogavast_datalist()
        #self.get_hogavastrank_datalist()
        self.logging.logger.debug("거래량 급증 15개 요청 완료")
        self.temp_enormous_code_dict.clear()
        self.get_5min_datalist_data(self.enormous_code_list)
        self.logging.logger.debug("waiting for 5min")

    def load_data(self, test_date = ""):  #### 텍스트 파일 가져와서, 딕셔너리에 넣음
        data = pd.read_csv(test_date, sep='\t', names=COLUMNS_CHART_DATA_H2, header=None, dtype={"stock_code":str, "time":str})
        for i in range(len(data)):
            self.text_dict[str(data.loc[i]['time'])] = {}
            self.text_dict.update({str(data.loc[i]['time']):{"종목코드":str(data.loc[i]['stock_code'])}})
        self.logging.logger.debug("load_data 종료")

    def text_query_data(self, code, sPrevNext="0", minute="1"):
        self.code = code
        self.logging.logger.debug(code)
        self.logging.logger.debug(self.target_date)
        QTest.qWait(4000)  # 3.6초(4초로 변경)마다 딜레이를 준다.
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "틱범위", minute)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "텍스트주식분봉차트조회", "opt10080", sPrevNext,
                         self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
        self.calculator_event_loop.exec_()

    def get_end_data(self, target_date = ""):  #### 위 텍스트 파일로부터 추출한 딕셔너리 종목의 test_date 날짜의 15:00 가격을 가져와서 딕셔너리에 저장
        self.logging.logger.debug("총 "+str(len(self.text_dict))+"개")
        for curtime in self.text_dict.keys():
            code = self.text_dict[curtime]["종목코드"]
            self.current_time = curtime
            self.text_query_data(code=code)

    def save_data(self, test_date = "", target_date = ""):  #### 작업 종료 후 다시 딕셔너리에 넣었던 순서대로 + n분 후 데이터 대신 15시의 가격을 넣음
        data = pd.read_csv(test_date, sep='\t', names=COLUMNS_CHART_DATA_H2, header=None, dtype={"stock_code":str, "time":str})
        # "관리" 사전 데이터 완성 후 파일에 저장 및 초기화
        folderpath = "files/dnn_data"
        if not os.path.isdir(folderpath):
            os.mkdir(folderpath)
        filepath = folderpath + "/" + target_date + "_" + str(self.minute_gap) + "min" + ".txt"
        f = open(filepath, "a", encoding="utf8")
        for i in range(len(data)):
            # 종목코드, 시간, 매도가격, 매수가격, 총매도..., "현재가"
            current_time = str(data.loc[i]['time'])
            end_price = self.text_dict[current_time]["종가"]
            f.write(
                "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
                    str(data.loc[i]['stock_code']),
                    str(data.loc[i]['time']),
                    str(data.loc[i]['mado_price']),
                    str(data.loc[i]['masu_price']),
                    str(data.loc[i]['total_mado']),
                    str(data.loc[i]['total_masu']),
                    str(data.loc[i]['mado_1']),
                    str(data.loc[i]['mado_2']),
                    str(data.loc[i]['mado_3']),
                    str(data.loc[i]['mado_4']),
                    str(data.loc[i]['mado_5']),
                    str(data.loc[i]['mado_6']),
                    str(data.loc[i]['mado_7']),
                    str(data.loc[i]['mado_8']),
                    str(data.loc[i]['mado_9']),
                    str(data.loc[i]['mado_10']),
                    str(data.loc[i]['masu_1']),
                    str(data.loc[i]['masu_2']),
                    str(data.loc[i]['masu_3']),
                    str(data.loc[i]['masu_4']),
                    str(data.loc[i]['masu_5']),
                    str(data.loc[i]['masu_6']),
                    str(data.loc[i]['masu_7']),
                    str(data.loc[i]['masu_8']),
                    str(data.loc[i]['masu_9']),
                    str(data.loc[i]['masu_10']),
                    str(end_price)
                )
            )
        f.close()

    def read_code(self):
        if os.path.exists("files/condition_stock.txt"): # 해당 경로에 파일이 있는지 체크한다.
            f = open("files/condition_stock.txt", "r", encoding="utf8") # "r"을 인자로 던져주면 파일 내용을 읽어 오겠다는 뜻이다.
            lines = f.readlines() #파일에 있는 내용들이 모두 읽어와 진다.
            for line in lines: #줄바꿈된 내용들이 한줄 씩 읽어와진다.
                if line != "":
                    ls = line.split("\t")
                    stock_code = ls[0]
                    stock_name = ls[1]
                    stock_price = int(ls[2].split("\n")[0])
                    stock_price = abs(stock_price)
                    self.portfolio_stock_dict.update({stock_code:{"종목명":stock_name, "현재가":stock_price}})
            f.close()

    def merge_dict(self):
        self.all_stock_dict.update({"계좌평가잔고내역": self.account_stock_dict})
        self.all_stock_dict.update({'미체결종목': self.not_account_stock_dict})
        self.all_stock_dict.update({'포트폴리오종목': self.portfolio_stock_dict})

    def screen_number_setting(self):
        screen_overwrite = []
        #계좌평가잔고내역에 있는 종목들
        for code in self.account_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)
        #미체결에 있는 종목들
        for order_number in self.not_account_stock_dict.keys():
            code = self.not_account_stock_dict[order_number]['종목코드']
            if code not in screen_overwrite:
                screen_overwrite.append(code)
        #포트폴리오에 담겨있는 종목들
        for code in self.portfolio_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)
        # 스크린번호 할당
        cnt = 0
        for code in screen_overwrite:
            temp_screen = int(self.screen_real_stock)
            meme_screen = int(self.screen_meme_stock)
            if (cnt % 50) == 0:
                temp_screen += 1
                self.screen_real_stock = str(temp_screen)
            if (cnt % 50) == 0:
                meme_screen += 1
                self.screen_meme_stock = str(meme_screen)
            if code in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict[code].update({"스크린번호": str(self.screen_real_stock)})
                self.portfolio_stock_dict[code].update({"주문용스크린번호": str(self.screen_meme_stock)})
            elif code not in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict.update({code: {"스크린번호": str(self.screen_real_stock), "주문용스크린번호": str(self.screen_meme_stock)}})
            cnt += 1

    # 실시간 데이터 얻어오기
    def realdata_slot(self, sCode, sRealType, sRealData):
        if sRealType == "장시작시간":
            fid = self.realType.REALTYPE[sRealType]['장운영구분']  # (0:장시작전, 2:장종료전(20분), 3:장시작, 4,8:장종료(30분), 9:장마감)
            value = self.dynamicCall("GetCommRealData(QString, int)", sCode, fid)
            if value == '0':
                self.logging.logger.debug("장 시작 전")
            elif value == '3':
                self.logging.logger.debug("장 시작")
            elif value == "2":
                self.logging.logger.debug("장 종료, 동시호가로 넘어감")
            elif value == "4":
                self.logging.logger.debug("3시30분 장 종료")
                for code in self.portfolio_stock_dict.keys():
                    self.dynamicCall("SetRealRemove(QString, QString)", self.portfolio_stock_dict[code]['스크린번호'], code)
                for code in self.invest_dict.keys():
                    self.dynamicCall("SetRealRemove(QString, QString)", self.invest_dict[code]['스크린번호'], code)
                QTest.qWait(5000)
                # self.file_delete() 포트폴리오 종목 분석한 텍스트 파일을 지움
                # self.calculator_fnc() 포트폴리오 종목 분석
                sys.exit()
        # elif sRealType == "주식체결":
        #     a = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['체결시간'])  # 출력 HHMMSS
        #     b = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['현재가'])  # 출력 : +(-)2520
        #     b = abs(int(b))
        #
        #     c = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['전일대비'])  # 출력 : +(-)2520
        #     c = abs(int(c))
        #
        #     d = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['등락율'])  # 출력 : +(-)12.98
        #     d = float(d)
        #
        #     e = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['(최우선)매도호가'])  # 출력 : +(-)2520
        #     e = abs(int(e))
        #
        #     f = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['(최우선)매수호가'])  # 출력 : +(-)2515
        #     f = abs(int(f))
        #
        #     g = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['거래량'])  # 출력 : +240124  매수일때, -2034 매도일 때
        #     g = abs(int(g))
        #
        #     h = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['누적거래량'])  # 출력 : 240124
        #     h = abs(int(h))
        #
        #     i = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['고가'])  # 출력 : +(-)2530
        #     i = abs(int(i))
        #
        #     j = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['시가'])  # 출력 : +(-)2530
        #     j = abs(int(j))
        #
        #     k = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['저가'])  # 출력 : +(-)2530
        #     k = abs(int(k))
        #
        #     if sCode not in self.portfolio_stock_dict:
        #         self.portfolio_stock_dict.update({sCode:{}})
        #
        #     self.portfolio_stock_dict[sCode].update({"체결시간": a})
        #     self.portfolio_stock_dict[sCode].update({"현재가": b})
        #     self.portfolio_stock_dict[sCode].update({"전일대비": c})
        #     self.portfolio_stock_dict[sCode].update({"등락율": d})
        #     self.portfolio_stock_dict[sCode].update({"(최우선)매도호가": e})
        #     self.portfolio_stock_dict[sCode].update({"(최우선)매수호가": f})
        #     self.portfolio_stock_dict[sCode].update({"거래량": g})
        #     self.portfolio_stock_dict[sCode].update({"누적거래량": h})
        #     self.portfolio_stock_dict[sCode].update({"고가": i})
        #     self.portfolio_stock_dict[sCode].update({"시가": j})
        #     self.portfolio_stock_dict[sCode].update({"저가": k})
        #
        #     # if sCode in self.account_stock_dict.keys() and sCode not in self.jango_dict.keys():
        #     #     asd = self.account_stock_dict[sCode]
        #     #     meme_rate = (b - asd['매입가']) / asd['매입가'] * 100
        #     #
        #     #     if asd['매매가능수량'] > 0 and (meme_rate > 5 or meme_rate < -5):
        #     #
        #     #         order_success = self.dynamicCall(
        #     #             "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
        #     #             ["신규매도", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 2, sCode, asd['매매가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'], ""]
        #     #         )
        #     #
        #     #         if order_success == 0:
        #     #             self.logging.logger.debug("매도주문 전달 성공")
        #     #             del self.account_stock_dict[sCode]
        #     #         else:
        #     #             self.logging.logger.debug("매도주문 전달 실패")
        #     #
        #     # elif sCode in self.jango_dict.keys():
        #     #     jd = self.jango_dict[sCode]
        #     #     meme_rate = (b - jd['매입단가']) / jd['매입단가'] * 100
        #     #
        #     #     if jd['주문가능수량'] > 0 and (meme_rate > 5 or meme_rate < -5):
        #     #
        #     #         order_success = self.dynamicCall(
        #     #             "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
        #     #             ["신규매도", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 2, sCode, jd['주문가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'], ""]
        #     #         )
        #     #
        #     #         if order_success == 0:
        #     #             self.logging.logger.debug("매도주문 전달 성공")
        #     #         else:
        #     #             self.logging.logger.debug("매도주문 전달 실패")
        #     #
        #     # elif d > 2.0 and sCode not in self.jango_dict:
        #     #     self.logging.logger.debug("매수조건 통과 %s " % sCode)
        #     #
        #     #     result = (self.use_money * 0.1) / e
        #     #     quantity = int(result)
        #     #
        #     #     order_success = self.dynamicCall(
        #     #         "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
        #     #         ["신규매수", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 1, sCode, quantity, e, self.realType.SENDTYPE['거래구분']['지정가'], ""]
        #     #     )
        #     #
        #     #     if order_success == 0:
        #     #         self.logging.logger.debug("매수주문 전달 성공")
        #     #     else:
        #     #         self.logging.logger.debug("매수주문 전달 실패")
        #
        #     not_meme_list = list(self.not_account_stock_dict)
        #     for order_num in not_meme_list:
        #         code = self.not_account_stock_dict[order_num]["종목코드"]
        #         meme_price = self.not_account_stock_dict[order_num]['주문가격']
        #         not_quantity = self.not_account_stock_dict[order_num]['미체결수량']
        #         order_gubun = self.not_account_stock_dict[order_num]['주문구분']
        #         # 미체결된 주식들 중(특히 주식체결 실시간 데이터 슬롯이 반응하였는데, 최우선매도호가보다 낮은 가격에 살 수는 없으므로
        #         # 매수취소
        #         # if order_gubun == "매수" and not_quantity > 0 and e > meme_price:
        #         #     order_success = self.dynamicCall(
        #         #         "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
        #         #         ["매수취소", self.invest_dict[sCode]["주문용스크린번호"], self.account_num, 3, code, 0, 0, self.realType.SENDTYPE['거래구분']['지정가'], order_num]
        #         #     )
        #         #
        #         #     if order_success == 0:
        #         #         self.logging.logger.debug("매수취소 전달 성공")
        #         #     else:
        #         #         self.logging.logger.debug("매수취소 전달 실패")
        #         # # 미체결된 주식들 중(어떻게 보면 체결되었다고 볼 수 있는) 미체결수량이 0이면 미체결사전에서 삭제
        #         if not_quantity == 0:
        #             del self.not_account_stock_dict[order_num]
        elif sRealType == "주식호가잔량":
            data = []
            hoga_time = self.dynamicCall("GetCommRealData(QString, int)", sCode, 21).strip()  # 출력 HHMMSS
            # 1. A (10매도, 매수호가 평균)
            mado_price = []
            masu_price = []
            for i in range(10):
                # 매도호가1 : 41 ~ 매도호가10 : 50
                temp_mado_price_index = 41 + i
                t_d = float(self.dynamicCall("GetCommRealData(QString, int)", sCode, temp_mado_price_index)
                            .strip().lstrip('+').lstrip('-'))
                if (t_d == 0):
                    pass
                else:
                    mado_price.append(t_d)
                # 매수호가1 : 51 ~ 매수호가10 : 60
                temp_masu_price_index = 51 + i
                t_s = float(self.dynamicCall("GetCommRealData(QString, int)", sCode, temp_masu_price_index)
                            .strip().lstrip('+').lstrip('-'))
                if (t_s == 0):
                    pass
                else:
                    masu_price.append(t_s)
            # 가격 이상을 통해 제어
            if(len(mado_price) == 0 or len(masu_price) == 0):
                return
            mado_price_mean = sum(mado_price) / len(mado_price)
            masu_price_mean = sum(masu_price) / len(masu_price)
            # 2. 호가잔량 - 1 ~ 10의 총합만을 사용
            # 매도총잔량 : 121 매도총잔량직전대비 : 122
            mado_total_mount = self.dynamicCall("GetCommRealData(QString, int)", sCode, 121).strip().lstrip('+').lstrip('-')
            mado_total_mount_diff = self.dynamicCall("GetCommRealData(QString, int)", sCode, 122).strip().lstrip('+')
            # 매수총잔량 : 125 매수총잔량직전대비 : 126
            masu_total_mount = self.dynamicCall("GetCommRealData(QString, int)", sCode, 125).strip().lstrip('+').lstrip('-')
            masu_total_mount_diff = self.dynamicCall("GetCommRealData(QString, int)", sCode, 126).strip().lstrip('+')
            # 3. 순매도, 매수잔량
            # 순매도잔량 : 138 매도비율 : 139
            mado_pure_mount = self.dynamicCall("GetCommRealData(QString, int)", sCode, 138).strip().lstrip('+')
            mado_ratio = self.dynamicCall("GetCommRealData(QString, int)", sCode, 139).strip().lstrip('+').lstrip('-')

            # 순매수잔량 : 128 매수비율 : 129
            masu_pure_mount = self.dynamicCall("GetCommRealData(QString, int)", sCode, 128).strip().lstrip('+')
            masu_ratio = self.dynamicCall("GetCommRealData(QString, int)", sCode, 129).strip().lstrip('+').lstrip('-')
            data.append("")
            data.append(hoga_time)
            data.append(mado_price_mean)
            data.append(masu_price_mean)
            data.append(mado_total_mount)
            data.append(mado_total_mount_diff)
            data.append(masu_total_mount)
            data.append(masu_total_mount_diff)
            data.append(mado_pure_mount)
            data.append(mado_ratio)
            data.append(masu_pure_mount)
            data.append(masu_ratio)
            data.append("")
            self.calcul_data.append(copy.deepcopy(data))
            # 09000 ~ 15:~~ 까지 전부 받아옴
            # self.logging.logger.debug("총 분봉수 %s" % len(self.calcul_data))
            folderpath = "files/" + self.cur_date
            if not os.path.isdir(folderpath):
                os.mkdir(folderpath)
            filepath = folderpath + "/" + self.cur_time + "_" + sCode + ".txt"
            f = open(filepath, "a", encoding="utf8")
            for k in range(len(self.calcul_data)):
                f.write(
                    "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
                        str(self.calcul_data[k][1]), str(self.calcul_data[k][2]), str(self.calcul_data[k][3]),
                        str(self.calcul_data[k][4]), str(self.calcul_data[k][5]), str(self.calcul_data[k][6]),
                        str(self.calcul_data[k][7]), str(self.calcul_data[k][8]), str(self.calcul_data[k][9]),
                        str(self.calcul_data[k][10]), str(self.calcul_data[k][11])))
            f.close()
            #self.logging.logger.debug("Stock Code : %s is updating... " % (sCode))
            self.calcul_data.clear()

            ######################## 데이터 수집 및 이용
            # if(sCode not in self.ten_cal_dict.keys()):
            #     return
            # data = []
            # hoga_time = self.dynamicCall("GetCommRealData(QString, int)", sCode, 21).strip()  # 출력 HHMMSS
            # mado_price = self.dynamicCall("GetCommRealData(QString, int)", sCode, 41).strip().lstrip('+').lstrip('-')  # 출력 HHMMSS
            # masu_price = self.dynamicCall("GetCommRealData(QString, int)", sCode, 51).strip().lstrip('+').lstrip('-')  # 출력 HHMMSS
            # mado = []
            # masu = []
            # for i in range(10):
            #     tempmadoint = 61 + i
            #     #tempmadoint = 81 + i
            #     mado.append(self.dynamicCall("GetCommRealData(QString, int)", sCode, tempmadoint).strip().lstrip('+').lstrip('-')) # 출력 HHMMSS
            #     tempmasuint = 71 + i
            #     #tempmasuint = 91 + i
            #     masu.append(self.dynamicCall("GetCommRealData(QString, int)", sCode, tempmasuint).strip().lstrip('+').lstrip('-')) # 출력 HHMMSS
            #
            # total_mado = self.dynamicCall("GetCommRealData(QString, int)", sCode, 121).strip().lstrip('+').lstrip('-')
            # #total_mado = self.dynamicCall("GetCommRealData(QString, int)", sCode, 122)
            # total_masu = self.dynamicCall("GetCommRealData(QString, int)", sCode, 125).strip().lstrip('+').lstrip('-')
            # data.append("")
            # data.append(hoga_time)
            # data.append(mado_price)
            # data.append(masu_price)
            # data.append(total_mado)
            # data.append(total_masu)
            # for i in range(10):
            #     data.append(mado[i])
            # for j in range(10):
            #     data.append(masu[j])
            # data.append("")
            # self.calcul_data.append(copy.deepcopy(data))
            # # 09000 ~ 15:~~ 까지 전부 받아옴
            # # self.logging.logger.debug("총 분봉수 %s" % len(self.calcul_data))
            # folderpath = "files/" + self.cur_date
            # if not os.path.isdir(folderpath):
            #     os.mkdir(folderpath)
            # filepath = folderpath + "/" + self.cur_time + "_" + sCode + ".txt"
            # f = open(filepath, "a", encoding="utf8")
            # for k in range(len(self.calcul_data)):
            #     f.write(
            #         "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
            #             str(self.calcul_data[k][1]), str(self.calcul_data[k][2]), str(self.calcul_data[k][3]),
            #             str(self.calcul_data[k][4]), str(self.calcul_data[k][5]), str(self.calcul_data[k][6]),
            #             str(self.calcul_data[k][7]), str(self.calcul_data[k][8]), str(self.calcul_data[k][9]),
            #             str(self.calcul_data[k][10]), str(self.calcul_data[k][11]), str(self.calcul_data[k][12]),
            #             str(self.calcul_data[k][13]), str(self.calcul_data[k][14]), str(self.calcul_data[k][15]),
            #             str(self.calcul_data[k][16]), str(self.calcul_data[k][17]), str(self.calcul_data[k][18]),
            #             str(self.calcul_data[k][19]), str(self.calcul_data[k][20]), str(self.calcul_data[k][21]),
            #             str(self.calcul_data[k][22]), str(self.calcul_data[k][23]), str(self.calcul_data[k][24]),
            #             str(self.calcul_data[k][25])))
            # f.close()
            # #self.logging.logger.debug("Stock Code : %s is updating... " % (sCode))
            # self.calcul_data.clear()
            # ############################################# 돌리기
            # #self.logging.logger.debug("Stock Code : %s is updating... -1" % (sCode))
            # data = []
            # mado_price = self.dynamicCall("GetCommRealData(QString, int)", sCode, 41).strip().lstrip('+').lstrip('-')  # 출력 HHMMSS
            # masu_price = self.dynamicCall("GetCommRealData(QString, int)", sCode, 51).strip().lstrip('+').lstrip('-')  # 출력 HHMMSS
            # mado = []
            # masu = []
            # for i in range(10):
            #     tempmadoint = 61 + i
            #     mado.append(self.dynamicCall("GetCommRealData(QString, int)", sCode, tempmadoint)
            #                 .strip().lstrip('+').lstrip('-'))  # 출력 HHMMSS
            #     tempmasuint = 71 + i
            #     masu.append(self.dynamicCall("GetCommRealData(QString, int)", sCode, tempmasuint)
            #                 .strip().lstrip('+').lstrip('-'))  # 출력 HHMMSS
            # total_mado = self.dynamicCall("GetCommRealData(QString, int)", sCode, 121).strip().lstrip('+').lstrip('-')
            # total_masu = self.dynamicCall("GetCommRealData(QString, int)", sCode, 125).strip().lstrip('+').lstrip('-')
            # # 시고저종에 전부 -, +가 붙을 수 있으므로 제거
            # data.append("")
            # data.append(mado_price)
            # data.append(masu_price)
            # data.append(total_mado)
            # data.append(total_masu)
            # for i in range(10):
            #     data.append(mado[i])
            # for j in range(10):
            #     data.append(masu[j])
            # data.append("")
            # ### diction 사용 기존 10개에서 하나빼고 넣기
            # #print("-1")
            # self.ten_cal_dict[sCode]['계산데이터'].append(copy.deepcopy(data))
            # #self.ten_cal_dict[sCode].update({"주식개수":1})
            # #print(self.ten_cal_dict[sCode])
            # #print("-2")
            # if(len(self.ten_cal_dict[sCode]['계산데이터']) >= 12):
            #     self.ten_cal_dict[sCode]['계산데이터'].pop(0)
            # # 계산하기 with 11개 (앞에 (last 10때문)
            # # 계산데이터 1 4 매도 매수 total매도 total매수 5 14 매도 15 24 매수
            # if(len(self.ten_cal_dict[sCode]['계산데이터']) == 11):
            #     temp_cal_data = []
            #     ## mado price - masu price
            #     #print("1")
            #     gap = int(mado_price) - int(masu_price)
            #     #print("12")
            #     if (gap <= 0): # 무시
            #         #print("ignore")
            #         return
            #     if (int(total_masu) == 0 or int(total_mado) == 0):
            #         return
            #     #print("13")
            #     step = pow(10, int(math.log10(gap)))
            #     mado = np.array(mado, dtype=int)
            #     masu = np.array(masu, dtype=int)
            #     temptotal = max(mado.max(), masu.max())
            #     #print("14")
            #     for i in range(len(mado)):
            #         temp_cal_data.append(float(mado[i]/temptotal))
            #     for i in range(len(masu)):
            #         temp_cal_data.append(float(masu[i]/temptotal))
            #     #print("15")
            #     temp_cal_data.append(float(int(total_mado) / (int(total_mado) + int(total_masu))))
            #     temp_cal_data.append(float(int(total_masu) / (int(total_mado) + int(total_masu))))
            #     ### 현재 - 과거 / step
            #     #print("2")
            #     # 5
            #     mado_average = 0
            #     mado_average_p = 0
            #     for i in range(5):
            #         mado_average += int(self.ten_cal_dict[sCode]['계산데이터'][i+6][3])
            #         mado_average_p += int(self.ten_cal_dict[sCode]['계산데이터'][i+5][3])
            #     mado_ma5 = float(mado_average / 5)
            #     mado_ma5_p = float(mado_average_p / 5)
            #     mado_ma5_sub = float((mado_ma5 - int(mado_price)) / step)
            #     mado_ma5_last = float((mado_ma5 - mado_ma5_p) / step)
            #     #print("3")
            #     # 10
            #     mado_average = 0
            #     mado_average_p = 0
            #     for i in range(10):
            #         mado_average += int(self.ten_cal_dict[sCode]['계산데이터'][i+1][3])
            #         mado_average_p += int(self.ten_cal_dict[sCode]['계산데이터'][i][3])
            #     mado_ma10 = float(mado_average / 10)
            #     mado_ma10_p = float(mado_average_p / 10)
            #     mado_ma10_sub = float((mado_ma10 - int(mado_price)) / step)
            #     mado_ma10_last = float((mado_ma10 - mado_ma10_p) / step)
            #     # mado_ma5_sub masu_ma5_sub
            #     temp_cal_data.append(mado_ma5_sub)
            #     temp_cal_data.append(mado_ma10_sub)
            #     temp_cal_data.append(mado_ma5_last)
            #     temp_cal_data.append(mado_ma10_last)
            #     #print("4")
            #     ###### 연산
            #     for i in range(len(self.weights)):  # 0 ~ 8
            #         temp_weight = np.array(self.weights[i], dtype=np.float64)
            #         temp_biased = np.array(self.biaseds[i], dtype=np.float64)
            #         if i == (len(self.weights)-1):
            #             temp_cal_data = (np.dot(temp_cal_data, temp_weight) + temp_biased)
            #         else:
            #             temp_cal_data = np.tanh(np.dot(temp_cal_data, temp_weight) + temp_biased)
            #     #### for문 이후 temp_cal_data는 결과값임
            #     trading_stocks = temp_cal_data
            #     # action = float(action / 10)  # 0.0 ~ 0.9로의 변환
            #     # testsample = copy.deepcopy(self.invest_dict[code])
            #     # num_stocks = int(action * int((testsample["포트폴리오가치"] / testsample["현재가"])))
            #     # trading_stocks = num_stocks - testsample["주식개수"]
            #     stocks = int(1000000 / int(mado_price))
            #     mado_stocks = int(self.ten_cal_dict[sCode]['주식개수'])
            #     real_mado_stocks = int(self.ten_cal_dict[sCode]['실제주식개수'])
            #     if trading_stocks[0] >= 0.05:  # 매수를 해야하는 상황
            #         if (mado_stocks == 0):
            #             print(temp_cal_data)
            #             self.ordercount += 1
            #             if (self.ordercount >= 80):
            #                 self.dynamicCall("DisconnectRealData(QString)", "6000")  # 스크린 연결 끊기
            #                 self.totalorder += self.ordercount
            #                 self.ordercount = 0
            #             order_success = self.dynamicCall(
            #                 "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
            #                 ["신규매수", self.ten_cal_dict[sCode]['주문용스크린번호'], self.account_num, 1, sCode, stocks, "",
            #                  self.realType.SENDTYPE['거래구분']['시장가'], ""])
            #             if order_success == 0:
            #                 self.logging.logger.debug("매수주문 전달 성공")
            #                 self.ten_cal_dict[sCode]['주식개수'] += int(stocks)
            #             else:
            #                 self.logging.logger.debug("매수주문 전달 실패")
            #     elif trading_stocks[0] < 0.05:  # 매도를 해야하는 상황 # int
            #         if (real_mado_stocks > 0):
            #             print(temp_cal_data)
            #             self.ordercount += 1
            #             if (self.ordercount >= 80):
            #                 self.dynamicCall("DisconnectRealData(QString)", "6000")  # 스크린 연결 끊기
            #                 self.totalorder += self.ordercount
            #                 self.ordercount = 0
            #             order_success = self.dynamicCall(
            #                 "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
            #                 ["신규매도", self.ten_cal_dict[sCode]['주문용스크린번호'], self.account_num, 2, sCode, real_mado_stocks, "",
            #                  self.realType.SENDTYPE['거래구분']['시장가'], ""])
            #             if order_success == 0:
            #                 self.logging.logger.debug("매도주문 전달 성공")
            #                 self.ten_cal_dict[sCode]['주식개수'] -= int(real_mado_stocks)
            #             else:
            #                 self.logging.logger.debug("매도주문 전달 실패")
            #             # QTest.qWait(5000) # 5초정도 기다림
            #     else: # 0.5 ~ 0.7은 굳이 매도를 하거나 매수를 할 필요는 없으므로 -> 수수료 줄이기
            #         pass
            #print(self.ten_cal_dict)
            #self.logging.logger.debug("Stock Code : %s is finish... " % (sCode))

    # 실시간 체결 정보
    def chejan_slot(self, sGubun, nItemCnt, sFidList):
        if int(sGubun) == 0: #주문체결
            self.logging.logger.debug("체결 관련 메시지 발생")
            account_num = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['계좌번호'])
            sCode = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목코드'])[1:]
            stock_name = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목명'])
            stock_name = stock_name.strip()

            # origin_order_number = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['원주문번호'])  # 출력 : defaluse : "000000"
            # order_number = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문번호'])  # 출럭: 0115061 마지막 주문번호
            self.logging.logger.debug("체결 관련 메시지 발생3")
            order_status = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문상태'])  # 출력: 접수, 확인, 체결
            order_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문수량'])  # 출력 : 3
            order_quan = int(order_quan)

            order_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문가격'])  # 출력: 21000
            order_price = int(order_price)

            not_chegual_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['미체결수량'])  # 출력: 15, default: 0
            not_chegual_quan = int(not_chegual_quan)

            order_gubun = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문구분'])  # 출력: -매도, +매수
            order_gubun = order_gubun.strip().lstrip('+').lstrip('-')

            # chegual_time_str = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문/체결시간'])  # 출력: '151028'
            #
            # chegual_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결가'])  # 출력: 2110  default : ''
            # if chegual_price == '':
            #     chegual_price = 0
            # else:
            #     chegual_price = int(chegual_price)
            #
            # chegual_quantity = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결량'])  # 출력: 5  default : ''
            # if chegual_quantity == '':
            #     chegual_quantity = 0
            # else:
            #     chegual_quantity = int(chegual_quantity)

            # current_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['현재가'])  # 출력: -6000
            # current_price = abs(int(current_price))
            #
            # first_sell_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['(최우선)매도호가'])  # 출력: -6010
            # first_sell_price = abs(int(first_sell_price))
            #
            # first_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['(최우선)매수호가'])  # 출력: -6000
            # first_buy_price = abs(int(first_buy_price))

            ######## 새로 들어온 주문이면 주문번호 할당
            # if order_number not in self.not_account_stock_dict.keys():
            #     self.not_account_stock_dict.update({order_number: {}})
            #
            # self.not_account_stock_dict[order_number].update({"종목코드": sCode})
            # self.not_account_stock_dict[order_number].update({"주문번호": order_number})
            # self.not_account_stock_dict[order_number].update({"종목명": stock_name})
            # self.not_account_stock_dict[order_number].update({"주문상태": order_status})
            # self.not_account_stock_dict[order_number].update({"주문수량": order_quan})
            # self.not_account_stock_dict[order_number].update({"주문가격": order_price})
            # self.not_account_stock_dict[order_number].update({"미체결수량": not_chegual_quan})
            # self.not_account_stock_dict[order_number].update({"원주문번호": origin_order_number})
            # self.not_account_stock_dict[order_number].update({"주문구분": order_gubun})
            # self.not_account_stock_dict[order_number].update({"주문/체결시간": chegual_time_str})
            # self.not_account_stock_dict[order_number].update({"체결가": chegual_price})
            # self.not_account_stock_dict[order_number].update({"체결량": chegual_quantity})
            # self.not_account_stock_dict[order_number].update({"현재가": current_price})
            # self.not_account_stock_dict[order_number].update({"(최우선)매도호가": first_sell_price})
            # self.not_account_stock_dict[order_number].update({"(최우선)매수호가": first_buy_price})
            self.logging.logger.debug("체결 관련 메시지 발생2")
            ########## 주문 체결 후 잔고처리 과정에서
            # 생각 - 150개 주문했다고 가정하자. -> 100개 체결 -> 100 / 50  15 체결량 115 / 미체결 35 -> 50개까지다 체결 -> 체결량 120 / 미체결 30
            # 또는 100개 체결 100 / 50 15개 체결 15 35 일수도 있음(아닐수도 있음)
            # 우려하던 문제점 발생 -> 미체결수량이 0이 되었을 때 해야할 듯??
            # 모든 주문량이 체결되었을 때
            if not_chegual_quan == 0:
                self.logging.logger.debug("체결 관련 메시지 발생5")
                if order_gubun == "매수":  # 매수이면
                    self.logging.logger.debug("체결 관련 메시지 발생6")
                    if(sCode in self.ten_cal_dict.keys()):
                        self.ten_cal_dict[sCode]["실제주식개수"] += order_quan
                        self.logging.logger.debug("매수 완료 종목 코드 : %s | 주식 개수 : %s" % (
                        sCode, str(self.ten_cal_dict[sCode]["실제주식개수"])))
                        self.logging.logger.debug("체결 관련 메시지 발생8")
                    # 모의투자세 + 수수료
                    # self.invest_dict[sCode]["운용금액"] -= (order_quan * chegual_price)
                    # self.invest_dict[sCode]["주식개수"] += order_quan
                    # self.logging.logger.debug("매수 완료 종목 코드 : %s | 운용금액 : %s | 주식 개수 : %s" %(sCode, str(self.invest_dict[sCode]["운용금액"]), str(self.invest_dict[sCode]["주식개수"])))
                elif order_gubun == "매도":  # 매도이면
                    if (sCode in self.ten_cal_dict.keys()):
                        self.logging.logger.debug("체결 관련 메시지 발생7")
                        self.ten_cal_dict[sCode]["실제주식개수"] -= order_quan
                        self.logging.logger.debug("매도 완료 종목 코드 : %s | 주식 개수 : %s" % (
                            sCode, str(self.ten_cal_dict[sCode]["실제주식개수"])))
                        self.logging.logger.debug("체결 관련 메시지 발생9")
                    # 거래세 + 모의투자세 + 수수료
                    # self.invest_dict[sCode]["운용금액"] += (order_quan * chegual_price)
                    # self.invest_dict[sCode]["주식개수"] -= order_quan
                    # self.logging.logger.debug("매도 완료 종목 코드 : %s | 운용금액 : %s | 주식 개수 : %s" %(sCode, str(self.invest_dict[sCode]["운용금액"]), str(self.invest_dict[sCode]["주식개수"])))
                else:
                    self.logging.logger.debug("체결 관련 오류")
        elif int(sGubun) == 1: #잔고
            self.logging.logger.debug("잔고 관련 메시지")
            account_num = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['계좌번호'])
            sCode = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['종목코드'])[1:]
            stock_name = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['종목명'])
            stock_name = stock_name.strip()
            current_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['현재가'])
            current_price = abs(int(current_price))
            stock_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['보유수량'])
            stock_quan = int(stock_quan)
            like_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['주문가능수량'])
            like_quan = int(like_quan)
            buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['매입단가'])
            buy_price = abs(int(buy_price))
            total_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['총매입가']) # 계좌에 있는 종목의 총매입가
            total_buy_price = int(total_buy_price)
            meme_gubun = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['매도매수구분'])
            meme_gubun = self.realType.REALTYPE['매도수구분'][meme_gubun]
            first_sell_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['(최우선)매도호가'])
            first_sell_price = abs(int(first_sell_price))
            first_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['(최우선)매수호가'])
            first_buy_price = abs(int(first_buy_price))
            if sCode not in self.jango_dict.keys():
                self.jango_dict.update({sCode:{}})
            self.jango_dict[sCode].update({"현재가": current_price})
            self.jango_dict[sCode].update({"종목코드": sCode})
            self.jango_dict[sCode].update({"종목명": stock_name})
            self.jango_dict[sCode].update({"보유수량": stock_quan})
            self.jango_dict[sCode].update({"주문가능수량": like_quan})
            self.jango_dict[sCode].update({"매입단가": buy_price})
            self.jango_dict[sCode].update({"총매입가": total_buy_price})
            self.jango_dict[sCode].update({"매도매수구분": meme_gubun})
            self.jango_dict[sCode].update({"(최우선)매도호가": first_sell_price})
            self.jango_dict[sCode].update({"(최우선)매수호가": first_buy_price})
            self.logging.logger.debug("잔고 종료")
            if stock_quan == 0:
                self.logging.logger.debug("설마 여기서?")
                del self.jango_dict[sCode]

    #송수신 메세지 get
    def msg_slot(self, sScrNo, sRQName, sTrCode, msg):
        self.logging.logger.debug("스크린: %s, 요청이름: %s, tr코드: %s --- %s" %(sScrNo, sRQName, sTrCode, msg))

    def file_delete(self):
        if os.path.isfile("files/condition_stock.txt"):
            os.remove("files/condition_stock.txt")

    def lastorder(self):
        self.logging.logger.debug("last_order")
        for code in self.ten_cal_dict.keys():
            if self.ten_cal_dict[code]["실제주식개수"] > 0:
                order_success = self.dynamicCall(
                    "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                    ["신규매도", self.ten_cal_dict[code]["주문용스크린번호"], self.account_num, 2, code, self.ten_cal_dict[code]['주식개수'], 0,
                     self.realType.SENDTYPE['거래구분']['시장가'], ""])
                if order_success == 0:
                    self.logging.logger.debug("마지막 매도주문 전달 성공")
                    # del self.invest_dict[code]
                else:
                    self.logging.logger.debug("마지막 매도주문 전달 실패")

    ##### 새로운 추가 #####
    def get_today_stock_kiwoom_db(self, sPrevNext="0"):
        self.dynamicCall("SetInputValue(QString, QString)", "시장구분", "000") # 코스피 + 코스닥 전체
        self.dynamicCall("SetInputValue(QString, QString)", "정렬구분", "1") # 거래대금 기준
        self.dynamicCall("SetInputValue(QString, QString)", "관리종목포함", "16") # 관리종목 포함
        self.dynamicCall("SetInputValue(QString, QString)", "신용구분", "0") #신용 전체 조회
        self.dynamicCall("SetInputValue(QString, QString)", "거래량구분", "0") # 전체 조회
        self.dynamicCall("SetInputValue(QString, QString)", "가격구분", "0") # 전체조회
        self.dynamicCall("SetInputValue(QString, QString)", "거래대금구분", "0") # 전체조회
        self.dynamicCall("SetInputValue(QString, QString)", "장운영구분", "0") # 전체조회
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "당일거래량상위요청", "opt10030", sPrevNext, self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
        self.calculator_event_loop.exec_()
    #
    # def get_today_stock_code_db(self, sPrevNext="0"):
    #     self.dynamicCall("SetInputValue(QString, QString)", "시장구분", "000") # 코스피 + 코스닥 전체
    #     self.dynamicCall("SetInputValue(QString, QString)", "정렬구분", "3") # 거래대금 기준
    #     self.dynamicCall("SetInputValue(QString, QString)", "관리종목포함", "0") # 관리종목 포함
    #     self.dynamicCall("SetInputValue(QString, QString)", "신용구분", "0") #신용 전체 조회
    #     self.dynamicCall("SetInputValue(QString, QString)", "거래량구분", "0") # 전체 조회
    #     self.dynamicCall("SetInputValue(QString, QString)", "가격구분", "0") # 전체조회
    #     self.dynamicCall("SetInputValue(QString, QString)", "거래대금구분", "0") # 전체조회
    #     self.dynamicCall("SetInputValue(QString, QString)", "장운영구분", "0") # 전체조회
    #     self.dynamicCall("CommRqData(QString, QString, int, QString)", "당일투자종목선정", "opt10030", sPrevNext, self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
    #     self.calculator_event_loop.exec_()
    #
    # def today_screen_number_setting(self):
    #     screen_overwrite = []
    #     #포트폴리오에 담겨있는 종목들
    #     for code in self.invest_dict.keys():
    #         if code not in screen_overwrite:
    #             screen_overwrite.append(code)
    #     # 스크린번호 할당
    #     cnt = 0
    #     for code in screen_overwrite:
    #         temp_screen = int(self.screen_invest_stock)
    #         meme_screen = int(self.screen_invest_meme_stock)
    #         if (cnt % 50) == 0:
    #             temp_screen += 1
    #             self.screen_invest_stock = str(temp_screen)
    #         if (cnt % 50) == 0:
    #             meme_screen += 1
    #             self.screen_invest_meme_stock = str(meme_screen)
    #         if code in self.invest_dict.keys():
    #             self.invest_dict[code].update({"스크린번호": str(self.screen_invest_stock)})
    #             self.invest_dict[code].update({"주문용스크린번호": str(self.screen_invest_meme_stock)})
    #         elif code not in self.invest_dict.keys():
    #             self.invest_dict.update({code: {"스크린번호": str(self.screen_invest_stock), "주문용스크린번호": str(self.screen_invest_meme_stock)}})
    #         cnt += 1
    #
    # def fivemin_kiwoom_db(self, code=None, minute="5", sPrevNext="0"):
    #     #QTest.qWait(3600)  # 3.6초(4초로 변경)마다 딜레이를 준다. 신경망 출력까지 5 ~ 6초 걸리므로 안해도 됨
    #     self.logging.logger.debug("fivemin_update_call")
    #     self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
    #     self.dynamicCall("SetInputValue(QString, QString)", "틱범위", minute)
    #     self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
    #     self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식5분봉차트조회", "opt10080", sPrevNext, self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
    #     self.calculator_event_loop.exec_()
    #
    # def fivemin_oneday_kiwoom_db(self, code=None, minute="5", sPrevNext="0"):
    #     QTest.qWait(3600)  # 3.6초(4초로 변경)마다 딜레이를 준다. 신경망 출력까지 5 ~ 6초 걸리므로 안해도 됨
    #     self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
    #     self.dynamicCall("SetInputValue(QString, QString)", "틱범위", minute)
    #     self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
    #     self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식5분봉일일차트조회", "opt10080", sPrevNext, self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
    #     self.calculator_event_loop.exec_()
    #
    # def onemin_chegeul_kiwoom_db(self, code=None, minute="1", sPrevNext="0"):
    #     QTest.qWait(3600)
    #     self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
    #     self.dynamicCall("SetInputValue(QString, QString)", "당일전일", "1") #당일 1 전일 2
    #     self.dynamicCall("SetInputValue(QString, QString)", "틱분", minute)
    #     self.dynamicCall("SetInputValue(QString, QString)", "시간", "0000") # 이렇게 하면 전체를 조사
    #     self.dynamicCall("CommRqData(QString, QString, int, QString)", "당일전일체결요청", "opt10084", sPrevNext, self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
    #     self.calculator_event_loop.exec_()
    #
    # def onemin_chegeul_invest_db(self, code=None, minute="1", sPrevNext="0"):
    #     #QTest.qWait(3600) 신경망 때문에 굳이 필요없을 듯
    #     self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
    #     self.dynamicCall("SetInputValue(QString, QString)", "당일전일", "1") #당일 1 전일 2
    #     self.dynamicCall("SetInputValue(QString, QString)", "틱분", minute)
    #     self.dynamicCall("SetInputValue(QString, QString)", "시간", "0000") # 이렇게 하면 전체를 조사
    #     self.dynamicCall("CommRqData(QString, QString, int, QString)", "체결강도1분단위조회", "opt10084", sPrevNext, self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
    #     self.calculator_event_loop.exec_()
    #
    # def chegeul_calcul_kiwoom_db(self, code=None, minute="0", sPrevNext="0"):
    #     QTest.qWait(3600)
    #     self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
    #     self.dynamicCall("SetInputValue(QString, QString)", "당일전일", "1")  # 당일 1 전일 2
    #     self.dynamicCall("SetInputValue(QString, QString)", "틱분", minute) # 틱
    #     self.dynamicCall("SetInputValue(QString, QString)", "시간", "0900")  # 9시의 최초 미상의 거래량 데이터 찾기
    #     self.dynamicCall("CommRqData(QString, QString, int, QString)", "최초누락거래량확인", "opt10084", sPrevNext, self.screen_calculation_stock)  # Tr서버로 전송 -Transaction
    #     self.calculator_event_loop.exec_()
    #
    # # invest_dict에 있는 각 종목별로 주식5분봉차트조회 -> 최신 10개 데이터를 받고 최근의 시고저종의 전일종가 비율, 거래량 비율, 5, 10 이동평균 계산
    # # invest_dict의 종목코드의 '입력데이터' 항목에 input_data list를 저장
    # def input_update(self):
    #     self.logging.logger.debug("input_update")
    #     now = datetime.now().today()
    #     count = 0
    #     for code in self.invest_dict.keys():
    #         count += 1
    #         self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock)  # 스크린 연결 끊기
    #         self.logging.logger.debug("count : %s / %s Stock Code : %s is updating... " % (count, len(self.invest_dict.keys()), code))
    #         self.code = code
    #         # fivemin_kiwoom_db -> onemin_chegeul_invest_db
    #         self.onemin_chegeul_invest_db(code=code)
    #
    #         self.logging.logger.debug("state making...")
    #         state = copy.deepcopy(self.invest_dict[code]['입력데이터'])
    #         #state.extend(self.get_states(code=code))
    #
    #         # 바깥으로 나가서 다른 폴더의 경로 사용
    #         filepath = "C:/Users/suk14/PycharmProjects/rltrader"
    #         fpath = os.path.join(filepath, 'data/fivedata/{}_data.txt'.format(code))
    #         saving_data = open(fpath, "w", encoding="utf8")
    #         # state를 file에 저장
    #         for content in state:
    #             saving_data.write("%s\t" % (content))
    #         saving_data.close()
    #         # 다른 가상환경의 calculate.py 함수 실행
    #         # 궁금점 : 그 py가 끝날때까지 기다리는가?? (놀랍게도... 기다려줌)
    #         self.logging.logger.debug("os command start")
    #         # 정확히는 get_action이 rltrader의 calculate.py을 실행함
    #         self.get_action(code=code)
    #         # rltrader files의 행동결과 받아오기
    #         filepath = "C:/Users/suk14/PycharmProjects/rltrader/files/" + code + "_data.txt"
    #         get_action = open(filepath, "r", encoding="utf8")
    #         data = get_action.read()
    #         get_action.close()
    #         data.strip()
    #         act = int(data)
    #         self.logging.logger.debug("os command done and action")
    #         #
    #         self.acting(code=code, action=act)
    #         self.save_status(code=code, time=now)
    #         #self.logging.logger.debug("Stock Code : %s is finished..." % (code))
    #
    # def get_states(self, code):
    #     #self.logging.logger.debug("get_states")
    #     testsample = copy.deepcopy(self.invest_dict[code])
    #     max_stocks = int((testsample['포트폴리오가치'] / testsample['현재가']))
    #     ratio = float(0)
    #     ratio = testsample['주식개수'] / max_stocks
    #     pv_ratio = testsample['포트폴리오가치'] / testsample['기준포트폴리오가치']
    #     return ratio, pv_ratio
    # # invest_dict에 있는 각 종목별로 입력데이터를 PPO(훈련된) 모델에 넣어서 행동, 예측을 받음
    # # 그 다음에 acting으로 행동(0 ~ 9)에 대한 매수, 매도 행위 수행
    # # def predicting(self, code):
    # #     state = self.invest_dict[code]['입력데이터']
    # #     state.extend(self.get_states(code=code))
    # #     # list
    # #     state = np.stack([state]).astype(dtype=np.float32)
    # #     self.logging.logger.debug("input_finished")
    # #     act, v_pred = self.PPO.get_action(state)
    # #     act, v_pred = np.asscalar(act), np.asscalar(v_pred)
    # #     return act
    # # 포트폴리오가치 / 현재가 = 최대 보유 가능 주식수
    # # num_stocks는 보유할 수 이므로 현재 주식보다 작다면 매도를 크다면 매수를 해야함
    #
    # def get_action(self, code):
    #     os.chdir("C:/Users/suk14/PycharmProjects/rltrader")
    #     exam_string = "python calculate.py" + " " + str(code)
    #     os.system("conda activate rltraderproj && " + exam_string)
    #     # 원래대로 돌아오기
    #     # os.system("conda deactivate")
    #     os.chdir("C:/Users/suk14/PycharmProjects/week1")
    #     os.system("conda activate trade_32")
    #     #self.logging.logger.debug("os command get action finish")
    #
    # def acting(self, code, action):
    #     action = float(action / 10) # 0.0 ~ 0.9로의 변환
    #     testsample = copy.deepcopy(self.invest_dict[code])
    #     num_stocks = int(action * int((testsample["포트폴리오가치"] / testsample["현재가"])))
    #     trading_stocks = num_stocks - testsample["주식개수"]
    #     if trading_stocks > 0: # 매수를 해야하는 상황
    #         order_success = self.dynamicCall(
    #             "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
    #             ["신규매수", self.invest_dict[code]["주문용스크린번호"], self.account_num, 1, code, int(trading_stocks), "",
    #              self.realType.SENDTYPE['거래구분']['시장가'], ""])
    #         if order_success == 0:
    #             self.logging.logger.debug("매수주문 전달 성공")
    #         else:
    #             self.logging.logger.debug("매수주문 전달 실패")
    #         #QTest.qWait(5000) # 5초정도 기다림
    #     elif trading_stocks < 0: # 매도를 해야하는 상황 # int
    #         trading_stocks = -trading_stocks
    #         order_success = self.dynamicCall(
    #             "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
    #             ["신규매도", self.invest_dict[code]["주문용스크린번호"], self.account_num, 2, code, int(trading_stocks), "",
    #              self.realType.SENDTYPE['거래구분']['시장가'], ""])
    #         if order_success == 0:
    #             self.logging.logger.debug("매도주문 전달 성공")
    #             # del self.invest_dict[code]
    #         else:
    #             self.logging.logger.debug("매도주문 전달 실패")
    #         #QTest.qWait(5000) # 5초정도 기다림
    #     else:
    #         None
    #
    # def save_status(self, code, time):
    #     self.logging.logger.debug("saving status...")
    #     h = str(time.hour)
    #     m = str(time.minute)
    #     s = str(time.second)
    #     if int(h) < 10:
    #         h = "0" + h
    #     if int(m) < 10:
    #         m = "0" + m
    #     if int(s) < 10:
    #         s = "0" + s
    #     timestr = h + m + s
    #     # 기록 대상 : 시간, 종목 코드, 현재가, 주식개수, 주식개수, 포트폴리오가치, 기준포트폴리오가치
    #     testsample = copy.deepcopy(self.invest_dict[code])
    #     curr_price = testsample["현재가"]
    #     num_stocks = testsample["주식개수"]
    #     money = testsample["운용금액"]
    #     pv = testsample["포트폴리오가치"]
    #     base_pv = testsample["기준포트폴리오가치"]
    #     filepath = "C:/Users/suk14/PycharmProjects/week1/files/todaysrecord"
    #     file = open(filepath, "a", encoding="utf8")
    #     file.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (timestr, code, str(curr_price), str(num_stocks), str(money), str(pv), str(base_pv)))
    #     file.close()
    #
    # def lastorder(self):
    #     self.logging.logger.debug("last_order")
    #     for code in self.invest_dict.keys():
    #         if self.invest_dict[code]["주식개수"] > 0:
    #             order_success = self.dynamicCall(
    #                 "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
    #                 ["신규매도", self.invest_dict[code]["주문용스크린번호"], self.account_num, 2, code, self.invest_dict[code]['주식개수'], 0,
    #                  self.realType.SENDTYPE['거래구분']['시장가'], ""])
    #             if order_success == 0:
    #                 self.logging.logger.debug("마지막 매도주문 전달 성공")
    #                 # del self.invest_dict[code]
    #             else:
    #                 self.logging.logger.debug("마지막 매도주문 전달 실패")
