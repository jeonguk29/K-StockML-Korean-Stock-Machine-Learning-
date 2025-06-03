import yfinance as yf
import pandas as pd
import numpy as np

# 1. KOSPI 과거 데이터 다운로드 (2년치)
kospi = yf.download("^KS11", period="2y")

# 2. 이동평균선 계산
kospi["MA50"] = kospi["Close"].rolling(window=50).mean()
kospi["MA200"] = kospi["Close"].rolling(window=200).mean()

# 3. 최신 값 추출
latest_close = float(kospi["Close"].iloc[-1])
latest_ma50 = float(kospi["MA50"].iloc[-1])
latest_ma200 = float(kospi["MA200"].iloc[-1])

# 4. 고점/저점, 추세 판단
market_position = "고점" if latest_close > latest_ma200 else "저점"
trend = "약세장 (데드크로스)" if latest_ma50 < latest_ma200 else "강세장 (골든크로스)"

# 5. VKOSPI는 수동 입력
latest_vkospi = 22.71  # 2024-06-03 기준 Investing.com 값

# 6. 결과 출력
print(f"[KOSPI 지수] 현재 종가: {latest_close:.2f}")
print(f"200일 이동평균선: {latest_ma200:.2f}")
print(f"→ 시장 위치: {market_position}")

print(f"\n[추세 분석] 50일 MA: {latest_ma50:.2f}, 200일 MA: {latest_ma200:.2f}")
print(f"→ 현재 시장 추세는 '{trend}'입니다.")

print(f"\n[VKOSPI] 현재 변동성 지수: {latest_vkospi:.2f}")
if latest_vkospi > 25:
    print("→ 변동성이 높아 리스크가 큽니다.")
elif latest_vkospi < 15:
    print("→ 변동성이 낮아 안정적인 장입니다.")
else:
    print("→ 변동성이 중간 수준입니다.")
