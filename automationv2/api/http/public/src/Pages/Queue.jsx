import React, { useState, useRef } from 'react';

const QueueList = () => {
    const [items, setItems] = useState(["🍰 Cake", "🍩 Donut", "🍎 Apple", "🍕 Pizza"]);
    const [dragging, setDragging] = useState(null);

    const onDragStart = (e, index) => {
        setDragging(items[index])
        e.dataTransfer.effectAllowed = "move";
        e.dataTransfer.setData("text/html", e.target.parentNode);
        e.dataTransfer.setDragImage(e.target.parentNode, 20, 20);
    };

    const onDragOver = (e, index) => {
        const overItem = items[index]

        // if the item is dragged over itself, ignore
        if (dragging !== overItem) {
            // filter out the currently dragged item
            let newItems = items.filter((item) => item != dragging);
            // add the dragged item after the dragged over item
            newItems.splice(index, 0, dragging);
            setItems(newItems);
        }
        e.preventDefault();
    };

    const onDragEnd = () => {
        setDragging(null);
    };

    const allowDrop = (e) => {
        e.preventDefault();
    }

    return (<ul className="mx-10">
        {items.map((item, idx) => (
            <li className="flex" key={item} onDragOver={(e) => onDragOver(e, idx)}>
                <div className="drag"
                    onDragStart={(e) => onDragStart(e, idx)}
                    onDragEnd={onDragEnd}
                    draggable>
                    <i className="fa fa-bars" />
                </div>
                <span className="content">{item}</span>
            </li>
        ))}
    </ul>);
}

const QueuePage = () => {
    return (
        <div>
            <h1>Queue</h1>
            <QueueList />
        </div>
    );
}
export default QueuePage;

