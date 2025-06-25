const sections = document.querySelectorAll('.section');
const nextBtn = document.getElementById('nextBtn');
let currentSection = 0;


function showSection(index) {
    sections.forEach((section, i) => {
        if (i === index) {
            section.classList.add('active');
        } else {
            section.classList.remove('active');
        }
    });
}

nextBtn.addEventListener('click', () => {
    currentSection = (currentSection + 1) % sections.length;
    showSection(currentSection);
});

showSection(currentSection); // Hiển thị section đầu tiên