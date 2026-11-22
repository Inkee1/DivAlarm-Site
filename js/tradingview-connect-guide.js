// The app hands off sign-in in the fragment. A section jump can happen before Firebase loads.
document.querySelector('.guide-nav').addEventListener('click', (event) => {
  const link = event.target.closest('a[href^="#"]');
  if (!link || !new URLSearchParams(location.hash.slice(1)).has('ct')) return;
  const section = document.getElementById(link.hash.slice(1));
  if (section) {
    event.preventDefault();
    section.scrollIntoView();
    section.tabIndex = -1;
    section.focus({ preventScroll: true });
  }
});

// The setup page works without a video player. Load a Short only when its chapter opens.
for (const video of document.querySelectorAll('.guide-video')) {
  const player = video.querySelector('.guide-player');
  const link = video.querySelector('a');
  const id = new URL(link.href).pathname.split('/').pop();
  if (!/^[\w-]{11}$/.test(id)) continue;

  const update = () => {
    if (!video.open) {
      player.replaceChildren();
      return;
    }
    if (player.firstElementChild) return;
    const frame = document.createElement('iframe');
    frame.title = video.querySelector('summary').textContent.trim();
    frame.src = 'https://www.youtube-nocookie.com/embed/' + id;
    frame.allow = 'encrypted-media; picture-in-picture; fullscreen';
    frame.allowFullscreen = true;
    frame.referrerPolicy = 'strict-origin-when-cross-origin';
    player.append(frame);
  };
  video.addEventListener('toggle', update);
  update();
}
