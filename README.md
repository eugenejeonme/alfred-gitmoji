## Alfred Gitmoji Workflow

![Alfred Gitmoji Thumbnail](./screenshots/thumbnail.png)

A workflow for searching and copying Gitmoji in Alfred.

## How to use

- <kbd>return</kbd> (↵): Copy the symbol of the selected emoji) (e.g. "🐛") to your clipboard.
- <kbd>option+return</kbd> (⌥↵): Copy the code of the selected gitmoji (e.g. `:bug:`) directly to your front-most application.
- <kbd>shift+return</kbd> (⇧↵): Copy the hexadecimal HTML Entity of the selected emoji) (e.g. `&#x1f41b;`) to your clipboard.

## Benchmark

Comparing the main operations of the two files (zsh and py):

1. JSON Parsing/Processing
- Python: Uses `json` module (native implementation)
- Zsh: Uses `jq` command (external process call)

2. String Processing
- Python: Uses built-in string methods
- Zsh: Basic string processing + perl call (external process)

3. File System Operations
- Python: Uses `os`, `pathlib` modules
- Zsh: Uses native commands

Here's a simple benchmark script:

```zsh
#!/bin/zsh

# benchmark.zsh
time_zsh() {
    local start=$(($(gdate +%s%N)/1000000))
    ./workflowscript.zsh "deploy"
    local end=$(($(gdate +%s%N)/1000000))
    echo "Zsh execution time: $((end-start)) ms"
}

time_python() {
    local start=$(($(gdate +%s%N)/1000000))
    ./workflowscript.py "deploy"
    local end=$(($(gdate +%s%N)/1000000))
    echo "Python execution time: $((end-start)) ms"
}

echo "Running benchmark..."
echo "Zsh version:"
time_zsh
echo "\nPython version:"
time_python
```

Expected results:
1. Initial Execution:
- Python might be slower (interpreter startup time)
- Zsh might be faster (using already running shell)

2. Repeated Execution:
- Python is likely to be faster
- Reasons:
  - Native JSON processing
  - No external process calls
  - Efficient string processing

3. Memory Usage:
- Python uses more memory
- Zsh uses lighter memory

Given the nature of the work (JSON parsing, string processing being the main tasks), Python is expected to be slightly faster.
