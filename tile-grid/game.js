document.addEventListener("DOMContentLoaded", function() {
    const canvas = document.getElementById('gridCanvas');
    const ctx = canvas.getContext('2d');
    const tileSize = 32; // Size of each tile
    const gridWidth = 15;
    const gridHeight = 15;
    const canvasWidth = tileSize * gridWidth;
    const canvasHeight = tileSize * gridHeight;

    canvas.width = canvasWidth;
    canvas.height = canvasHeight;

    // Generate tile URLs based on naming pattern
    const tiles = [];
    for (let i = 0; i <= 114; i++) {
        tiles.push(`tile_${i.toString().padStart(3, '0')}.png`);
    }

    // Draw the grid
    function drawGrid() {
        ctx.clearRect(0, 0, canvasWidth, canvasHeight);
        for (let x = 0; x < gridWidth; x++) {
            for (let y = 0; y < gridHeight; y++) {
                ctx.strokeRect(x * tileSize, y * tileSize, tileSize, tileSize);
            }
        }
    }

    // Function to handle tile dragging
    function handleDragStart(e) {
        e.dataTransfer.setData('text/plain', this.id);
    }

    // Initialize the tile container
    const tileContainer = document.getElementById('tileContainer');
    tiles.forEach((tile, index) => {
        const img = new Image();
        img.src = tile;
        img.id = `tile${index}`;
        img.className = 'tile';
        img.draggable = true;
        img.addEventListener('dragstart', handleDragStart);
        tileContainer.appendChild(img);
    });

    // Event listener for canvas drop
    canvas.addEventListener('drop', function(e) {
        e.preventDefault();
        const tileId = e.dataTransfer.getData('text/plain');
        const img = document.getElementById(tileId);
        const rect = canvas.getBoundingClientRect();
        const x = Math.floor((e.clientX - rect.left) / tileSize) * tileSize;
        const y = Math.floor((e.clientY - rect.top) / tileSize) * tileSize;
        ctx.drawImage(img, x, y, tileSize, tileSize);
    });

    // Prevent default behavior for drag events
    canvas.addEventListener('dragover', function(e) {
        e.preventDefault();
    });

    // Redraw the grid initially and whenever needed
    drawGrid();
});
