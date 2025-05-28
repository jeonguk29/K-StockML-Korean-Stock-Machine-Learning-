import requests
import pandas as pd
from datetime import datetime

# 1. 거시경제 분석 단계

def get_kospi_index():
    """코스피 지수 가져오기 (네이버 금융)"""
    try:
        url = 'https://finance.naver.com/sise/sise_index.naver?code=KOSPI'
        res = requests.get(url)
        df = pd.read_html(res.text)[0]
        price = df.iloc[0, 1]
        return float(str(price).replace(',', ''))
    except:
        return None

def get_kosdaq_index():
    """코스닥 지수 가져오기 (네이버 금융)"""
    try:
        url = 'https://finance.naver.com/sise/sise_index.naver?code=KOSDAQ'
        res = requests.get(url)
        df = pd.read_html(res.text)[0]
        price = df.iloc[0, 1]
        return float(str(price).replace(',', ''))
    except:
        return None

def get_usd_krw_exchange_rate():
    """원/달러 환율 (네이버 금융)"""
    try:
        url = 'https://finance.naver.com/marketindex/exchangeDetail.naver?marketindexCd=FX_USDKRW'
        res = requests.get(url)
        df = pd.read_html(res.text)[0]
        price = df.iloc[0, 1]
        return float(str(price).replace(',', ''))
    except:
        return None

def get_interest_rate():
    """기준금리, 국고채 3년물 등 (구조만 설계)"""
    # TODO: 실제 데이터 수집 코드 구현
    return None

def get_cpi_ppi():
    """CPI, PPI (구조만 설계)"""
    # TODO: 실제 데이터 수집 코드 구현
    return None

def macro_analysis():
    kospi = get_kospi_index()
    kosdaq = get_kosdaq_index()
    rate = get_interest_rate()
    fx = get_usd_krw_exchange_rate()
    cpi_ppi = get_cpi_ppi()
    # TODO: 지표를 종합적으로 분석하여 시장이 호황/침체인지 판단
    # 예시: 단순히 KOSPI가 2500 이상이면 호황, 아니면 침체
    if kospi and kospi > 2500:
        market_status = '호황'
    else:
        market_status = '침체'
    return {
        'KOSPI': kospi,
        'KOSDAQ': kosdaq,
        'Interest Rate': rate,
        'USD/KRW': fx,
        'CPI/PPI': cpi_ppi,
        'Market Status': market_status
    }

# 2. 산업분석 단계 (실제 데이터 기반)
def industry_analysis(top_n=3):
    """
    네이버 금융 업종별 시세에서 당일 등락률(전일대비)이 높은 상위 n개 산업군 추천
    """
    url = 'https://finance.naver.com/sise/sise_group.naver?type=upjong'
    res = requests.get(url)
    df = pd.read_html(res.text, header=0)[0]  # 첫 번째 테이블이 업종별 시세
    df = df.dropna(subset=['전일대비'])
    # '전일대비' 컬럼에서 %와 +, -, , 제거 후 float 변환
    df['전일대비(수치)'] = df['전일대비'].astype(str).str.replace('%','').str.replace('+','').str.replace(',','')
    df['전일대비(수치)'] = pd.to_numeric(df['전일대비(수치)'], errors='coerce')
    df = df.dropna(subset=['전일대비(수치)'])
    # 상위 n개 산업군 추출
    top_industries = df.sort_values('전일대비(수치)', ascending=False).head(top_n)
    result = top_industries[['업종명', '전일대비']].reset_index(drop=True)
    return result

# 3. 종목분석 단계 (머신러닝 등)
INDUSTRY_GROUPS = {
    '전통': ['철강', '석유화학', '은행'],
    '성장': ['2차전지', 'AI 반도체', '바이오'],
    '방어': ['통신', '필수소비재']
}

def stock_analysis(selected_industries):
    # TODO: 산업군 내 종목별 투자매력 평가 (머신러닝 등)
    # 예시: 임의의 종목 추천
    recommendations = {}
    for group in selected_industries:
        if group in INDUSTRY_GROUPS:
            recommendations[group] = INDUSTRY_GROUPS[group][:2]  # 각 산업군 상위 2개 종목 추천
        else:
            recommendations[group] = ['(실제 종목 추천 필요)']
    return recommendations

# 전체 파이프라인 실행
def run_pipeline():
    print('[1] 거시경제 분석')
    macro = macro_analysis()
    print(macro)
    if macro['Market Status'] == '침체':
        print('시장 침체: 종목 추천을 보수적으로 진행합니다.')
    else:
        print('시장 호황: 적극적으로 종목 추천을 진행합니다.')

    print('\n[2] 산업분석 (실제 데이터 기반)')
    industry_df = industry_analysis(top_n=3)
    print(industry_df)
    selected = industry_df['업종명'].tolist()
    print(f'추천 산업군: {selected}')

    print('\n[3] 종목분석')
    stock_recs = stock_analysis(selected)
    print('추천 종목:', stock_recs)

if __name__ == "__main__":
    run_pipeline() 