#!/bin/zsh

GITMOJIS_JSON="gitmojis.json"
ICONS_DIR="icons"
ICONS_TAR="icons.tar.gz"
BASE_URL="https://raw.githubusercontent.com/eugenejeonme/alfred-gitmoji/refs/heads/main/src/gitmojis/assets"

# 문자열 정규화 함수
normalize_korean() {
    echo "$1" | perl -CS -MUnicode::Normalize -e 'print NFC(<>)'
}

# 초기화 함수
initialize_gitmojis() {
    local initialization_needed=false

    # 디렉토리 생성
    mkdir -p "$ICONS_DIR"

    # gitmojis.json이 없으면 다운로드
    if [[ ! -f "$GITMOJIS_JSON" ]]; then
        initialization_needed=true
        print -r -- "{\"rerun\": 0.1, \"items\":[{\"title\":\"Downloading gitmojis.json\",\"subtitle\":\"Please wait...\",\"valid\":false}]}"
        curl -s "${BASE_URL}/gitmojis.json" > "$GITMOJIS_JSON"
        if (( $? != 0 )); then
            print -r -- "{\"items\":[{\"title\":\"Error\",\"subtitle\":\"Failed to download gitmojis.json\",\"valid\":false}]}"
            return 1
        fi
    fi

    # icons 디렉토리가 비어있으면 tar 파일 다운로드 및 압축해제
    if [[ -z "$(ls -A $ICONS_DIR)" ]]; then
        initialization_needed=true
        print -r -- "{\"rerun\": 0.1, \"items\":[{\"title\":\"Downloading\",\"subtitle\":\"Getting icons.tar.gz...\",\"valid\":false}]}"

        # tar 파일 다운로드
        curl -s "${BASE_URL}/icons.tar.gz" > "$ICONS_TAR"
        if (( $? != 0 )); then
            print -r -- "{\"items\":[{\"title\":\"Error\",\"subtitle\":\"Failed to download icons.tar.gz\",\"valid\":false}]}"
            return 1
        fi

        # tar 파일 압축해제
        print -r -- "{\"rerun\": 0.1, \"items\":[{\"title\":\"Extracting\",\"subtitle\":\"Unpacking icons...\",\"valid\":false}]}"
        tar -xzf "$ICONS_TAR"
        if (( $? != 0 )); then
            print -r -- "{\"items\":[{\"title\":\"Error\",\"subtitle\":\"Failed to extract icons\",\"valid\":false}]}"
            return 1
        fi

        # 압축 해제 후 tar 파일 삭제
        rm -f "$ICONS_TAR"
        return 1
    fi

    # 초기화가 필요없으면 0 반환
    if [[ "$initialization_needed" == "false" ]]; then
        return 0
    fi
    return 1
}

search_gitmojis() {
    local query="$1"
    local is_ko="$2"

    query=${query:l} # zsh의 소문자 변환
    query=$(normalize_korean "$query") # 검색어 정규화

    if [[ -z "$query" ]]; then
        jq -c '{items: [.[] | {
            valid: true,
            title: (if "'$is_ko'" == "true" then .description.ko else .description.en end),
            subtitle: .code,
            arg: .emoji,
            icon: {path: "./icons/\(.name).png"}
        }]}' "$GITMOJIS_JSON"
    else
        jq -c --arg q "$query" '{items: [.[] | select(
            (.description.en|ascii_downcase|contains($q)) or
            (.description.ko|contains($q)) or
            (.name|ascii_downcase|contains($q))
        ) | {
            valid: true,
            title: (if "'$is_ko'" == "true" then .description.ko else .description.en end),
            subtitle: .code,
            arg: .emoji,
            icon: {path: "./icons/\(.name).png"}
        }]}' "$GITMOJIS_JSON"
    fi
}

main() {
    # 초기화 시도
    initialize_gitmojis
    # 초기화가 필요한 경우 종료
    if (( $? == 1 )); then
        exit 0
    fi

    # 검색 처리
    local query=""
    local is_ko=false

    if [[ "$1" == "-ko "* ]]; then
        is_ko=true
        query="${1#-ko }"
    elif [[ "$1" == "-k "* ]]; then
        is_ko=true
        query="${1#-k }"
    else
        query="$1"
    fi

    search_gitmojis "$query" "$is_ko"
}

main "$@"
