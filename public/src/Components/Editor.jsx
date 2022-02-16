import React, { useState, useEffect } from "react";

const CodeEditor = props => {
    const [content, setContent] = useState("Hello 123");
    const [highlighted, setHighlighted] = useState(props.content);

    const handleKeyDown = evt => {
        let value = content,
            selStartPos = evt.currentTarget.selectionStart;

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

    // no need to be in useEffect
    useEffect(() => {
        if (content) {
            let tmp = content;

            /* syntax highlighting */
            const blockReg = /^([^\s]+)/
            tmp = tmp.replace(blockReg, '<span class="text-blue-500">$1</span>');
            setHighlighted(tmp);
        }
        else {
            setHighlighted('')
        }
    }, [props.language, content]);

    return (
        <div className="w-full h-full relative box-border p-0 overflow-hidden rounded-sm">
            <textarea
                className="m-0 border-0 text-black text-opacity-0 w-full h-full text-base font-mono absolute px-2 overflow-hidden bg-white bg-opacity-0"
                value={content}
                onChange={evt => setContent(evt.target.value)}
                onKeyDown={handleKeyDown}
                spellCheck={false}
                style={{ caretColor: 'black', outline: 0, minHeight: 50 }}
            />
            <pre className="pointer-events-none relative whitespace-pre-wrap w-full text-base font-mono px-2 overflow-hidden bg-gray-400"
                dangerouslySetInnerHTML={{ __html: highlighted }}>
            </pre>
        </div>
    );
};

export default CodeEditor;