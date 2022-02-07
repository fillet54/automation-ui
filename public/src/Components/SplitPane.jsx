import React, { useState, useEffect, useRef } from 'react';

function unFocus(document, window) {
  if (document.selection) {
    document.selection.empty();
  } else {
    try {
      window.getSelection().removeAllRanges();
      // eslint-disable-next-line no-empty
    } catch (e) { }
  }
}

const Pane = React.forwardRef(({ size, children }, ref) => {
  const style = {
    width: size
  };

  return (
    <div ref={ref} style={style}>
      {children}
    </div>
  );
});

const Resizer = ({ onMouseDown, onMouseUp }) => {
  return (
    <div onMouseDown={onMouseDown} onMouseUp={onMouseUp} className="flex self-stretch items-center px-2 cursor-col-resize">
      <div className="h-full bg-gray-200 w-px" />
    </div>
  );
};

const SplitPane = ({ children, minSize = 50, initSize = 200 }) => {
  const [active, setActive] = useState(false);
  const [position, setPosition] = useState(undefined);
  const [size, setSize] = useState(initSize);
  const leftPane = useRef(undefined);

  const onMouseDown = (event) => {
    unFocus(document, window);
    const position = event.clientX;

    setActive(true);
    setPosition(position);
  }

  const onMouseUp = (event) => {
    setActive(false);
  }

  const onMouseMove = (event) => {
    if (active) {
      unFocus(document, window);
      if (leftPane.current.getBoundingClientRect) {
        const size = leftPane.current.getBoundingClientRect().width;
        const current = event.clientX;
        const sizeDelta = position - current;

        let newSize = size - sizeDelta;

        if (newSize < minSize) {
          newSize = minSize;
        }

        setPosition(current);
        setSize(newSize);
      }
    }
  }

  useEffect(() => {
    document.addEventListener('mouseup', onMouseUp);
    document.addEventListener('mousemove', onMouseMove);
    return function cleanup() {
      document.removeEventListener('mouseup', onMouseUp);
      document.removeEventListener('mousemove', onMouseMove);
    };
  });

  return (
    <div className="flex">
      <Pane ref={leftPane} size={size}>
        {children[0]}
      </Pane>
      <Resizer onMouseDown={onMouseDown} onMouseUp={onMouseUp} />
      <Pane>
        {children[1]}
      </Pane>
    </div>
  )


}
export default SplitPane;
