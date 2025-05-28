import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score
from pykrx import stock
from datetime import datetime, timedelta

# 거시경제/산업분석 함수 임포트
from stock_investment_pipeline import macro_analysis, industry_analysis

# 1. 실제 데이터 준비 (pykrx 활용)
def get_real_stock_data(n_sample=100):
    today = datetime.today()
    start = today - timedelta(days=365*2)  # 2년치 데이터
    start_str = start.strftime('%Y%m%d')
    end_str = today.strftime('%Y%m%d')
    tickers = stock.get_market_ticker_list(market="KOSPI")[:n_sample]
    all_data = []
    for code in tickers:
        df = stock.get_market_ohlcv_by_date(start_str, end_str, code)
        if len(df) < 80:  # 데이터 부족 종목 제외
            continue
        df = df.reset_index()
        df['code'] = code
        all_data.append(df)
    df_all = pd.concat(all_data)
    return df_all

def make_ml_dataset(df_all):
    # 3개월(60영업일) 뒤 수익률 계산
    dfs = []
    for code, df in df_all.groupby('code'):
        df = df.sort_values('날짜').reset_index(drop=True)
        df['return_3m'] = (df['종가'].shift(-60) - df['종가']) / df['종가']
        # 특성: 시가, 고가, 저가, 종가, 거래량 (정규화)
        features = df[['시가', '고가', '저가', '종가', '거래량']].copy()
        features = (features - features.mean()) / features.std()
        features.columns = [f'{c}' for c in features.columns]
        out = features.copy()
        out['target_reg'] = df['return_3m']
        out['target_cls'] = (df['return_3m'] > 0.1).astype(int)
        out['code'] = code
        out['date'] = df['날짜']
        dfs.append(out)
    data = pd.concat(dfs)
    # 결측치/미래 없는 row 제거
    data = data.dropna(subset=['target_reg'])
    return data

def get_code_name_sector_dict():
    # pykrx에서 종목코드-종목명, 종목코드-업종(산업군) dict 생성
    tickers = stock.get_market_ticker_list(market="KOSPI")
    code2name = {code: stock.get_market_ticker_name(code) for code in tickers}
    # 업종 정보는 pykrx에서 직접 제공하지 않으므로, 네이버 금융 크롤링 등으로 확장 가능
    # 여기서는 임시로 모두 '기타'로 표기
    code2sector = {code: '기타' for code in tickers}
    return code2name, code2sector

def main():
    print('[실제 데이터 기반 ML 예시]')
    print('주가 데이터 수집 중...')
    df_all = get_real_stock_data(n_sample=50)  # 50종목 예시
    print('ML 데이터셋 생성 중...')
    data = make_ml_dataset(df_all)
    X = data[['시가', '고가', '저가', '종가', '거래량']]
    y_reg = data['target_reg']
    y_cls = data['target_cls']
    X_train, X_test, y_reg_train, y_reg_test, y_cls_train, y_cls_test = train_test_split(
        X, y_reg, y_cls, test_size=0.2, random_state=42)

    # 회귀 모델 학습 및 예측
    lr = LinearRegression().fit(X_train, y_reg_train)
    rf_reg = RandomForestRegressor(random_state=42).fit(X_train, y_reg_train)
    y_pred_lr = lr.predict(X_test)
    y_pred_rf = rf_reg.predict(X_test)
    print('[회귀] LinearRegression MSE:', mean_squared_error(y_reg_test, y_pred_lr))
    print('[회귀] RandomForestRegressor MSE:', mean_squared_error(y_reg_test, y_pred_rf))

    # 분류 모델 학습 및 예측
    rf_cls = RandomForestClassifier(random_state=42).fit(X_train, y_cls_train)
    y_pred_cls = rf_cls.predict(X_test)
    print('[분류] RandomForestClassifier 정확도:', accuracy_score(y_cls_test, y_pred_cls))

    # 종목명, 산업군 dict
    code2name, code2sector = get_code_name_sector_dict()

    # 예측 결과로 추천 종목 예시 (상위 10개)
    test_df = X_test.copy()
    test_df['pred_reg'] = y_pred_rf
    test_df['pred_cls'] = y_pred_cls
    test_df['code'] = data.iloc[X_test.index]['code'].values
    test_df['date'] = data.iloc[X_test.index]['date'].values
    test_df['종목명'] = test_df['code'].map(code2name)
    test_df['산업군'] = test_df['code'].map(code2sector)
    # 3개월 뒤 수익률 예측이 높은 순 추천
    top_recommend = test_df.sort_values('pred_reg', ascending=False).head(10)
    print('\n[추천 종목 TOP 10 - 3개월 뒤 수익률 예측 기준]')
    print(top_recommend[['종목명', '산업군', 'code', 'date', 'pred_reg']].to_string(index=False))
    # 10% 초과로 분류된 종목만 추천
    print('\n[추천 종목 - 10% 초과로 분류된 종목]')
    print(test_df[test_df['pred_cls'] == 1][['종목명', '산업군', 'code', 'date', 'pred_reg']].to_string(index=False))

    # 전체 해석 출력
    print('\n[해석 및 요약]')
    print('1. 거시경제 분석 결과:')
    macro = macro_analysis()
    print(macro)
    print('\n2. 산업분석 결과:')
    industry_df = industry_analysis(top_n=3)
    print(industry_df)
    print('\n3. 종목분석 결과: 위 표에서 예측 수익률이 높거나 10% 초과로 분류된 종목이 추천 대상입니다.')
    print('   실제 투자 전에는 재무제표, 산업 트렌드, 뉴스 등 추가 분석이 필요합니다.')

if __name__ == "__main__":
    main() 