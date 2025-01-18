//Code to create the close buttons

function addCloseButtons() {
    const elements = document.querySelectorAll('.dashboard > div');

    elements.forEach(element => {
        const button = document.createElement('button');
        button.innerHTML = '×';
        button.title = 'Close';

        button.style.cursor = 'pointer';
        button.style.marginRight = '5px';

        button.onclick = function() {
            element.remove();
        };

        element.insertBefore(button, element.firstChild);
    });
}

addCloseButtons();

// script.js

// Array of custom POG designs (add your image paths here)
const pogDesigns = [
  'images/pog-design.png',
  'images/pog-design-2.png',
  'images/pog-design-3.png',
  'images/pog-design-4.png',
  'images/pog-design-5.png',
  'images/pog-design-6.png',
  
];

// Create a stack of POGs with custom designs
const stack = document.getElementById('stack');
const gameArea = document.getElementById('game-area');

for (let i = 0; i < 10; i++) {
  const pog = document.createElement('div');
  pog.className = 'pog';

  // Assign a random design to each POG
  const randomDesign = pogDesigns[Math.floor(Math.random() * pogDesigns.length)];
  pog.style.backgroundImage = `url('${randomDesign}')`;

  // Stagger initial stacking positions slightly for realism
  pog.style.bottom = `${20 + i * 5}px`; // Offset each POG vertically
  pog.style.left = `calc(50% - 25px)`; // Center each POG horizontally

  stack.appendChild(pog);
}

// Dragging the slammer
const slammer = document.getElementById('slammer');
let isDragging = false;

slammer.addEventListener('mousedown', (e) => {
  isDragging = true;

  // Offset to ensure smooth dragging
  const offsetX = e.clientX - slammer.offsetLeft;
  const offsetY = e.clientY - slammer.offsetTop;

  const moveSlammer = (event) => {
    if (isDragging) {
      const newX = event.clientX - offsetX;
      const newY = event.clientY - offsetY;

      // Constrain the slammer within the game area
      const gameAreaRect = gameArea.getBoundingClientRect();
      const slammerRect = slammer.getBoundingClientRect();

      if (
        newX >= gameAreaRect.left &&
        newX + slammerRect.width <= gameAreaRect.right &&
        newY >= gameAreaRect.top &&
        newY + slammerRect.height <= gameAreaRect.bottom
      ) {
        slammer.style.left = `${newX - gameAreaRect.left}px`;
        slammer.style.top = `${newY - gameAreaRect.top}px`;
      }
    }
  };

  const stopDragging = () => {
    isDragging = false;
    document.removeEventListener('mousemove', moveSlammer);
    document.removeEventListener('mouseup', stopDragging);

    // Simulate "throw" logic
    simulateSlam();
  };

  document.addEventListener('mousemove', moveSlammer);
  document.addEventListener('mouseup', stopDragging);
});

// Simulate the slam
function simulateSlam() {
  const pogs = document.querySelectorAll('.pog');
  const gameAreaRect = gameArea.getBoundingClientRect();

  pogs.forEach((pog) => {
    const pogRect = pog.getBoundingClientRect();

    // Generate random forces
    let randomX = Math.random() * 200 - 100; // Horizontal force
    let randomY = Math.random() * -150; // Upward force
    const rotation = Math.random() * 360; // Random rotation angle

    // Constrain new positions within the game area
    let newX = pogRect.left + randomX;
    let newY = pogRect.top + randomY;

    // Correct for horizontal bounds
    if (newX < gameAreaRect.left) newX = gameAreaRect.left;
    if (newX + pogRect.width > gameAreaRect.right) newX = gameAreaRect.right - pogRect.width;

    // Correct for vertical bounds
    if (newY < gameAreaRect.top) newY = gameAreaRect.top;
    if (newY + pogRect.height > gameAreaRect.bottom) newY = gameAreaRect.bottom - pogRect.height;

    // Apply movement
    pog.style.transform = `translate(${newX - pogRect.left}px, ${newY - pogRect.top}px) rotate(${rotation}deg)`;
    pog.style.transition = 'transform 0.5s ease-out';

    // Add gravity after scatter
    setTimeout(() => {
      const gravityY = Math.min(gameAreaRect.bottom - pogRect.bottom, 150); // Gravity pulls within bounds
      pog.style.transition = 'transform 1s ease-in';
      pog.style.transform += ` translateY(${gravityY}px)`;

      // Randomize face-up or face-down landing
      const isFaceUp = Math.random() > 0.5;
      if (isFaceUp) {
        pog.classList.add('face-up');
        pog.classList.remove('face-down');
      } else {
        pog.classList.add('face-down');
        pog.classList.remove('face-up');
      }
    }, 500);
  });
}
