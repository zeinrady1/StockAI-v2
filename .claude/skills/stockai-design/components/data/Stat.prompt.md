Inset well showing a micro-label over a bold value — the portfolio/account readout primitive. Tile in a 2-col grid.

```jsx
<div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'4px'}}>
  <Stat label="Total Value" value="$104,238" tone="green" />
  <Stat label="Cash" value="$22,910" />
  <Stat label="Today P/L" value="+$1,204" tone="green" />
  <Stat label="Buying Power" value="$45,820" />
</div>
```
