const { spawnSync } = require("node:child_process");

const candidates = [
  { command: "python", prefixArgs: [] },
  { command: "python3", prefixArgs: [] },
  { command: "py", prefixArgs: ["-3"] },
  {
    command: "C:\\Users\\pc\\AppData\\Local\\Programs\\Python\\Python315\\python.exe",
    prefixArgs: [],
  },
];

function runPython(args, options = {}) {
  let lastError = null;

  for (const candidate of candidates) {
    const result = spawnSync(candidate.command, [...candidate.prefixArgs, ...args], {
      stdio: "inherit",
      shell: false,
      ...options,
    });

    if (result.status === 0) {
      return 0;
    }

    if (result.error) {
      lastError = result.error;
      if (result.error.code === "ENOENT" || result.error.code === "EPERM") {
        continue;
      }
      return result.status || 1;
    }
  }

  console.error(lastError ? lastError.message : "No Python runtime was available.");
  return 1;
}

module.exports = { runPython };
