import React from 'react';
import NavBar from './Navbar'
import { Route } from 'react-router-dom';

const Layout = ({ children }) => {

    return (
        <div className="min-h-full">
            <Route exact path='/' component={NavBar} />
            <Route path="/:page" component={NavBar} />
            <main>
                <div class="h-full">
                    {children}
                </div>
            </main>
        </div>
    )
}
export default Layout