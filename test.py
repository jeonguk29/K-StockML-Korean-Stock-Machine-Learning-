import ssl
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pykrx import stock
import time
from tqdm import tqdm
import warnings
from datetime import datetime

# SSL 인증서 검증 비활성화
ssl._create_default_https_context = ssl._create_unverified_context

warnings.filterwarnings('ignore')

class StockScreener:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
    
    def get_stock_lists(self):
        """KOSPI와 KOSDAQ 상장기업 목록을 가져옴"""
        today = datetime.today().strftime("%Y%m%d")
        
        # KOSPI 종목 리스트
        kospi_tickers = stock.get_market_ticker_list(market="KOSPI")
        kospi_names = []
        kospi_sectors = []
        
        print("KOSPI 종목 정보 수집 중...")
        for ticker in tqdm(kospi_tickers):
            name = stock.get_market_ticker_name(ticker)
            kospi_names.append(name)
            # 네이버 금융에서 업종 정보 가져오기
            sector = self.get_sector_info(ticker)
            kospi_sectors.append(sector)
            time.sleep(0.1)  # 네이버 서버 부하 방지
        
        kospi_df = pd.DataFrame({
            '종목코드': kospi_tickers,
            '종목명': kospi_names,
            '업종': kospi_sectors,
            '시장구분': 'KOSPI'
        })

        # KOSDAQ 종목 리스트
        kosdaq_tickers = stock.get_market_ticker_list(market="KOSDAQ")
        kosdaq_names = []
        kosdaq_sectors = []
        
        print("KOSDAQ 종목 정보 수집 중...")
        for ticker in tqdm(kosdaq_tickers):
            name = stock.get_market_ticker_name(ticker)
            kosdaq_names.append(name)
            # 네이버 금융에서 업종 정보 가져오기
            sector = self.get_sector_info(ticker)
            kosdaq_sectors.append(sector)
            time.sleep(0.1)  # 네이버 서버 부하 방지
        
        kosdaq_df = pd.DataFrame({
            '종목코드': kosdaq_tickers,
            '종목명': kosdaq_names,
            '업종': kosdaq_sectors,
            '시장구분': 'KOSDAQ'
        })

        # 데이터프레임 합치기
        self.stock_df = pd.concat([kospi_df, kosdaq_df])
        return self.stock_df
    
    def get_sector_info(self, code):
        """네이버 금융에서 업종 정보를 가져옴"""
        url = f'https://finance.naver.com/item/main.naver?code={code}'
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 업종 정보 추출
            sector = soup.select_one('div.trade_compare > h4 > em > a')
            return sector.text if sector else "기타"
        except:
            return "기타"
    
    def get_stock_info(self, code):
        """개별 종목의 투자지표 정보를 가져옴"""
        url = f'https://finance.naver.com/item/main.naver?code={code}'
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # PER, PBR 추출
            per = soup.select_one('#_per')
            pbr = soup.select_one('#_pbr')
            
            per = float(per.text.replace(',', '')) if per else None
            pbr = float(pbr.text.replace(',', '')) if pbr else None
            
            return per, pbr
        except:
            return None, None
    
    def analyze_stocks(self):
        """전체 종목 분석"""
        # 기본 정보 가져오기
        self.get_stock_lists()
        
        # 투자지표 정보 추가
        tqdm.pandas()
        print("투자지표 수집 중...")
        
        def get_indicators(code):
            per, pbr = self.get_stock_info(code)
            time.sleep(0.1)  # 네이버 서버 부하 방지
            return pd.Series([per, pbr])
        
        self.stock_df[['PER', 'PBR']] = self.stock_df['종목코드'].progress_apply(get_indicators)
        
        # NaN 값 제거
        self.stock_df = self.stock_df.dropna(subset=['PER', 'PBR'])
        
        # 비정상적인 값 제거 (PER이 0이하이거나 1000이상인 경우)
        self.stock_df = self.stock_df[(self.stock_df['PER'] > 0) & (self.stock_df['PER'] < 1000)]
        
        return self.stock_df
    
    def find_undervalued_stocks(self, top_n=5):
        """업종별 저평가 종목 찾기"""
        # 업종별 평균 PER, PBR 계산
        industry_avg = self.stock_df.groupby('업종').\
            agg({'PER': 'mean', 'PBR': 'mean'}).\
            rename(columns={'PER': 'industry_PER', 'PBR': 'industry_PBR'})
        
        # 개별 종목에 업종 평균 추가
        self.stock_df = self.stock_df.merge(industry_avg, on='업종')
        
        # PER, PBR 상대값 계산 (낮을수록 저평가)
        self.stock_df['PER_ratio'] = self.stock_df['PER'] / self.stock_df['industry_PER']
        self.stock_df['PBR_ratio'] = self.stock_df['PBR'] / self.stock_df['industry_PBR']
        
        # 종합 점수 계산 (PER와 PBR 비율의 평균)
        self.stock_df['value_score'] = (self.stock_df['PER_ratio'] + self.stock_df['PBR_ratio']) / 2
        
        # 업종별로 가장 저평가된 종목 선정
        undervalued = self.stock_df.sort_values('value_score').\
            groupby('업종').head(top_n).\
            sort_values(['업종', 'value_score'])
        
        return undervalued[['종목명', '업종', 'PER', 'PBR', 'industry_PER', 'industry_PBR', 'value_score']]

# 실행
if __name__ == "__main__":
    screener = StockScreener()
    print("주식 데이터 분석 중...")
    screener.analyze_stocks()
    
    print("\n업종별 저평가 종목 추천 (상위 3개):")
    recommended_stocks = screener.find_undervalued_stocks(top_n=3)
    print(recommended_stocks.to_string())