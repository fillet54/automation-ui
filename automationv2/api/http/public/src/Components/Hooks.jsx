import { useRef, useEffect, useLayoutEffect, useState, useCallback } from 'react';

export const useWindowSize = () => {
    // Initialize state with undefined width/height so server and client renders match
    // Learn more here: https://joshwcomeau.com/react/the-perils-of-rehydration/
    const [windowSize, setWindowSize] = useState({
        width: undefined,
        height: undefined,
    });
    useEffect(() => {
        // Handler to call on window resize
        function handleResize() {
            // Set window width/height to state
            setWindowSize({
                width: window.innerWidth,
                height: window.innerHeight,
            });
        }
        // Add event listener
        window.addEventListener("resize", handleResize);
        // Call handler right away so state gets updated with initial window size
        handleResize();
        // Remove event listener on cleanup
        return () => window.removeEventListener("resize", handleResize);
    }, []); // Empty array ensures that effect is only run on mount
    return windowSize;
}


export const useResizeObserver = () => {
    const [observerEntry, setObserverEntry] = useState({});
    const [node, setNode] = useState(null);
    const observer = useRef(null);

    const disconnect = useCallback(() => {
        if (observer.current) {
            observer.current.disconnect()
        }
    }, []);

    const observe = useCallback(() => {
        observer.current = new ResizeObserver(([entry]) => setObserverEntry(entry));
        if (node) observer.current.observe(node);
    }, [node]);

    useLayoutEffect(() => {
        observe();
        return () => disconnect();
    }, [disconnect, observe]);

    return [setNode, observerEntry];
};