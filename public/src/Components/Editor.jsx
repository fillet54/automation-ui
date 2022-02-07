import React, { useState, useEffect } from "react";

const CodeEditor = props => {
    const [content, setContent] = useState(props.content);

    const handleKeyDown = evt => {
        let value = content,
            selStartPos = evt.currentTarget.selectionStart;

        console.log(evt.currentTarget);

        // handle 4-space indent on
        if (evt.key === "Tab") {
            value =
                value.substring(0, selStartPos) +
                "    " +
                value.substring(selStartPos, value.length);
            evt.currentTarget.selectionStart = selStartPos + 3;
            evt.currentTarget.selectionEnd = selStartPos + 4;
            evt.preventDefault();

            setContent(value);
        }
    };

    useEffect(() => {
        //Prism.highlightAll();
    }, [props.language, content]);

    return (
        <div className="code-edit-container" style={{ position: 'relative' }}>
            <textarea
                className="code-input"
                value={content}
                onChange={evt => setContent(evt.target.value)}
                onKeyDown={handleKeyDown}
                style={{ position: 'absolute' }}
            />
            <pre className="code-output" style={{ position: 'relative' }}>
                <code className={`language-${props.language}`}>{content}</code>
            </pre>
        </div>
    );
};

export default CodeEditor;