import React, { Component } from 'react';
import Settings from '../../../components/Settings'
import { FontAwesomeIcon as Icon } from '@fortawesome/react-fontawesome'
import { faCog, faPaw, faPlay, faHistory, faUser, faSignOutAlt } from '@fortawesome/free-solid-svg-icons'
import NavItem from "../../../../components/reusables/navbar/NavItem";
import ModalRoot from '../../../../components/ModalRoot/ModalRoot';
import Dropdown from 'react-bootstrap/Dropdown';
import './MainMenu.css';
import { Link } from 'react-router-dom';
import { Redirect } from 'react-router-dom/cjs/react-router-dom.min';
import { makeApiServiceProxyRequest } from '../../../../services/helpers';
import { toast } from 'react-toastify';
import SmallLoading from '../../../../components/reusables/SmallLoading';

const CustomToggle = React.forwardRef(({ children, onClick }, ref) => (
	<a
		className='nav-link nav-item p-0'
	  	href={() => false}
	  	ref={ref}
	  	onClick={(e) => {
			e.preventDefault();
			onClick(e);
	  	}}
	>
	  	{children}
	</a>
  ));

class MainMenu extends Component {
	constructor(props){
		super(props);
		this.state = {
			display: false,
			settingsIconInFocus: false,
			showSettings: false,
			showBrandSeparator: true,
			hoveredBrand: true,
			redirectToLogin: false,
			loading: false,
			authenticatedUserId: null,
			authenticatedUserName: null,
		}
	}

	componentDidMount() {
		this.setState({loading: true});
		makeApiServiceProxyRequest(`users/authenticated-user-id`, 'get', undefined, 
			(data) => {
				this.setState({ authenticatedUserId: data.id });
				makeApiServiceProxyRequest(`users/${data.id}`, 'get', undefined, 
					(userData) => {
						this.setState({ loading: false, authenticatedUserName: userData.username });
					},
					() => this.setState({loading: false})
				);
			},
			() => this.setState({loading: false})
		);
	}

	toggleSettingsHover = (e) => {
		e.preventDefault();
		this.setState({settingsIconInFocus: !this.state.settingsIconInFocus});
	}

	showSettingsModal = () => {
		this.setState({showSettings: true});
	}

	hideSettingsModal = () => {
		this.setState({showSettings: false});
	}

	toggleNavbar = (e) => {
		e.preventDefault();
		this.setState({display: !this.state.display, showBrandSeparator: !this.state.showBrandSeparator});
	}

	onLogout = (e) => {
		e.preventDefault();
		this.setState({loading: true});
		makeApiServiceProxyRequest('users/logout', 'post', undefined, 
			() => {
				this.setState({ redirectToLogin: true, loading: false });
				toast.success(`Logout successful`);
			}
		);
	}
			
	render() {
		let { pathname } = this.props.location;
		let { display, showSettings, showBrandSeparator, redirectToLogin, loading, authenticatedUserId, authenticatedUserName } = this.state;

		if (redirectToLogin) {
			return (
				<Redirect to="/login"/>
			);
		}

		return (
			<nav className="navbar navbar-expand-lg navbar-light sticky-top" style={{backgroundColor: 'lightblue'}}>
				<ModalRoot show={showSettings} hideModal={this.hideSettingsModal}>
					{showSettings && (
						<Settings hideModal={this.hideSettingsModal}/>
					)}
				</ModalRoot>
				<button
					className="navbar-toggler"
					type="button"
					onClick={this.toggleNavbar}
				>
					<span className="navbar-toggler-icon" />
				</button>
				<div className={(display ? '' : 'collapse ') + "navbar-collapse"}>
					<NavItem 
						pageURI={pathname}
						path={pathname}
						brand
					>
						<div className='shake-on-hover'>
							{(loading ? (<SmallLoading/>) : (<Icon icon={faPaw}/>))} Animal breed detector
						</div>
					</NavItem>
					{showBrandSeparator && (
						<div style={{'borderLeft': '1px solid gray', 'height': '40px'}}></div>
					)}
					<ul className="navbar-nav mr-auto ml-3">
						<NavItem
							pageURI={pathname}
							path="/app/run"
							name="Run new detection"
							key={-2}
						>
							<Icon icon={faPlay} size='sm'/> Run new detection
						</NavItem>
						<NavItem
							pageURI={pathname}
							path="/app/overview"
							name="History"
							key={-1}
						>
							<Icon icon={faHistory} size='sm'/> History
						</NavItem>
						{this.props.children}
					</ul>
					<ul className="navbar-nav">
						<NavItem
							pageURI={pathname}
							name="Settings"
							onClick={this.showSettingsModal}
							key={0}
						>
							<Icon icon={faCog} size='sm'/> Settings 
						</NavItem>
						{authenticatedUserId && authenticatedUserName && (
							<NavItem
								pageURI={pathname}
								name="User"
								key={1}
								onClick={(e) => e.preventDefault()}
							>
								<Dropdown size='sm'>
									<Dropdown.Toggle as={CustomToggle}>
										<Icon icon={faUser} size='sm'/> <span style={{ all: 'unset' }}>{authenticatedUserName}</span>
									</Dropdown.Toggle>
									<Dropdown.Menu>
										<Link className="dropdown-item d-flex flex-nowrap" to={`/app/users/${authenticatedUserId}`}>
											<Icon icon={faUser} size='sm'/> <span className='mx-1'>Profile</span> 
										</Link>
										<Dropdown.Item className='d-flex flex-nowrap' onClick={this.onLogout}>
											<Icon icon={faSignOutAlt} size='sm'/> <span className='mx-1'>Log out</span> 
										</Dropdown.Item>
									</Dropdown.Menu>
								</Dropdown>
							</NavItem>
						)}
						{(!authenticatedUserId || !authenticatedUserName) && loading && (
							<NavItem
								pageURI={pathname}
								name="User"
								key={1}
							>
								<SmallLoading/>
							</NavItem>
						)}
					</ul>
				</div>
			</nav>
		);
	}
}

export default MainMenu