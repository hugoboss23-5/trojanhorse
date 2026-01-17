const canvas = document.getElementById('canvas');
const blocks = [];
const connections = [];
const SINK_SPEED = 0.8;
const BLOCK_WIDTH = 80;
const BLOCK_HEIGHT = 50;
const FALL_DELAY = 150;

let draggedBlock = null;
let offsetX = 0;
let offsetY = 0;

let isConnecting = false;
let connectionStart = null;
let tempLine = null;

let hoveredBlock = null;

const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
svg.id = 'connections';
canvas.appendChild(svg);

const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
defs.innerHTML = `
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
        <polygon points="0 0, 10 3.5, 0 7" fill="#444" />
    </marker>
    <marker id="arrowhead-active" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
        <polygon points="0 0, 10 3.5, 0 7" fill="#666" />
    </marker>
`;
svg.appendChild(defs);

document.addEventListener('keydown', (e) => {
    if (e.key === 'Shift') {
        canvas.classList.add('connecting');
    }
});

document.addEventListener('keyup', (e) => {
    if (e.key === 'Shift') {
        canvas.classList.remove('connecting');
    }
});

canvas.addEventListener('click', (e) => {
    if (e.target !== canvas) return;
    if (e.shiftKey) return;

    const block = document.createElement('div');
    block.className = 'block';
    block.style.left = (e.clientX - 40) + 'px';
    block.style.top = (e.clientY - 25) + 'px';
    block.dataset.fallDelay = '0';
    block.dataset.wobbleOffset = Math.random() * Math.PI * 2;
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
    draggedBlock.dataset.fallDelay = '0';

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

canvas.addEventListener('mouseover', (e) => {
    if (e.target.classList.contains('block')) {
        hoveredBlock = e.target;
        updateHoverHighlights();
    }
});

canvas.addEventListener('mouseout', (e) => {
    if (e.target.classList.contains('block')) {
        hoveredBlock = null;
        clearHoverHighlights();
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
    updateWobbleStates();
    updateConnectionWeights();
}

function removeConnection(index) {
    if (index < 0 || index >= connections.length) return;

    const conn = connections[index];
    svg.removeChild(conn.line);
    connections.splice(index, 1);

    updateConnectionIndices();
    updateWobbleStates();
    updateConnectionWeights();
    markUnsupportedForFall();
}

function updateConnectionIndices() {
    connections.forEach((conn, i) => {
        conn.line.dataset.index = i;
    });
}

function deleteBlock(block) {
    const index = blocks.indexOf(block);
    if (index === -1) return;

    block.classList.add('deleting');

    setTimeout(() => {
        for (let i = connections.length - 1; i >= 0; i--) {
            if (connections[i].supporter === block || connections[i].dependent === block) {
                svg.removeChild(connections[i].line);
                connections.splice(i, 1);
            }
        }
        updateConnectionIndices();

        blocks.splice(index, 1);
        if (block.parentNode) {
            canvas.removeChild(block);
        }
        updateWobbleStates();
        updateConnectionWeights();
        markUnsupportedForFall();
    }, 100);
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

function findCyclicBlocks() {
    const inCycle = new Set();

    for (const block of blocks) {
        if (isInCycle(block, new Set())) {
            inCycle.add(block);
        }
    }

    return inCycle;
}

function isInCycle(block, visited, start = null) {
    if (start === null) start = block;

    for (const conn of connections) {
        if (conn.dependent === block) {
            const supporter = conn.supporter;

            if (supporter === start) {
                return true;
            }

            if (!visited.has(supporter)) {
                visited.add(supporter);
                if (isInCycle(supporter, visited, start)) {
                    return true;
                }
            }
        }
    }

    return false;
}

function getDependentsOfWobbling(wobblingSet) {
    const allWobbling = new Set(wobblingSet);
    let changed = true;

    while (changed) {
        changed = false;
        for (const conn of connections) {
            if (allWobbling.has(conn.supporter) && !allWobbling.has(conn.dependent)) {
                allWobbling.add(conn.dependent);
                changed = true;
            }
        }
    }

    return allWobbling;
}

function updateWobbleStates() {
    const cyclicBlocks = findCyclicBlocks();
    const allWobbling = getDependentsOfWobbling(cyclicBlocks);

    for (const block of blocks) {
        if (allWobbling.has(block)) {
            block.classList.add('wobble');
        } else {
            block.classList.remove('wobble');
        }
    }
}

function isWobbling(block) {
    return block.classList.contains('wobble');
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

function updateConnectionWeights() {
    for (const conn of connections) {
        const supporterGrounded = hasSupport(conn.supporter);
        if (supporterGrounded) {
            conn.line.classList.add('load-bearing');
            conn.line.classList.remove('floating');
            conn.line.setAttribute('marker-end', 'url(#arrowhead-active)');
        } else {
            conn.line.classList.remove('load-bearing');
            conn.line.classList.add('floating');
            conn.line.setAttribute('marker-end', 'url(#arrowhead)');
        }
    }
}

function updateGroundedStates() {
    for (const block of blocks) {
        if (isGrounded(block)) {
            block.classList.add('grounded');
        } else {
            block.classList.remove('grounded');
        }
    }
}

function markUnsupportedForFall() {
    for (const block of blocks) {
        if (!hasSupport(block) && !isWobbling(block)) {
            block.dataset.fallDelay = Date.now().toString();
        }
    }
}

function getDependents(block, visited = new Set()) {
    const dependents = new Set();
    for (const conn of connections) {
        if (conn.supporter === block && !visited.has(conn.dependent)) {
            dependents.add(conn.dependent);
            visited.add(conn.dependent);
            const subDeps = getDependents(conn.dependent, visited);
            subDeps.forEach(d => dependents.add(d));
        }
    }
    return dependents;
}

function getSupporters(block, visited = new Set()) {
    const supporters = new Set();
    for (const conn of connections) {
        if (conn.dependent === block && !visited.has(conn.supporter)) {
            supporters.add(conn.supporter);
            visited.add(conn.supporter);
            const subSups = getSupporters(conn.supporter, visited);
            subSups.forEach(s => supporters.add(s));
        }
    }
    return supporters;
}

function updateHoverHighlights() {
    if (!hoveredBlock) return;

    const dependents = getDependents(hoveredBlock);
    const supporters = getSupporters(hoveredBlock);

    dependents.forEach(b => b.classList.add('highlight-dependent'));
    supporters.forEach(b => b.classList.add('highlight-supporter'));
}

function clearHoverHighlights() {
    for (const block of blocks) {
        block.classList.remove('highlight-dependent');
        block.classList.remove('highlight-supporter');
    }
}

let wobbleTime = 0;

function applyGravity() {
    const groundY = getGroundY();
    const now = Date.now();
    wobbleTime += 0.05;

    for (const block of blocks) {
        if (block === draggedBlock) continue;

        const currentY = parseFloat(block.style.top) || 0;

        if (currentY >= groundY) {
            block.style.top = groundY + 'px';
            continue;
        }

        if (isWobbling(block)) {
            const offset = parseFloat(block.dataset.wobbleOffset) || 0;
            const wobbleX = Math.sin(wobbleTime * 8 + offset) * 2 +
                           Math.sin(wobbleTime * 13 + offset * 2) * 0.5;
            block.style.transform = `translateX(${wobbleX}px)`;
            continue;
        } else {
            block.style.transform = '';
        }

        if (hasSupport(block)) {
            block.dataset.fallDelay = '0';
            continue;
        }

        const fallStart = parseInt(block.dataset.fallDelay) || 0;
        if (fallStart === 0) {
            block.dataset.fallDelay = now.toString();
            continue;
        }

        if (now - fallStart < FALL_DELAY) {
            continue;
        }

        const elapsed = now - fallStart - FALL_DELAY;
        const easeIn = Math.min(1, elapsed / 300);
        const speed = SINK_SPEED * easeIn;

        const newY = Math.min(currentY + speed, groundY);
        block.style.top = newY + 'px';
    }

    updateGroundedStates();
    updateConnectionLines();
    updateConnectionWeights();
    requestAnimationFrame(applyGravity);
}

requestAnimationFrame(applyGravity);
