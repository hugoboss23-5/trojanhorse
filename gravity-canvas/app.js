const canvas = document.getElementById('canvas');
const blocks = [];
const SINK_SPEED = 0.8;
const BLOCK_HEIGHT = 50;

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
    blocks.push(block);
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

function getGroundY() {
    return canvas.clientHeight - BLOCK_HEIGHT;
}

function applyGravity() {
    const groundY = getGroundY();

    for (const block of blocks) {
        if (block === draggedBlock) continue;

        const currentY = parseFloat(block.style.top) || 0;

        if (currentY < groundY) {
            const newY = Math.min(currentY + SINK_SPEED, groundY);
            block.style.top = newY + 'px';
        }
    }

    requestAnimationFrame(applyGravity);
}

requestAnimationFrame(applyGravity);
