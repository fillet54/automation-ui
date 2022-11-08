import React, { useState, useEffect, useRef, useMemo } from "react";
import debounce from "lodash.debounce";
import { fetchRvt } from "../Services/navigation.js";

import { useResizeObserver } from "./Hooks";
// Codemirror is included globally

const htmlToElement = (htmlStr) => {
    var template = document.createElement('template')
    template.innerHTML = htmlStr.trim()
    return template.content.firstChild
}

// returns requirement id(s) to line mappings
const findRequirements = (text) => {
    const lines = text.split(/\r?\n/)
    var reqsOnLines = []
    for (var i = 0; i < lines.length; ++i) {
        const reqs = lines[i].match(/(\$[^\s]+)/g)
        if (reqs) {
            reqsOnLines.push([reqs, i])
        }
    }
    return reqsOnLines
}

const updateRequirements = (editor, widgets) => {
    // Remove previous widgets
    for (var i = 0; i < widgets.length; ++i)
        editor.removeLineWidget(widgets[i])

    var newWidgets = []
    const reqsOnLines = findRequirements(editor.getDoc().getValue())

    for (var i = 0; i < reqsOnLines.length; ++i) {
        const [reqs, line] = reqsOnLines[i]
        reqs.forEach((req) => {
            const reqElement = htmlToElement(`
            <div class="bg-yellow-50 border" >
                <span class="inline-flex justify-center items-center mr-2 w-4 h-4 text-xs bg-red-500 text-red-200 font-semibold rounded-full">!!</span>
                Requirement found: ${req}
            </div>`)
            newWidgets.push(editor.addLineWidget(line, reqElement, { coverGutter: false, noHScroll: true }));
        })
    }
    return newWidgets
}

const guessMode = (file) => {
    const ext = file.path.split('.').pop()
    return {
        py: 'python',
        js: 'javascript',
        json: 'javascript',
        ipynb: 'javascript',
    }[ext] || ''
}

const useDebounce = (func, wait, deps) => {
    return useMemo(() => debounce(func, wait), deps)
}

const useCodeMirror = (options) => {
    const editorEl = useRef(null)
    const [editor, setEditor] = useState(null)

    useEffect(() => {
        const codemirror = CodeMirror.fromTextArea(editorEl.current, options);
        setEditor(codemirror)
    }, []);

    return [editorEl, editor]
}

const PlainTextEditor = ({ file, ...props }) => {
    const [wrapperRef, { contentRect }] = useResizeObserver()
    const [editorEl, editor] = useCodeMirror({ lineNumbers: true })
    const [value, setValue] = useState("")
    const [widgets, setWidgets] = useState([])
    const wrapperHeight = contentRect && contentRect['height']

    // debounced methods
    const debouncedEditorRefresh = useDebounce(() => editor.refresh(), 500, [editor])
    const debouncedAddRequirement = useDebounce(() => {
        setWidgets(updateRequirements(editor, widgets))
    }, 500, [editor, widgets])

    const onValueChanged = (doc, change) => {
        if (props.onChange && change.origin !== 'setValue') {
            props.onChange(doc.getValue(), change)
        }
        setValue(doc.getValue())
    }

    useEffect(() => {
        if (!editor) return

        editor.on('change', onValueChanged);
    }, [editor]);

    // Fetch file contents
    useEffect(() => {
        if (!editor || !file) return
        if (file.type !== 'folder') {
            fetchRvt(file.path)
                .then((text) => {
                    setValue(text)
                    editor.setValue(text)
                    editor.setOption('mode', guessMode(file))
                })
        }
    }, [editor, file])

    // Set editor size based on wrapper height
    // width can be auto
    useEffect(() => {
        if (!editor) return

        editor.setSize('auto', wrapperHeight)
        debouncedEditorRefresh();
    }, [wrapperHeight])

    // Update any widgets when content changes
    useEffect(() => {
        if (!editor) return
        debouncedAddRequirement()
    }, [value])


    return (
        <div ref={wrapperRef} >
            <textarea classNames="w-full h-full" ref={editorEl}></textarea>
        </div>
    );
};

export default PlainTextEditor;