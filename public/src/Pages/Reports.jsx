import React, { useEffect, useState } from 'react';
import Split from 'react-split';
import PlainTextEditor from '../Components/Editor';
import TreeView from '../Components/TreeView';
import { fetchRvtTree } from '../Services/navigation.js';

const ReportsPage = () => {
    const [rvtTree, setRvtTree] = useState([]);
    const [selectedFile, setSelectedFile] = useState(null)

    useEffect(() => {
        fetchRvtTree()
            .then(treeData => setRvtTree(treeData));
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
            style={{ height: "calc(100vh - 48px)" }}
        >
            <TreeView treeData={rvtTree} onSelected={setSelectedFile}></TreeView>
            <PlainTextEditor language="python" file={selectedFile}></PlainTextEditor>
        </Split>
    );
}
export default ReportsPage;