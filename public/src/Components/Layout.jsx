import React from 'react';
import NavBar from './Navbar'
import { Route } from 'react-router-dom';

const Layout = ({ children }) => {

    return (
        <div className="min-h-screen flex flex-col">
            <Route exact path='/' component={NavBar} />
            <Route path="/:page" component={NavBar} />
            <main className="flex w-full flex-grow">
                {children}
            </main>
        </div>
    )
}
export default Layout