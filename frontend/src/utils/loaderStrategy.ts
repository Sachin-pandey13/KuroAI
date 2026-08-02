export function getLoaderMode(): 'full' | 'short' | 'skip' {
  if (typeof window === 'undefined') return 'full';
  
  // Respect user prefers-reduced-motion
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    return 'skip';
  }

  // Check URL params e.g. ?skipIntro=1
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('skipIntro') === '1') {
    return 'skip';
  }

  const lastVisit = localStorage.getItem('kuro_intro_ts');
  const now = Date.now();

  // If visited within 24 hours, show short loader
  if (lastVisit && now - Number(lastVisit) < 86_400_000) {
    return 'short';
  }

  // Store current timestamp for future visits
  localStorage.setItem('kuro_intro_ts', now.toString());
  return 'full';
}
