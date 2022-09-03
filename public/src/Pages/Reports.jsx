import React, { useEffect, useState } from 'react';
import SplitPane from '../Components/SplitPane';
import CodeEditor from '../Components/Editor';
import TreeView from '../Components/TreeView';
import { getRvtTree } from '../Services/navigation.js';

const ReportsPage = () => {
    const [rvtTree, setRvtTree] = useState([]);

    useEffect(() => {
        getRvtTree(setRvtTree);
    }, []);

    return (
        <SplitPane>
            <TreeView treeData={rvtTree}></TreeView>
            <CodeEditor language="python"></CodeEditor>
        </SplitPane>
    );
}
export default ReportsPage;