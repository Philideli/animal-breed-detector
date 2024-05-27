import React, { Component } from 'react';
import { BrowserRouter as Router, Route, Switch, Redirect } from 'react-router-dom'
import MainRouter from './views/MainRouter'
import ToastRoot from './components/ToastRoot'
import Login from './views/components/Login';
import Register from './views/components/Register';

/**
 * The main component, that gets rendered by the DOM.
 * At the same time it is the main router for the whole app.
 *
 * @component
 * @memberOf components
 */
class App extends Component {
    render() {
        return (
            <div>
                <Router>
                    <ToastRoot />
                    <Switch>
                        <Route
                            path="/login"
                            component={Login}
                        />
                        <Route
                            path="/register"
                            component={Register}
                        />
                        <Route
                            path="/app"
                            component={MainRouter}
                        />
                        <Redirect from="*" to="/login"/>
                    </Switch>
                </Router>
            </div>
        );
    }
}

export default App;