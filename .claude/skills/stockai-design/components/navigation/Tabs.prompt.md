Uppercase horizontal tab strip; active tab green + underlined.

```jsx
const [tab, setTab] = React.useState('chart');
<Tabs
  tabs={[{id:'chart',label:'Chart'},{id:'analysis',label:'AI Analysis'},
         {id:'market',label:'Market'},{id:'movers',label:'Movers'}]}
  active={tab} onChange={setTab} />
```

Accepts bare strings too (`tabs={['Intel Feed','Prices']}`) when id and label match.
