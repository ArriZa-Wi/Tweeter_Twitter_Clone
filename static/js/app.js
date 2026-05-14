/* =========================================================================
   Tweeter — Client app
   - Markdown rendering + Prism syntax highlighting for tweet bodies
   - htmx wiring: NProgress top bar, toast feedback, like animations
   - Auto-prepend new tweets and animate removals
   ========================================================================= */

(function () {
  'use strict';

  // ---- Notyf (toasts) ----
  const notyf = new Notyf({
    duration: 2800,
    position: { x: 'right', y: 'top' },
    types: [
      { type: 'success', background: '#3fb950', icon: false },
      { type: 'error',   background: '#ff7b72', icon: false },
      { type: 'info',    background: '#79c0ff', icon: false }
    ]
  });
  window.notyf = notyf;

  // ---- Marked + DOMPurify config ----
  if (window.marked) {
    marked.setOptions({
      breaks: true,
      gfm: true,
      headerIds: false,
      mangle: false
    });
  }

  function renderMarkdownIn(root) {
    if (!root || !window.marked || !window.DOMPurify) return;
    const nodes = root.querySelectorAll('.twit-content[data-markdown]:not([data-rendered])');
    nodes.forEach(node => {
      const raw = node.getAttribute('data-source') || node.textContent;
      const html = DOMPurify.sanitize(marked.parse(raw));
      node.innerHTML = html;
      node.setAttribute('data-rendered', '1');
      if (window.Prism) Prism.highlightAllUnder(node);
    });
  }

  // ---- CountUp helper ----
  function animateCount(el, to) {
    if (!el || !window.countUp) return;
    const from = parseInt(el.getAttribute('data-prev') || el.textContent || '0', 10) || 0;
    const counter = new countUp.CountUp(el, to, { startVal: from, duration: 0.6, useEasing: true });
    if (!counter.error) counter.start();
    el.setAttribute('data-prev', to);
  }

  function spawnParticles(btn) {
    btn.classList.remove('is-bursting');
    // strip any old particles
    btn.querySelectorAll('.particle').forEach(p => p.remove());
    let container = btn.querySelector('.particles');
    if (!container) {
      container = document.createElement('span');
      container.className = 'particles';
      btn.appendChild(container);
    }
    for (let i = 0; i < 5; i++) {
      const p = document.createElement('span');
      p.className = 'particle';
      container.appendChild(p);
    }
    void btn.offsetWidth; // reflow
    btn.classList.add('is-bursting');
    setTimeout(() => btn.classList.remove('is-bursting'), 650);
  }

  // ---- NProgress wiring ----
  if (window.NProgress) {
    NProgress.configure({ showSpinner: false, trickleSpeed: 120, minimum: 0.18 });
    document.addEventListener('htmx:beforeRequest', () => NProgress.start());
    document.addEventListener('htmx:afterRequest', () => NProgress.done());
    document.addEventListener('htmx:responseError', () => { NProgress.done(); notyf.error('request failed'); });
    document.addEventListener('htmx:sendError', () => { NProgress.done(); notyf.error('network error'); });
  }

  // ---- Render markdown on initial load + after htmx swaps ----
  document.addEventListener('DOMContentLoaded', () => renderMarkdownIn(document));
  document.addEventListener('htmx:afterSwap', (e) => {
    renderMarkdownIn(e.detail.target || document);
    // Re-init Alpine for swapped-in nodes (Alpine handles automatically via mutation observer)
  });

  // ---- HX-Trigger: server emits events to drive UI ----
  document.body.addEventListener('twit:created', () => notyf.success('tweet committed ✓'));
  document.body.addEventListener('twit:updated', () => notyf.success('tweet patched'));
  document.body.addEventListener('twit:deleted', () => notyf.success('tweet removed'));
  document.body.addEventListener('comment:created', () => notyf.success('comment posted'));

  document.body.addEventListener('twit:liked', (e) => {
    const detail = e.detail || {};
    const twitId = detail.twit_id;
    const count = detail.count;
    const liked = detail.liked;
    if (twitId == null) return;
    const btn = document.querySelector(`.like-btn[data-twit-id="${twitId}"]`);
    if (!btn) return;
    btn.classList.toggle('is-liked', !!liked);
    if (liked) spawnParticles(btn);
    const countEl = btn.querySelector('.like-count');
    if (countEl && typeof count === 'number') animateCount(countEl, count);
  });

  // ---- Animated removal: when server returns 200 for delete, fade out card ----
  document.body.addEventListener('htmx:beforeSwap', (e) => {
    // If swap is "delete", we handle via hx-swap="outerHTML swap:300ms" + class
    const trigger = e.detail.requestConfig && e.detail.requestConfig.elt;
    if (!trigger) return;
    if (trigger.dataset && trigger.dataset.removesCard === '1') {
      const card = trigger.closest('.twit-card');
      if (card) card.classList.add('is-leaving');
    }
  });

  // ---- Mark freshly-swapped tweet cards for the slide-in animation ----
  document.addEventListener('htmx:afterSwap', (e) => {
    const target = e.detail.target;
    if (!target) return;
    if (target.id === 'feed' || target.classList.contains('feed-list')) {
      // The first card is freshly added (afterbegin swap)
      const firstCard = target.querySelector('.twit-card');
      if (firstCard && !firstCard.classList.contains('is-new')) {
        firstCard.classList.add('is-new');
        setTimeout(() => firstCard.classList.remove('is-new'), 400);
      }
    }
  });

  // ---- Form reset after successful tweet create ----
  document.body.addEventListener('htmx:afterRequest', (e) => {
    const cfg = e.detail.requestConfig;
    if (!cfg) return;
    const form = cfg.elt;
    if (e.detail.successful && form && form.matches('form[data-reset-on-success]')) {
      form.reset();
      // reset char counter via Alpine
      const counterEl = form.querySelector('[x-data]');
      if (counterEl && counterEl._x_dataStack) {
        counterEl._x_dataStack[0].count = 0;
      }
    }
  });

  // ---- Modal close on Escape (handled by Alpine in template) ----
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.dispatchEvent(new CustomEvent('modal:close'));
    }
  });
})();
