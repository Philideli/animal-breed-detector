import React, { Component } from 'react';
import { toast } from 'react-toastify'
import { Redirect } from 'react-router-dom';
import { makeApiServiceProxyRequest, } from '../../../services/helpers';
import BigLoadingCentered from '../../../components/reusables/BigLoadingCentered';
import { Link } from 'react-router-dom';

class Register extends Component {
    constructor(props){
        super(props);
        this.state = { 
            password: "",
            username: "",
            firstName: "",
            lastName: "",
            redirectToLogin: false,
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
            email: this.state.email,
            first_name: this.state.firstName,
            last_name: this.state.lastName,
        }
		makeApiServiceProxyRequest('users/register', 'post', JSON.stringify(body), 
			() => {
				this.setState({ loading: false, redirectToLogin: true });
				toast.success(`Your account has been created succesfully, you can log in now`);
			},
			() => this.setState({loading: false})
		);
    }

    render() {
        let { password, username, redirectToLogin, loading, firstName, lastName, email } = this.state;
        let inputAlignLeftStyle = {textAlign: 'left'}
        return (
            <div className="container my-5">
                {redirectToLogin && (<Redirect to={`/login`} />)}
                <div className="card">
                    <div className="card-body">
                        <h5 className="card-title">Create an account</h5>
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
                                    <label className="text-primary col-sm-2 col-form-label" htmlFor='emailInput'>
                                        E-Mail
                                    </label>
                                    <div className="col-sm-10">
                                        <input 
                                            style={inputAlignLeftStyle}
                                            id='emailInput'
                                            onChange={this.handleChange("email")}
                                            type="email"
                                            className="form-control"
                                            value={email}
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
                                <div className="form-group row">
                                    <label className="text-secondary col-sm-2 col-form-label" htmlFor='firstNameInput'>
                                        First name (optional)
                                    </label>
                                    <div className="col-sm-10">
                                        <input 
                                            style={inputAlignLeftStyle}
                                            id='firstNameInput'
                                            onChange={this.handleChange("firstName")}
                                            type="text"
                                            className="form-control"
                                            value={firstName}
                                        />
                                    </div>
                                </div>
                                <div className="form-group row">
                                    <label className="text-secondary col-sm-2 col-form-label" htmlFor='lastNameInput'>
                                        Last name (optional)
                                    </label>
                                    <div className="col-sm-10">
                                        <input 
                                            style={inputAlignLeftStyle}
                                            id='lastNameInput'
                                            onChange={this.handleChange("lastName")}
                                            type="text"
                                            className="form-control"
                                            value={lastName}
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
                                        Register
                                    </button>
                                </div>
                            </form>
                        </div>
                        
                        <p>Already have an account? You can <Link to="/login">log in here</Link></p>
                    </div>
                    {loading && (
                        <BigLoadingCentered/>
                    )}
                </div>
            </div>
        )
    }
}

export default Register