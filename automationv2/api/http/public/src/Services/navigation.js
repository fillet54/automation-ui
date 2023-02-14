export const fetchRvtTree = () => {
    return fetch('/api/nav/tree/rvt')
        .then(response => response.json())
}

export const fetchRvt = (path) => {
    return fetch(`/api/nav/file?path=${path}`)
        .then(response => response.text())
}
