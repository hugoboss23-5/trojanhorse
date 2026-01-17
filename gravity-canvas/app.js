const canvas = document.getElementById('canvas');

let draggedBlock = null;
let offsetX = 0;
let offsetY = 0;

canvas.addEventListener('click', (e) => {
    if (e.target !== canvas) return;

    const block = document.createElement('div');
    block.className = 'block';
    block.style.left = (e.clientX - 40) + 'px';
    block.style.top = (e.clientY - 25) + 'px';
    canvas.appendChild(block);
});

canvas.addEventListener('mousedown', (e) => {
    if (!e.target.classList.contains('block')) return;

    draggedBlock = e.target;
    draggedBlock.classList.add('dragging');

    const rect = draggedBlock.getBoundingClientRect();
    offsetX = e.clientX - rect.left;
    offsetY = e.clientY - rect.top;
});

document.addEventListener('mousemove', (e) => {
    if (!draggedBlock) return;

    draggedBlock.style.left = (e.clientX - offsetX) + 'px';
    draggedBlock.style.top = (e.clientY - offsetY) + 'px';
});

document.addEventListener('mouseup', () => {
    if (draggedBlock) {
        draggedBlock.classList.remove('dragging');
        draggedBlock = null;
    }
});
