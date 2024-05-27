import React, { Component } from 'react';
import { faUser, faTrash, faCheckCircle, faTimesCircle } from '@fortawesome/free-solid-svg-icons'
import NavItem from '../../../../components/reusables/navbar/NavItem';
import { FontAwesomeIcon as Icon } from '@fortawesome/react-fontawesome';
import { makeApiServiceProxyRequest } from '../../../../services/helpers';
import { toast } from 'react-toastify';
import BigLoadingCentered from '../../../../components/reusables/BigLoadingCentered';
import ModalRoot from '../../../../components/ModalRoot';
import { Redirect } from 'react-router-dom';

class UserDetail extends Component {

	constructor(props) {
		super(props);
		this.state = {
			loading: false,
			userObject: null,
			oldPassword: '',
			newPassword: '',
			redirectToLogin: '',
			showDeleteModal: false,
		};
	}

	get id() {
		return this.props?.match?.params?.id
	}

	get pathname() {
		return this.props?.location?.pathname;
	}

	handleDelete = () => {
		this.setState({loading: true});
		makeApiServiceProxyRequest(`users/${this.id}`, 'delete', undefined,
			(data) => {
				if (data?.success) {
					this.setState({ redirectToLogin: true })
					toast.info(`User ${this.state.userObject.username} was deleted`);
				}
			},
			() => this.setState({loading: false})
		);
	}

	onChangePassword = (e) => {
		e.preventDefault();
		this.setState({loading: true});
		let body = {
			'old_password': this.state.oldPassword,
			'new_password': this.state.newPassword
		}
		makeApiServiceProxyRequest(`users/${this.id}/change-password`, 'put', JSON.stringify(body),
			(data) => {
				if (data?.success) {
					this.setState({ loading: false, newPassword: '', oldPassword: '' })
					toast.success(`Password was successfully changed`);
				}
			},
			() => this.setState({loading: false})
		);
	}

	handleChange = (name) => (e) => {
        this.setState({
            [name]: e.target.value
        })
    }

	showDeleteModal = (e) => {
		e.preventDefault();
		this.setState({showDeleteModal: true});
	}

	hideModal = () => {
		this.setState({ showDeleteModal: false });
	}


	componentDidMount() {
		this.loadData();
	}

	componentWillUnmount() {
		if (this.navigationComponent) {
			this.props.removeNavigation(this.navigationComponent);
		}
		this.navigationComponent = null;
	}

	loadData = () => {
		this.setState({loading: true});
		makeApiServiceProxyRequest(`users/${this.id}`, 'get', undefined, 
			(data) => {
				this.setState({ loading: false, userObject: data });
				this.navigationComponent = (
					<NavItem
						pageURI={this.pathname}
						path={`/app/users/${this.id}`}
						name="User"
						key={-1}
					>
						<Icon icon={faUser} size='sm'/> User {data.username}
					</NavItem>
				)
		
				this.props.addNavigation(this.navigationComponent);
			},
			() => this.setState({loading: false})
		);
	};


