// This loads an env-specific config file at runtime
export async function loadConfig() {
  const res = await fetch('/env.js');
  const text = await res.text();
  const config = {};
  new Function('config', text)(config); // 👈 load into object
  return config;
}
