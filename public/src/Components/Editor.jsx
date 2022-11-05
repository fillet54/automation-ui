import React, { useState, useEffect, useRef, useMemo } from "react";
import debounce from "lodash.debounce";


import { useResizeObserver } from "./Hooks";
// Codemirror is included globally

const PlainTextEditor = (props) => {
    const [wrapperRef, { contentRect }] = useResizeObserver()
    const editorEl = useRef(null)
    const [editor, setEditor] = useState(null)
    const [value, setValue] = useState("")
    const debouncedEditorRefresh = useMemo(() => {
        return editor && debounce(() => {
            console.log("DEBOUNCE")
            editor.refresh()
        }, 500)
    }, [editor])

    const wrapperHeight = contentRect && contentRect['height']

    const codemirrorValueChanged = (doc, change) => {
        if (props.onChange && change.origin !== 'setValue') {
            props.onChange(doc.getValue(), change);
        }
        setValue(doc.getValue())
    };

    useEffect(() => {
        const codemirror = CodeMirror.fromTextArea(editorEl.current);

        // register events
        codemirror.on('change', codemirrorValueChanged);
        setEditor(codemirror);

        // cancel any pending debouncing
        return () => debouncedEditorRefresh && debouncedEditorRefresh.cancel()
    }, []);

    useEffect(() => {
        if (editor) {
            editor.setSize('auto', wrapperHeight)
            debouncedEditorRefresh();
        }
    }, [editor, wrapperHeight])

    return (
        <div className="w-1/2" style={{ height: "calc(100vh - 49px)" }} ref={wrapperRef} >
            <textarea classNames="w-full h-full" ref={editorEl}></textarea>
        </div>
    );
};

export default PlainTextEditor;