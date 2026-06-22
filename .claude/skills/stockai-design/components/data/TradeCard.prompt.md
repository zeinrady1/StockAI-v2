The AI recommendation card from the Analysis tab. Left accent + tag keyed to action; confidence, signal chips, rationale, execute button.

```jsx
<TradeCard ticker="NVDA" action="buy" confidence={8}
  price="$118.40 · entry $116 · target $134"
  signals={['RSI 41','MACD cross','Insider buy','Rev +62% YoY']}
  rationale="Pullback to 50DMA with bullish insider flow and accelerating data-center revenue."
  onExecute={() => {}} />
<TradeCard ticker="SObI" action="hold" confidence={5}
  signals={['Range-bound','Earnings 7d']}
  rationale="Wait for the print before sizing in." />
```
