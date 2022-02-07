import React from 'react';
import SplitPane from '../Components/SplitPane';
import CodeEditor from '../Components/Editor';

const ReportsPage = () => {
    return (
        <SplitPane>
            <h1>Reports</h1>
            <CodeEditor language="python"></CodeEditor>
        </SplitPane>
    );
}
export default ReportsPage;