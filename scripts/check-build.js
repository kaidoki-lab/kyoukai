const { runPython } = require("./python-runner");

process.exit(runPython(["-m", "py_compile", "main.py", "api/index.py"]));
