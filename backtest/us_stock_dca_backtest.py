"""미국 주식 10년 적립식(DCA) 백테스트.

전략 (종목별 독립 실행):
  1. 매 거래일 daily_buy_krw 만큼 매수.
  2. 종가가 평균단가 대비 -5% 이하로 내려가면 extra_buy_krw 만큼 추가 매수.
  3. 종가가 평균단가 대비 +10% 이상으로 올라가면 전량 매도(현금 실현) 후 재시작.

주의(단위):
  daily_buy_krw / extra_buy_krw 는 '원' 단위이지만 가격은 USD 종가입니다.
  즉 `금액 / USD가격` 으로 수량을 계산하므로 결과 금액은 환율을 반영하지 않은
  명목 단위입니다(원본 스크립트 동작을 그대로 유지). 실제 원화 가치를 보려면
  USD/KRW 환율을 곱해 환산하세요.

실행:
  pip install yfinance pandas openpyxl
  python us_stock_dca_backtest.py
"""

import sys

import pandas as pd
import yfinance as yf

tickers = {
    "메타": "META",
    "아마존": "AMZN",
    "코카콜라": "KO",
    "존슨앤드존슨": "JNJ",
    "P&G": "PG",
    "알파벳A": "GOOGL",
    "엔비디아": "NVDA",
    "테슬라": "TSLA",
    "마이크로소프트": "MSFT",
    "AMD": "AMD",
}

daily_buy_krw = 3000
extra_buy_krw = 3000
years = 10


def get_close_series(ticker: str) -> pd.Series:
    """단일 종목의 조정 종가 시계열을 반환. 실패 시 빈 Series."""
    data = yf.download(
        ticker,
        period=f"{years}y",
        interval="1d",
        auto_adjust=True,
        progress=False,
    )

    if data is None or data.empty:
        return pd.Series(dtype="float64")

    # 최신 yfinance 는 MultiIndex 컬럼(('Close', 'META'))을 반환한다.
    # 이 경우 row["Close"] 가 스칼라가 아닌 1개짜리 Series 가 되어
    # float(...) 이 pandas>=2.2 에서 TypeError 를 낸다. 컬럼을 평탄화한다.
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    if "Close" not in data.columns:
        return pd.Series(dtype="float64")

    return data["Close"].dropna()


def backtest_one(name: str, ticker: str) -> dict | None:
    close = get_close_series(ticker)
    if close.empty:
        print(f"{name}({ticker}) 데이터 없음", file=sys.stderr)
        return None

    shares = 0.0
    invested = 0.0
    realized_cash = 0.0
    total_buy_count = 0
    total_sell_count = 0

    for price in close.astype(float):
        # 1) 매일 정액 매수
        shares += daily_buy_krw / price
        invested += daily_buy_krw
        total_buy_count += 1

        # 2) 평균단가 대비 -5% 하락 시 추가 매수
        avg_price = invested / shares if shares > 0 else 0.0
        if price <= avg_price * 0.95:
            shares += extra_buy_krw / price
            invested += extra_buy_krw
            total_buy_count += 1

        # 3) 평균단가 대비 +10% 상승 시 전량 매도
        avg_price = invested / shares if shares > 0 else 0.0
        if shares > 0 and price >= avg_price * 1.10:
            realized_cash += shares * price
            shares = 0.0
            invested = 0.0
            total_sell_count += 1

    last_price = float(close.iloc[-1])
    holding_value = shares * last_price
    total_value = realized_cash + holding_value

    return {
        "종목": name,
        "티커": ticker,
        "매수횟수": total_buy_count,
        "매도횟수": total_sell_count,
        "현재보유주식수": round(shares, 6),
        "실현현금": round(realized_cash, 0),
        "현재보유평가액": round(holding_value, 0),
        "현재총가치": round(total_value, 0),
    }


def main() -> None:
    results = [r for name, ticker in tickers.items()
               if (r := backtest_one(name, ticker)) is not None]

    if not results:
        print("가져온 데이터가 없습니다. 네트워크/티커를 확인하세요.", file=sys.stderr)
        sys.exit(1)

    df = pd.DataFrame(results)

    print(df.to_string(index=False))
    print()
    print("총 현재가치:", round(df["현재총가치"].sum(), 0), "원(명목)")

    out_xlsx = "미국주식_10년_백테스트.xlsx"
    try:
        df.to_excel(out_xlsx, index=False)
        print(f"엑셀 저장 완료: {out_xlsx}")
    except ModuleNotFoundError:
        # openpyxl 미설치 시 CSV 로 대체 저장
        out_csv = "미국주식_10년_백테스트.csv"
        df.to_csv(out_csv, index=False, encoding="utf-8-sig")
        print(f"openpyxl 미설치 → CSV 로 저장: {out_csv}")


if __name__ == "__main__":
    main()
