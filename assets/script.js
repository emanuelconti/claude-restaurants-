document.getElementById('year').textContent = new Date().getFullYear();

const nav = document.getElementById('nav');
const navToggle = document.getElementById('navToggle');
navToggle.addEventListener('click', () => {
  const isOpen = nav.classList.toggle('menu-open');
  navToggle.setAttribute('aria-expanded', isOpen);
});
nav.querySelectorAll('.nav-links a').forEach(link => {
  link.addEventListener('click', () => nav.classList.remove('menu-open'));
});

const betaForm = document.getElementById('betaForm');
const formNote = document.getElementById('formNote');

betaForm.addEventListener('submit', (e) => {
  e.preventDefault();
  const data = new FormData(betaForm);
  const name = data.get('name').trim();
  const email = data.get('email').trim();
  const role = data.get('role');
  const city = data.get('city').trim();

  const roleLabel = {
    business: 'Business (restaurant, bar, studio...)',
    organizer: 'Organizer / crew member',
    other: 'Something else'
  }[role] || role;

  const subject = encodeURIComponent('SocialPerks beta access request');
  const body = encodeURIComponent(
    `Name: ${name}\nEmail: ${email}\nRole: ${roleLabel}\nCity: ${city || 'n/a'}\n`
  );

  window.location.href = `mailto:emanuelconti.mim@gmail.com?subject=${subject}&body=${body}`;
  formNote.textContent = "Your email client should be opening now — just hit send!";
});
