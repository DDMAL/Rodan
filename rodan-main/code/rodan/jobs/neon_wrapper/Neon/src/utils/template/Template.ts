async function setBody (): Promise<void> {
  const response = await fetch(__ASSET_PREFIX__ + 'assets/template.html');
  document.body.innerHTML = await response.text();
  (document.getElementById('home-link') as HTMLAnchorElement)
    .href = __LINK_LOCATION__;
  document.getElementById('neon-version').textContent = __NEON_VERSION__;
}

export { setBody as default };
