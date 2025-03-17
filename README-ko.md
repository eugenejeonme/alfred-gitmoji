## Alfred Gitmoji Workflow

![Alfred Gitmoji Thumbnail](./screenshots/thumbnail-ko.png)

Alfred Workflow 에서 Gitmoji 를 검색/복사할 수 있도록 만든 것입니다.

## 사용법

- <kbd>return</kbd> (↵): Copy the symbol of the selected emoji) (e.g. "🐛") to your clipboard.
- <kbd>option+return</kbd> (⌥↵): Copy the code of the selected gitmoji (e.g. `:bug:`) directly to your front-most application.
- <kbd>shift+return</kbd> (⇧↵): Copy the hexadecimal HTML Entity of the selected emoji) (e.g. `&#x1f41b;`) to your clipboard.

## Benchmark

작성된 zsh, py 두 파일의 주요 작업들을 비교해보면:

1. JSON 파싱/처리
- Python: `json` 모듈 사용 (네이티브 구현)
- Zsh: `jq` 명령어 사용 (외부 프로세스 호출)

2. 문자열 처리
- Python: 내장 문자열 메소드 사용
- Zsh: 기본 문자열 처리 + perl 호출 (외부 프로세스)

3. 파일 시스템 작업
- Python: `os`, `pathlib` 모듈 사용
- Zsh: 네이티브 명령어 사용

간단한 벤치마크 스크립트를 만들어볼 수 있습니다:

```zsh
#!/bin/zsh

# benchmark.zsh
time_zsh() {
    local start=$(($(gdate +%s%N)/1000000))
    ./workflowscript.zsh "배포"
    local end=$(($(gdate +%s%N)/1000000))
    echo "Zsh execution time: $((end-start)) ms"
}

time_python() {
    local start=$(($(gdate +%s%N)/1000000))
    ./workflowscript.py "배포"
    local end=$(($(gdate +%s%N)/1000000))
    echo "Python execution time: $((end-start)) ms"
}

echo "Running benchmark..."
echo "Zsh version:"
time_zsh
echo "\nPython version:"
time_python
```

예상되는 결과:
1. 초기 실행 시:
   - Python이 더 느릴 수 있음 (인터프리터 시작 시간)
   - Zsh가 더 빠를 수 있음 (이미 실행 중인 셸 사용)

2. 반복 실행 시:
   - Python이 더 빠를 가능성이 높음
   - 이유:
     - 네이티브 JSON 처리
     - 외부 프로세스 호출 없음
     - 효율적인 문자열 처리

3. 메모리 사용:
   - Python이 더 많은 메모리 사용
   - Zsh는 더 가벼운 메모리 사용

작업의 특성상 (JSON 파싱, 문자열 처리가 주요 작업) Python이 조금 더 빠를 것으로 예상됩니다.
