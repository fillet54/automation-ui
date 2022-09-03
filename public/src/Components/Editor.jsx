import React, { useState, useEffect, useRef } from "react";
// Codemirror is included globally

const CodeEditor = props => {
    const editorEl = useRef(null);
    const [value, setValue] = useState("");

    const codemirrorValueChanged = (doc, change) => {
        if (props.onChange && change.origin !== 'setValue') {
            props.onChange(doc.getValue(), change);
        }
        setValue(doc.getValue())
    };

    // no need to be in useEffect
    useEffect(() => {
        const codemirror = CodeMirror.fromTextArea(editorEl.current);

        // register events
        codemirror.on('change', codemirrorValueChanged);
    }, []);

    return (
        <div className="w-1/2">
            <textarea classNames="w-full h-full" ref={editorEl}></textarea>
        </div>
    );
};

export default CodeEditor;