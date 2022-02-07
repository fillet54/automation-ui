import React from 'react';
import classNames from 'classnames';
import logo from '../logo.png';
import { Link, useParams } from 'react-router-dom';

const NavLink = ({ children, page }) => {
    const { page: currentPage = 'dashboard' } = useParams();
    const isCurrent = page === currentPage;

    const style = classNames(
        'text-white', 'px-3', 'py-2', 'rounded-md', 'text-sm', 'font-medium',
        {
            'bg-ngc-blue-700': isCurrent,
            'bg-ngc-blue-500': !isCurrent,
            'hover:bg-ngc-blue-700': !isCurrent,
            'hover:bg-opacity-75': !isCurrent
        });
    return (
        <Link to={`/${page}`} className={style}>{children}</Link>
    )
}
const NavBar = () => {
    return (
        <nav className="bg-ngc-blue-500">
            <div className="w-full px-2">
                <div className="flex items-center justify-between h-12">
                    <div className="flex items-center">
                        <div className="flex-shrink-0">
                            <img className="h-8" src={logo} alt="Workflow" />
                        </div>
                        <div className="hidden md:block">
                            <div className="ml-6 flex items-baseline space-x-4">
                                <NavLink page="dashboard">Dashboard</NavLink>
                                <NavLink page="team">Team</NavLink>
                                <NavLink page="projects">Projects</NavLink>
                                <NavLink page="calendar">Calendar</NavLink>
                                <NavLink page="reports">Reports</NavLink>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    );
};
export default NavBar