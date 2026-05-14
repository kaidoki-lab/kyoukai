const { runPython } = require("./python-runner");

process.exit(runPython(["main.py"]));
