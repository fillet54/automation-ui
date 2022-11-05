import React, { useEffect, useState } from 'react';
import Split from 'react-split';
import PlainTextEditor from '../Components/Editor';
import TreeView from '../Components/TreeView';
import { getRvtTree } from '../Services/navigation.js';

const ReportsPage = () => {
    const [rvtTree, setRvtTree] = useState([]);

    useEffect(() => {
        getRvtTree(setRvtTree);
    }, []);

    return (
        <Split
            sizes={[25, 75]}
            minSize={100}
            expandToMin={false}
            gutterSize={10}
            gutterAlign="center"
            snapOffset={30}
            dragInterval={1}
            direction="horizontal"
            cursor="col-resize"
            className="split flex-grow"
        >
            <TreeView treeData={rvtTree}></TreeView>
            <PlainTextEditor language="python"></PlainTextEditor>
        </Split>
    );
}
export default ReportsPage;