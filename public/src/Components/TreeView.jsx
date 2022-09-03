import React, { useState } from "react";
import classNames from "classnames";

const getRoots = (data) => {
    return Object.values(data).filter(node => node.isRoot === true)
}

const getChildNodes = (node, data) => {
    if (!node.children) return [];
    return node.children.map(path => data[`${node.path}/${path}`])
}

const getNodeLabel = (node) => {
    const parts = node.path.split('/');
    return parts[parts.length - 1];
}

const TreeNode = ({ node, treeData, selectedNode, setSelectedNode, level }) => {
    const [isOpen, setOpen] = useState(false)
    const toggleOpenClose = () => {
        if (node.type === 'folder')
            setOpen(!isOpen);
        setSelectedNode(node)
    }

    console.log(selectedNode)

    const chevron = (
        <i className={classNames('fa', 'fa-fw', { 'fa-chevron-down': isOpen, 'fa-chevron-right': !isOpen })} />);

    const children = getChildNodes(node, treeData).sort((a, b) => {
        if (a.type === 'folder' && b.type === 'folder')
            return a.path.localeCompare(b.path);
        else if (a.type === 'folder')
            return -1;
        else
            return 1;
    });

    return (
        <div className={classNames({ 'pl-5': !node.isRoot })}>
            <div onClick={toggleOpenClose}
                className={classNames({ 'bg-blue-200': node === selectedNode }, 'text-xs', 'whitespace-nowrap')}>
                {node.type === 'folder' && chevron}
                {node.type === 'file' && <i className="fa fa-fw fa-file-o" />}
                {node.type === 'folder2' && isOpen === true && <i className="fa fa-fw fa-folder-open" />}
                {node.type === 'folder2' && !isOpen && <i className="fa fa-fw fa-folder" />}
                {getNodeLabel(node)}
            </div>
            <div>
                {isOpen && children.map((childNode) => {
                    return (<TreeNode
                        key={childNode.path}
                        node={childNode}
                        treeData={treeData}
                        selectedNode={selectedNode}
                        setSelectedNode={setSelectedNode} />)

                })}
            </div>
        </div>)
};


const TreeView = ({ treeData }) => {
    const [selectedNode, setSelectedNode] = useState(null)
    const roots = getRoots(treeData);

    return (
        <div>
            {
                roots.map(node => (
                    <TreeNode
                        key={node.path}
                        node={node}
                        treeData={treeData}
                        selectedNode={selectedNode}
                        setSelectedNode={setSelectedNode}
                    />))
            }
        </div>
    );
};

export default TreeView