import React from 'react';
import ReactDOM from 'react-dom';
import "./App.css"
import {
  BrowserRouter as Router,
  Switch,
  Route,
} from "react-router-dom";
import Layout from './Components/Layout'
import IndexPage from './Pages/Index';
import ReportsPage from './Pages/Reports';
import QueuePage from './Pages/Queue';

ReactDOM.render(
  <React.StrictMode>
    <Router>
      <Layout>
        <Switch>
          <Route exact path='/' component={IndexPage} />
          <Route exact path='/dashboard' component={IndexPage} />
          <Route exact path='/reports' component={ReportsPage} />
          <Route exact path='/queue' component={QueuePage} />
        </Switch>
      </Layout>
    </Router>
  </React.StrictMode>,
  document.getElementById('root')
);

