

const image = document.getElementById('puzzleImage');
image.onload = () => {
  initPieces(image);
  animate();
};

let pieces = [];

function initPieces(image) {
  for (let row = 0; row < 10; row++) {
    for (let col = 0; col < 10; col++) {
      let piece = {
        correctX: col * pieceWidth,
        correctY: row * pieceHeight,
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        row, col
      };
      pieces.push(piece);
    }
  }
}

    function animate() {
    const bar = document.getElementById('loading-bar');

    // Count how many pieces are snapped into place
    let placed = 0;
    for (let p of pieces) {
    const closeEnoughX = Math.abs(p.x - p.correctX) < 0.5;
    const closeEnoughY = Math.abs(p.y - p.correctY) < 0.5;

    if (closeEnoughX) p.x = p.correctX;
    if (closeEnoughY) p.y = p.correctY;

    if (closeEnoughX && closeEnoughY) {
        placed++;
    }

    ctx.drawImage(
        image,
        p.srcX, p.srcY, pieceWidth, pieceHeight,
        p.x, p.y, drawWidth, drawHeight
    );
    }

    // Calculate progress %
    const progress = (placed / pieces.length) * 100;
    bar.style.width = `${progress}%`;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (let piece of pieces) {
        // Move towards correct position
        piece.x += (piece.correctX - piece.x) * 0.1;
        piece.y += (piece.correctY - piece.y) * 0.1;

        // Optional: snap into place
        if (Math.abs(piece.x - piece.correctX) < 1) piece.x = piece.correctX;
        if (Math.abs(piece.y - piece.correctY) < 1) piece.y = piece.correctY;

        // Draw the piece
        ctx.drawImage(
        fullImage,
        piece.col * pieceWidth, piece.row * pieceHeight, // source coords
        pieceWidth, pieceHeight,
        piece.x, piece.y, // destination coords
        pieceWidth, pieceHeight
        );
    }

    requestAnimationFrame(animate);
    }
