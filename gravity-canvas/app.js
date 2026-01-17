const canvas = document.getElementById('canvas');
const blocks = [];
const connections = [];
const SINK_SPEED = 0.8;
const BLOCK_WIDTH = 80;
const BLOCK_HEIGHT = 50;

let draggedBlock = null;
let offsetX = 0;
let offsetY = 0;

let isConnecting = false;
let connectionStart = null;
let tempLine = null;

const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
svg.id = 'connections';
canvas.appendChild(svg);

const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
defs.innerHTML = `
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
        <polygon points="0 0, 10 3.5, 0 7" fill="#444" />
    </marker>
`;
svg.appendChild(defs);

canvas.addEventListener('click', (e) => {
    if (e.target !== canvas) return;
    if (e.shiftKey) return;

    const block = document.createElement('div');
    block.className = 'block';
    block.style.left = (e.clientX - 40) + 'px';
    block.style.top = (e.clientY - 25) + 'px';
    canvas.appendChild(block);
    blocks.push(block);
});

canvas.addEventListener('mousedown', (e) => {
    if (!e.target.classList.contains('block')) return;

    if (e.shiftKey) {
        isConnecting = true;
        connectionStart = e.target;

        tempLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        tempLine.setAttribute('class', 'temp-line');
        const startPos = getBlockCenter(connectionStart);
        tempLine.setAttribute('x1', startPos.x);
        tempLine.setAttribute('y1', startPos.y);
        tempLine.setAttribute('x2', startPos.x);
        tempLine.setAttribute('y2', startPos.y);
        svg.appendChild(tempLine);
        return;
    }

    draggedBlock = e.target;
    draggedBlock.classList.add('dragging');

    const rect = draggedBlock.getBoundingClientRect();
    offsetX = e.clientX - rect.left;
    offsetY = e.clientY - rect.top;
});

document.addEventListener('mousemove', (e) => {
    if (isConnecting && tempLine) {
        tempLine.setAttribute('x2', e.clientX);
        tempLine.setAttribute('y2', e.clientY);
        return;
    }

    if (!draggedBlock) return;

    draggedBlock.style.left = (e.clientX - offsetX) + 'px';
    draggedBlock.style.top = (e.clientY - offsetY) + 'px';
});

document.addEventListener('mouseup', (e) => {
    if (isConnecting) {
        if (tempLine) {
            svg.removeChild(tempLine);
            tempLine = null;
        }

        const target = e.target;
        if (target.classList.contains('block') && target !== connectionStart) {
            createConnection(connectionStart, target);
        }

        isConnecting = false;
        connectionStart = null;
        return;
    }

    if (draggedBlock) {
        draggedBlock.classList.remove('dragging');
        draggedBlock = null;
    }
});

canvas.addEventListener('contextmenu', (e) => {
    e.preventDefault();

    if (e.target.classList.contains('block')) {
        deleteBlock(e.target);
    }
});

svg.addEventListener('click', (e) => {
    if (!e.shiftKey) return;

    if (e.target.classList.contains('connection-line')) {
        const index = parseInt(e.target.dataset.index);
        removeConnection(index);
    }
});

function getBlockCenter(block) {
    const x = parseFloat(block.style.left) + BLOCK_WIDTH / 2;
    const y = parseFloat(block.style.top) + BLOCK_HEIGHT / 2;
    return { x, y };
}

function createConnection(supporter, dependent) {
    for (const conn of connections) {
        if (conn.supporter === supporter && conn.dependent === dependent) {
            return;
        }
    }

    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('class', 'connection-line');
    line.setAttribute('marker-end', 'url(#arrowhead)');
    svg.appendChild(line);

    connections.push({ supporter, dependent, line });
    updateConnectionLines();
}

function removeConnection(index) {
    if (index < 0 || index >= connections.length) return;

    const conn = connections[index];
    svg.removeChild(conn.line);
    connections.splice(index, 1);

    updateConnectionIndices();
}

function updateConnectionIndices() {
    connections.forEach((conn, i) => {
        conn.line.dataset.index = i;
    });
}

function deleteBlock(block) {
    const index = blocks.indexOf(block);
    if (index === -1) return;

    for (let i = connections.length - 1; i >= 0; i--) {
        if (connections[i].supporter === block || connections[i].dependent === block) {
            svg.removeChild(connections[i].line);
            connections.splice(i, 1);
        }
    }
    updateConnectionIndices();

    blocks.splice(index, 1);
    canvas.removeChild(block);
}

function updateConnectionLines() {
    connections.forEach((conn, i) => {
        const start = getBlockCenter(conn.supporter);
        const end = getBlockCenter(conn.dependent);

        conn.line.setAttribute('x1', start.x);
        conn.line.setAttribute('y1', start.y);
        conn.line.setAttribute('x2', end.x);
        conn.line.setAttribute('y2', end.y);
        conn.line.dataset.index = i;
    });
}

function getGroundY() {
    return canvas.clientHeight - BLOCK_HEIGHT;
}

function isGrounded(block) {
    const y = parseFloat(block.style.top) || 0;
    return y >= getGroundY() - 0.5;
}

function hasSupport(block, visited = new Set()) {
    if (visited.has(block)) return false;
    visited.add(block);

    if (isGrounded(block)) return true;

    for (const conn of connections) {
        if (conn.dependent === block) {
            if (hasSupport(conn.supporter, visited)) {
                return true;
            }
        }
    }

    return false;
}

function applyGravity() {
    const groundY = getGroundY();

    for (const block of blocks) {
        if (block === draggedBlock) continue;

        const currentY = parseFloat(block.style.top) || 0;

        if (currentY >= groundY) continue;

        if (hasSupport(block)) continue;

        const newY = Math.min(currentY + SINK_SPEED, groundY);
        block.style.top = newY + 'px';
    }

    updateConnectionLines();
    requestAnimationFrame(applyGravity);
}

requestAnimationFrame(applyGravity);
