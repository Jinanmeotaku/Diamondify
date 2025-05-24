

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
