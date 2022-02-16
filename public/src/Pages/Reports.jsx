import React from 'react';
import SplitPane from '../Components/SplitPane';
import CodeEditor from '../Components/Editor';

const ReportsPage = () => {
    return (
        <SplitPane>
            <h1>Reports</h1>
            <div style={{ width: 500, minHeight: 75 }}>
                <CodeEditor language="python"></CodeEditor>
            </div>
        </SplitPane>
    );
}
export default ReportsPage;