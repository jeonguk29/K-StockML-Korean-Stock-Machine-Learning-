import numpy as np
import pandas as pd

def diagnose_market_phase(
    kospi=None, sp500=None, vkospi=None,
    kor_bond3y=None, base_rate=None, m2_growth=None,
    usdkrw=None, us10y=None
):
    # 진단 근거 표 생성
    data = {
        '지표': ['KOSPI', 'S&P500', 'VKOSPI', '국고채 3년', '기준금리', 'M2 증가율', 'USD/KRW', '미국 10Y'],
        '값': [kospi, sp500, vkospi, kor_bond3y, base_rate, m2_growth, usdkrw, us10y]
    }
    df = pd.DataFrame(data)
    print('[시장 주요 지표]')
    print(df.to_string(index=False))

    # 국면 진단 로직
    # (예시: 실제로는 더 정교하게 조합 가능)
    # - 금리↓: 기준금리, 국고채3년, 미국10Y 모두 2.5 이하
    # - 금리↑: 기준금리, 국고채3년, 미국10Y 중 2개 이상 3.0 이상
    # - 지수↑: KOSPI > 2000, S&P500 > 4000
    # - 지수↓: KOSPI < 2000, S&P500 < 4000
    # - 경기지표↑: M2 증가율 7 이상, VKOSPI < 20
    # - 경기지표↓: M2 증가율 5 이하, VKOSPI > 25
    # - 환율↑: USD/KRW > 1300

    # 조건 플래그
    rate_down = sum([
        (base_rate is not None and base_rate <= 2.5),
        (kor_bond3y is not None and kor_bond3y <= 2.5),
        (us10y is not None and us10y <= 2.5)
    ]) >= 2
    rate_up = sum([
        (base_rate is not None and base_rate >= 3.0),
        (kor_bond3y is not None and kor_bond3y >= 3.0),
        (us10y is not None and us10y >= 3.0)
    ]) >= 2
    index_up = sum([
        (kospi is not None and kospi >= 2000),
        (sp500 is not None and sp500 >= 4000)
    ]) >= 2
    index_down = sum([
        (kospi is not None and kospi < 2000),
        (sp500 is not None and sp500 < 4000)
    ]) >= 2
    econ_up = sum([
        (m2_growth is not None and m2_growth >= 7),
        (vkospi is not None and vkospi < 20)
    ]) >= 1
    econ_down = sum([
        (m2_growth is not None and m2_growth <= 5),
        (vkospi is not None and vkospi > 25)
    ]) >= 1
    # 국면 진단
    phase = '판단불가'
    if rate_down and index_up and econ_up:
        phase = '회복기'
    elif rate_up and index_up and econ_up:
        phase = '과열기'
    elif rate_up and index_down:
        phase = '침체기'
    elif rate_down and index_down and econ_down:
        phase = '불황기'
    print('\n[시장 국면 진단 결과]')
    print(f'현재 시장 국면: {phase}')
    '''
    print('\n[진단 근거]')
    print(f'- 금리↓: {rate_down}, 금리↑: {rate_up}')
    print(f'- 지수↑: {index_up}, 지수↓: {index_down}')
    print(f'- 경기지표↑: {econ_up}, 경기지표↓: {econ_down}')
    print(f'- (판단 로직: 회복기=금리↓+지수↑+경기↑, 과열기=금리↑+지수↑+경기↑, 침체기=금리↑+지수↓, 불황기=금리↓+지수↓+경기↓)')
    '''
if __name__ == "__main__":
    # 예시: 각 분석 파일에서 값 수동 입력 또는 import해서 전달
    # 아래 값은 예시이므로 실제 분석 결과로 대체하세요
    kospi = 2700
    sp500 = 5200
    vkospi = 15
    kor_bond3y = 2.4
    base_rate = 3.5
    m2_growth = 7.1
    usdkrw = 1370
    us10y = 4.3
    diagnose_market_phase(
        kospi=kospi, sp500=sp500, vkospi=vkospi,
        kor_bond3y=kor_bond3y, base_rate=base_rate, m2_growth=m2_growth,
        usdkrw=usdkrw, us10y=us10y
    ) 