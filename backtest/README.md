# 미국 주식 10년 적립식(DCA) 백테스트

`us_stock_dca_backtest.py` 는 미국 대형주 10종목에 대해 간단한 적립식 매매 전략을
10년 일봉 데이터로 백테스트합니다.

## 전략

종목별로 독립적으로 실행합니다.

1. 매 거래일 **3,000원**어치 매수.
2. 종가가 평균단가 대비 **-5%** 이하로 내려가면 **3,000원** 추가 매수.
3. 종가가 평균단가 대비 **+10%** 이상으로 올라가면 **전량 매도**(현금 실현) 후 재시작.

## 실행

```sh
pip install -r requirements.txt
python us_stock_dca_backtest.py
```

결과를 표로 출력하고 `미국주식_10년_백테스트.xlsx` 로 저장합니다
(`openpyxl` 이 없으면 CSV 로 대체 저장).

## 참고

- 데이터는 [`yfinance`](https://pypi.org/project/yfinance/) 를 통해 Yahoo Finance
  에서 조정 종가(`auto_adjust=True`)로 받아옵니다. 실행 환경에서 Yahoo Finance 로의
  아웃바운드 네트워크 접속이 필요합니다.
- 최신 `yfinance` 는 `download()` 에서 MultiIndex 컬럼을 반환하므로, 스크립트는
  컬럼을 평탄화해 `pandas>=2.2` 에서 `float(...)` TypeError 가 나지 않도록 합니다.
- **단위 주의**: 매수 금액은 '원'이지만 가격은 USD 종가입니다. `금액 / USD가격` 으로
  수량을 계산하므로 결과 금액은 환율을 반영하지 않은 명목값입니다. 실제 원화 가치를
  보려면 USD/KRW 환율을 곱해 환산하세요.
