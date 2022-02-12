import React, { useState, useEffect } from "react";

const CodeEditor = props => {
    const [content, setContent] = useState(props.content);
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
        <div className="overflow-auto" style={{ maxHeight: 400 }}>
            <div className="relative" style={{ width: 400 }}>
                <textarea
                    className="text-black text-opacity-0 w-full text-base font-mono absolute bg-gray-100 px-2 overflow-hidden"
                    value={content}
                    onChange={evt => setContent(evt.target.value)}
                    onKeyDown={handleKeyDown}
                    spellCheck={false}
                    style={{ caretColor: 'black', outline: 0 }}
                />
                <pre className="pointer-events-none relative whitespace-pre-wrap w-full text-base font-mono px-2 overflow-hidden"
                    dangerouslySetInnerHTML={{ __html: highlighted }}>
                </pre>
            </div>
        </div>
    );
};

export default CodeEditor;