	render() {
		const { loading, userObject: data, redirectToLogin, showDeleteModal: showModal, oldPassword, newPassword } = this.state;
	
		let isMobileWidth = (window.innerWidth <= 1000);
		const modalComponent = (
			<div
				className="container text-center my-3 align-items-center"
				style={{width: isMobileWidth ? '90%' : '90%'}}
			>
				<p>Are you sure that you want to delete your account?</p>
				<div className='d-flex flex-nowrap'>
					<div className="ml-auto ml-3">
						<button onClick={this.hideModal} className="btn btn-raised mr-3" disabled={loading}>
							Cancel
						</button>
						<button onClick={this.handleDelete} className="btn btn-danger btn-raised" disabled={loading}>
							Yes, delete
						</button>
					</div>
				</div>
				{loading && (<BigLoadingCentered></BigLoadingCentered>)}
			</div>
		);

		let inputAlignLeftStyle = {textAlign: 'left'}

		return (
			<div className="container my-5">
				<ModalRoot show={showModal} hideModal={this.hideModal}>
					{showModal && modalComponent}
				</ModalRoot>
				{redirectToLogin && (<Redirect to={`/login`} />)}
				<div className="card">
					<div className="card-body">
						{loading && (<BigLoadingCentered></BigLoadingCentered>)}
						{!!data && ( <div className="row my-3" style={{display: !!data ? '' : 'none'}}>
								<div className="col-md-6 align-items-center">
									<div className='col-md-12'>
										<div className="form-group row">
											<label className="col-sm-4 col-form-label" htmlFor='usernameInput'>
												User name
											</label>
											<div className="col-sm-8">
												<input 
													style={inputAlignLeftStyle}
													id='usernameInput'
													disabled="true"
													type="text"
													className="form-control"
													value={data.username}
												/>
											</div>
										</div>
										<div className="form-group row">
											<label className="col-sm-4 col-form-label" htmlFor='emailInput'>
												E-Mail
											</label>
											<div className="col-sm-8">
												<input 
													style={inputAlignLeftStyle}
													id='emailInput'
													type="email"
													disabled="true"
													className="form-control"
													value={data.email}
												/>
											</div>
										</div>
										<div className="form-group row">
											<label className="col-sm-4 col-form-label" htmlFor='firstNameInput'>
												First name
											</label>
											<div className="col-sm-8">
												<input 
													style={inputAlignLeftStyle}
													id='firstNameInput'
													type="text"
													disabled="true"
													className="form-control"
													value={data.first_name}
												/>
											</div>
										</div>
										<div className="form-group row">
											<label className="col-sm-4 col-form-label" htmlFor='lastNameInput'>
												Last name
											</label>
											<div className="col-sm-8">
												<input 
													style={inputAlignLeftStyle}
													id='lastNameInput'
													type="text"
													disabled="true"
													className="form-control"
													value={data.last_name}
												/>
											</div>
										</div>
									</div>
								</div>
								<div className="col-md-6 align-items-center">
									<div className='col-md-12'>
										<div className="form-group row">
											<label className="col-sm-4 col-form-label" htmlFor='lastLoginInput'>
												Last login
											</label>
											<div className="col-sm-8 d-flex align-items-center">
												{new Date(data?.last_login).toLocaleDateString()}
												{' '}
												{new Date(data?.last_login).toLocaleTimeString()}
											</div>
										</div>
										<div className="form-group row">
											<label className="col-sm-4 col-form-label" htmlFor='dateJoinedInput'>
												Date joined
											</label>
											<div className="col-sm-8 d-flex align-items-center">
												{new Date(data?.date_joined).toLocaleDateString()}
												{' '}
												{new Date(data?.date_joined).toLocaleTimeString()}
											</div>
										</div>
										<div className="form-group row">
											<label className="col-sm-4 col-form-label" htmlFor='isAdminInput'>
												Is admin
											</label>
											<div className="col-sm-8 d-flex align-items-center">
												{data.is_admin ? (
													<Icon icon={faCheckCircle} color='green'/>
												) : (
													<Icon icon={faTimesCircle} color='red'/>
												)}
											</div>
										</div>
									</div>
								</div>
							</div>
						)}
						<hr></hr>
						<form>
							<div className="row my-3">
								<div className="col-md-6 align-items-center">
									<div className='col-md-12'>
										<div className="form-group row">
											<label className="col-sm-4 col-form-label" htmlFor='oldPasswordInput'>
												Old password
											</label>
											<div className="col-sm-8">
												<input 
													style={inputAlignLeftStyle}
													id='oldPasswordInput'
													type="password"
													onChange={this.handleChange("oldPassword")}
													className="form-control"
													value={oldPassword}
												/>
											</div>
										</div>
									</div>
								</div>
								<div className="col-md-6 align-items-center">
									<div className='col-md-12'>
									<div className="form-group row">
											<label className="col-sm-4 col-form-label" htmlFor='newPasswordInput'>
												New password
											</label>
											<div className="col-sm-8">
												<input 
													style={inputAlignLeftStyle}
													id='newPasswordInput'
													type="password"
													onChange={this.handleChange("newPassword")}
													className="form-control"
													value={newPassword}
												/>
											</div>
										</div>
									</div>
								</div>
								<div className="ml-5">
									<button 
										className="btn btn-outline btn-info btn-raised"
										onClick={this.onChangePassword}
										type="submit"
										disabled={loading}
									>
										Change password
									</button>
								</div>
							</div>
							
						</form>
						<hr></hr>
						<div className='d-flex flex-wrap flex-row-reverse'>
							<div className='d-flex justify-content-center'>
								<button onClick={this.showDeleteModal} className="btn btn-raised btn-danger" disabled={loading}>
									<Icon icon={faTrash} size='sm'/> Delete account
								</button>
							</div>
						</div>
					</div>
				</div>
			</div>
		);
	}
}


export default UserDetail