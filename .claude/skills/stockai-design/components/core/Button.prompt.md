Dense monospace button with green-primary / ghost-secondary / buy-sell variants — use for every action in the terminal UI.

```jsx
<Button variant="primary" full>▶ Run AI Analysis</Button>
<Button variant="secondary" size="sm">⚡ Refresh Intel</Button>
<Button variant="buy" size="sm">Buy 12 sh</Button>
<Button variant="sell" size="sm">Close</Button>
<Button variant="primary" disabled full>Submitting…</Button>
```

Variants: `primary` (green, black text — the loud action), `secondary` (ghost outline, brightens to green on hover), `buy` (green), `sell` (red). Sizes: `md` (block), `inline` (toolbar Go button), `sm` (compact). Pass `full` to stretch.
