import yfinance as yf
import pandas as pd
import numpy as np

def get_usdkrw():
    df = yf.download('USDKRW=X', period='5d')
    if df.empty:
        return np.nan
    return float(df['Close'].iloc[-1])

def get_us10y():
    df = yf.download('^TNX', period='5d')
    if df.empty:
        return np.nan
    # yfinance의 ^TNX는 10배수로 제공됨
    return float(df['Close'].iloc[-1]) / 10

def get_sp500():
    df = yf.download('^GSPC', period='5d')
    if df.empty:
        return np.nan
    return float(df['Close'].iloc[-1])

if __name__ == "__main__":
    usdkrw = get_usdkrw()
    us10y = get_us10y()
    sp500 = get_sp500()
    table = pd.DataFrame({
        '지표': ['USD/KRW 환율', '미국 10Y 국채금리', 'S&P500'],
        '값': [usdkrw, us10y, sp500]
    })
    print("[환율 및 글로벌 지표]")
    print(table.to_string(index=False))
    print("\n[판단]")
    # 1. USD/KRW 환율
    if not np.isnan(usdkrw):
        if usdkrw >= 1300:
            print(f"USD/KRW {usdkrw:.2f}: 1300 이상, 외국인 수급 불안 심리 반영 가능")
        else:
            print(f"USD/KRW {usdkrw:.2f}: 1300 미만, 비교적 안정")
    else:
        print("USD/KRW 환율 데이터 부족")
    # 2. 미국 10Y 국채금리
    if not np.isnan(us10y):
        if us10y >= 4.0:
            print(f"미국 10Y {us10y:.2f}%: 글로벌 금리 고점, 위험자산 선호 약화 가능성")
        elif us10y <= 2.0:
            print(f"미국 10Y {us10y:.2f}%: 저금리, 위험자산 선호 가능성")
        else:
            print(f"미국 10Y {us10y:.2f}%: 중립적 수준")
    else:
        print("미국 10Y 국채금리 데이터 부족")
    # 3. S&P500
    if not np.isnan(sp500):
        if sp500 > 4500:
            print(f"S&P500 {sp500:.2f}: 글로벌 증시 강세 흐름")
        elif sp500 < 4000:
            print(f"S&P500 {sp500:.2f}: 글로벌 증시 약세 흐름")
        else:
            print(f"S&P500 {sp500:.2f}: 중립적 흐름")
    else:
        print("S&P500 데이터 부족") 