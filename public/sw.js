const { exportsMap } = JSON.parse((decodeURIComponent(self.location.search) || '?{}').substr(1));

// TODO: Update to latest babel standalone. Using this version as its the 
// version I have available
importScripts('/js/babel/babel.min.js');

//this is needed to activate the worker immediately without reload
//@see https://developers.google.com/web/fundamentals/primers/service-workers/lifecycle#clientsclaim
self.addEventListener('activate', event => event.waitUntil(clients.claim()));

// Returns the export map for a particular URL
const getExportMapByUrl = (url) => Object.keys(exportsMap).reduce((res, key) => {
    if (res) return res;
    if (matchUrl(url, key)) return exportsMap[key];
    return res;
}, null);


// Returns a list of export statements for a URL
const getExportsForUrl = (url) => {
    const { defaultName, exports } = getExportMapByUrl(url);
    const defaultExport = `export default window.${defaultName};\n`
    const others = exports.map(e => `export let ${e} = window.${defaultName}.${e};`).join("\n")
    return defaultExport + others;

}

const matchUrl = (url, key) => url.includes(`/${key}/`);

const removeSpaces = str => str.split(/^ +/m).join('').trim();

function base64Encode(buf) {
    let string = '';
    (new Uint8Array(buf)).forEach(
        (byte) => { string += String.fromCharCode(byte) }
    )
    return btoa(string)
}


const headers = new Headers({
    'Content-Type': 'application/javascript'
});

self.addEventListener('fetch', (event) => {

    let { request: { url } } = event;
    console.log(url)

    const fileName = url.split('/').pop();
    const ext = fileName.includes('.') ? url.split('.').pop() : '';

    if (!ext && !url.endsWith('/') && new URL(url).pathname.startsWith('/src/')) {
        url = url + '.' + 'jsx';
    }

    console.log('Req', url, ext);

    if (exportsMap && Object.keys(exportsMap).some(key => matchUrl(url, key))) {
        event.respondWith(
            fetch(url)
                .then(response => response.text())
                .then(body => {
                    console.log('JS', url);
                    return body;
                })
                .then(body => new Response(removeSpaces(`
                        const head = document.getElementsByTagName('head')[0];
                        const script = document.createElement('script');
                        script.setAttribute('type', 'text/javascript');
                        script.appendChild(document.createTextNode(${JSON.stringify(body)}));
                        head.appendChild(script);
                        ${getExportsForUrl(url)}
                    `), { headers }
                ))
        )
    } else if (url.endsWith('.svg') || url.endsWith('.jpg') || url.endsWith('jpeg') || url.endsWith('png')) {
        event.respondWith(
            fetch(url)
                .then(response => response.arrayBuffer())
                .then(arrayBuffer => {
                    const data = base64Encode(arrayBuffer)
                    const contentType = {
                        svg: 'image/svg+xml',
                        jpg: 'image/jpg',
                        jpeg: 'image/jpeg',
                        png: 'image/png'
                    }[url.split('.').pop().trim()];


                    return (new Response(removeSpaces(`
                            const dataUrl = "data:${contentType};base64,${data}";
                            export default dataUrl; //TODO here we can export CSS module instead
                        `),
                        { headers })
                    )
                })
        )
    } else if (url.endsWith('.css') && !(new URL(url).pathname.startsWith('/css'))) {
        event.respondWith(
            fetch(url)
                .then(response => response.text())
                .then(body => new Response(removeSpaces(`
                        //TODO We don't track instances, so 2x imports will result in 2x style tags
                        const head = document.getElementsByTagName('head')[0];
                        const style = document.createElement('style');
                        style.setAttribute('type', 'text/css');
                        style.appendChild(document.createTextNode(${JSON.stringify(body)}));
                        head.appendChild(style);
                        export default null; //TODO here we can export CSS module instead
                    `),
                    { headers }
                ))
        )
    } else if (url.endsWith('.jsx')) {
        event.respondWith(
            fetch(url)
                .then(response => response.text())
                .then(body => new Response(
                    //TODO Cache
                    //
                    Babel.transform(body, {
                        presets: [
                            'react',
                        ],
                        plugins: [
                            'transform-es2015-destructuring',
                            'syntax-object-rest-spread'
                        ],
                        sourceMaps: true
                    }).code,
                    { headers }
                ))
        )
    } else if (url.endsWith('.js')) { // rewrite for import('./Panel') with no extension
        event.respondWith(
            fetch(url)
                .then(response => response.text())
                .then(body => new Response(body, { headers }))
        )
    }

});
