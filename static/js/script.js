// Add click effect to animated buttons
document.addEventListener('DOMContentLoaded', function () {
  const animatedButtons = document.querySelectorAll('.btn-animated');

  animatedButtons.forEach(button => {
    button.addEventListener('mousedown', () => {
      button.style.transform = 'scale(0.95)';
    });

    button.addEventListener('mouseup', () => {
      button.style.transform = 'scale(1)';
    });

    button.addEventListener('mouseleave', () => {
      button.style.transform = 'scale(1)';
    });
  });
});
