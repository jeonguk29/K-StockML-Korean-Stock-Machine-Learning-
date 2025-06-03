import pandas as pd
import numpy as np
import requests

def get_base_rate():
    try:
        url = 'https://ecos.bok.or.kr/api/StatisticSearch/sample/json/kr/1/5/722Y001/M/202301/202312/0101000'
        r = requests.get(url)
        data = r.json()
        rows = data['StatisticSearch']['row']
        latest = float(rows[-1]['DATA_VALUE'])
        return latest
    except:
        return 3.5

def get_m2_growth():
    try:
        url = 'https://ecos.bok.or.kr/api/StatisticSearch/sample/json/kr/1/5/322Y001/M/202301/202312/0101000'
        r = requests.get(url)
        data = r.json()
        rows = data['StatisticSearch']['row']
        latest = float(rows[-1]['DATA_VALUE'])
        return latest
    except:
        return 7.1  # 최신값 수동입력(예시)

if __name__ == "__main__":
    # 국고채 3년/10년 금리: 2025년 4월 기준 수동 입력
    bond3y = 2.40
    bond10y = 2.66
    base_rate = get_base_rate()
    m2_growth = get_m2_growth()
    table = pd.DataFrame({
        '지표': ['국고채 3년', '국고채 10년', '기준금리', 'M2 증가율'],
        '값': [bond3y, bond10y, base_rate, m2_growth]
    })
    print("[금리 및 유동성 지표]")
    print(table.to_string(index=False))
    print("\n[판단]")
    if not np.isnan(bond3y) and not np.isnan(bond10y):
        if bond3y > bond10y:
            print("⚠️ 장단기 금리 역전: 경기침체 신호 가능성")
        else:
            print("✅ 장단기 금리 정상: 경기 정상 흐름")
    else:
        print("국고채 금리 데이터 부족 (수동 입력값도 없음)")
    if not np.isnan(base_rate):
        if base_rate >= 3.0:
            print(f"기준금리 {base_rate:.2f}%: 금리 인상기 또는 고금리 국면")
        elif base_rate <= 1.5:
            print(f"기준금리 {base_rate:.2f}%: 금리 인하기 또는 저금리 국면")
        else:
            print(f"기준금리 {base_rate:.2f}%: 중립적 수준")
    else:
        print("기준금리 데이터 부족")
    if not np.isnan(m2_growth):
        if m2_growth >= 8:
            print(f"M2 증가율 {m2_growth:.2f}%: 유동성 풍부")
        elif m2_growth <= 5:
            print(f"M2 증가율 {m2_growth:.2f}%: 유동성 경색 우려")
        else:
            print(f"M2 증가율 {m2_growth:.2f}%: 유동성 중간")
    else:
        print("M2 증가율 데이터 부족") 