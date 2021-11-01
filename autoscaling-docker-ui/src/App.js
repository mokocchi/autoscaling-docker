import { BrowserRouter, Route, Switch } from 'react-router-dom';
import AddComponent from './AddComponent';
import Restart from './Restart';
import Menu from './Menu';
import WatchConfig from './WatchConfig';

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Menu />
        <Switch>
          <Route exact path="/">
            <WatchConfig />
          </Route>
          <Route exact path="/add">
            <AddComponent />
          </Route>
          <Route exact path="/restart">
            <Restart/>
          </Route>
        </Switch>
      </BrowserRouter>
    </div>
  );
}

export default App;
