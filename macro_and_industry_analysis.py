import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from stock_investment_pipeline import get_kospi_index, get_kosdaq_index, get_usd_krw_exchange_rate

# 1. 거시경제 분석 (네이버 금융 실시간)
def macro_analysis():
    kospi = get_kospi_index()
    kosdaq = get_kosdaq_index()
    usdkrw = get_usd_krw_exchange_rate()
    print(f"KOSPI: {kospi}")
    print(f"KOSDAQ: {kosdaq}")
    print(f"USD/KRW: {usdkrw}")

    if None in [kospi, kosdaq, usdkrw]:
        print("⚠️ KOSPI, KOSDAQ, 환율 데이터가 충분하지 않습니다.")
        return None

    # 간단 경기 진단
    if kospi > 2500 and kosdaq > 800 and usdkrw < 1300:
        econ_status = '호황'
    elif kospi < 2200 or kosdaq < 700 or usdkrw > 1400:
        econ_status = '침체'
    else:
        econ_status = '불황'

    print(f"\n[경기 진단 결과] 현재는 '{econ_status}' 국면으로 판단됩니다.")
    return econ_status

# 2. 산업군 추천 + 머신러닝 기반 종목 추천
def recommend_stocks_by_industry(econ_status, file_path='dataSet.xlsx'):
    # 데이터 불러오기
    df = pd.read_excel(file_path)

    # 수치형 컬럼 정리
    numeric_cols = ['PER', 'PBR', 'ROE', '부채비율', '영업이익률', '시가총액', '3개월수익률']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=numeric_cols + ['산업군'])

    # 산업 점수 계산
    if econ_status == '호황':
        df['산업점수'] = 0.6 * df['ROE'] + 0.4 * df['영업이익률']
    else:
        df['산업점수'] = 0.7 * df['ROE'] - 0.3 * df['부채비율'] / 100

    # 산업군별 평균 점수 기준 상위 3개 산업군 선정
    top_industries = df.groupby('산업군')['산업점수'].mean().sort_values(ascending=False).head(3).index
    df_top = df[df['산업군'].isin(top_industries)]

    # 회귀 모델 학습을 위한 컬럼
    features = ['PER', 'PBR', 'ROE', '부채비율', '영업이익률', '시가총액']
    target = '3개월수익률'
    result_df = pd.DataFrame()

    for industry in top_industries:
        industry_df = df_top[df_top['산업군'] == industry]
        if len(industry_df) < 10:
            continue

        X = industry_df[features]
        y = industry_df[target]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = RandomForestRegressor(random_state=42)
        model.fit(X_train, y_train)

        industry_df['예측수익률'] = model.predict(X)

        top3 = industry_df.sort_values('예측수익률', ascending=False).head(3)
        result_df = pd.concat([result_df, top3])

    return result_df[['회사명', '산업군', '예측수익률', '3개월수익률', 'PER', 'PBR', 'ROE', '부채비율', '영업이익률']]

# 3. 실행부
if __name__ == "__main__":
    econ_status = macro_analysis()
    if econ_status:
        recommendations = recommend_stocks_by_industry(econ_status, file_path='dataSet.xlsx')
        print("\n[📈 산업군별 추천 종목 상위 3개]")
        print(recommendations.to_string(index=False))
