import React, { Component } from 'react';
import { toast } from 'react-toastify'
import { Redirect } from 'react-router-dom';
import { makeApiServiceProxyRequest } from '../../../services/helpers';
import BigLoadingCentered from '../../../components/reusables/BigLoadingCentered';
import { Link } from 'react-router-dom';

class Login extends Component {
    constructor(props){
        super(props);
        this.state = { 
            password: "",
            username: "",
            redirectToMain: false,
            loading: false,
        }
    }

    handleChange = (name) => (e) => {
        this.setState({
            [name]: e.target.value
        })
    }

    onSubmit = (e) => {
        e.preventDefault();
        this.setState({loading: true});
        const body = {
            username: this.state.username,
            password: this.state.password,
        }
		makeApiServiceProxyRequest('users/login', 'post', JSON.stringify(body), 
			() => {
				this.setState({ loading: false, redirectToMain: true });
				toast.success(`You have been logged in successfully`);
			},
			() => this.setState({loading: false})
		);
    }

    render() {
        let { password, username, redirectToMain, loading } = this.state;
        let inputAlignLeftStyle = {textAlign: 'left'}
        return (
            <div className="container my-5">
                {redirectToMain && (<Redirect to={`/app`} />)}
                <div className="card">
                    <div className="card-body">
                        <h5 className="card-title">Login</h5>
                        <div style={{display: 'block', margin: '0% 20%'}}>
                            <form>
                                <div className="form-group row">
                                    <label className="text-primary col-sm-2 col-form-label" htmlFor='usernameInput'>
                                        User name
                                    </label>
                                    <div className="col-sm-10">
                                        <input 
                                            style={inputAlignLeftStyle}
                                            id='usernameInput'
                                            onChange={this.handleChange("username")}
                                            type="text"
                                            className="form-control"
                                            value={username}
                                        />
                                    </div>
                                </div>
                                <div className="form-group row">
                                    <label className="text-primary col-sm-2 col-form-label" htmlFor='passwordInput'>
                                        Password
                                    </label>
                                    <div className="col-sm-10">
                                        <input 
                                            style={inputAlignLeftStyle}
                                            id='passwordInput'
                                            onChange={this.handleChange("password")}
                                            type="password"
                                            className="form-control"
                                            value={password}
                                        />
                                    </div>
                                </div>
                                <hr></hr>
                                <div className="text-center mb-3">
                                    <button 
                                        className="btn btn-outline btn-info btn-raised"
                                        onClick={this.onSubmit}
                                        type="submit"
                                    >
                                        Log in
                                    </button>
                                </div>
                            </form>
                        </div>
                        
                        <p>Don't have an account? You can <Link to="/register">create one here</Link></p>
                    </div>
                    {loading && (
                        <BigLoadingCentered/>
                    )}
                </div>
            </div>
        )
    }
}

export default Login