export const getRvtTree = (setTreeData) => {
    fetch('/api/nav/tree/rvt')
        .then(response => response.json())
        .then(data => {
            setTreeData(data);
        });
}
