#!/bin/bash

GITMOJIS_JSON="gitmojis.json"
ICONS_DIR="icons"

# 초기화 함수
initialize_gitmojis() {
    local initialization_needed=false

    # 디렉토리 생성
    mkdir -p "$ICONS_DIR"

    # gitmojis.json이 없으면 다운로드
    if [ ! -f "$GITMOJIS_JSON" ]; then
        initialization_needed=true
        echo "{\"rerun\": 0.1, \"items\":[{\"title\":\"Downloading gitmojis.json\",\"subtitle\":\"Please wait...\",\"valid\":false}]}"
        curl -s "https://raw.githubusercontent.com/eugenejeonme/alfred-gitmoji/refs/heads/main/src/gitmojis/assets/gitmojis.json" > "$GITMOJIS_JSON"
        if [ $? -ne 0 ]; then
            echo "{\"items\":[{\"title\":\"Error\",\"subtitle\":\"Failed to download gitmojis.json\",\"valid\":false}]}"
            exit 1
        fi
        return 1
    fi

    # 아이콘 파일 체크
    while IFS= read -r name; do
        if [ ! -f "${ICONS_DIR}/${name}.png" ]; then
            initialization_needed=true
            echo "{\"rerun\": 0.1, \"items\":[{\"title\":\"Downloading icons\",\"subtitle\":\"Getting ${name}.png...\",\"valid\":false}]}"
            curl -s "https://raw.githubusercontent.com/eugenejeonme/alfred-gitmoji/refs/heads/main/src/gitmojis/assets/icons/${name}.png" > "${ICONS_DIR}/${name}.png"
            return 1
        fi
    done < <(jq -r '.[].name' "$GITMOJIS_JSON")

    # 초기화가 필요없으면 0 반환
    if [ "$initialization_needed" = false ]; then
        return 0
    fi
    return 1
}

search_gitmojis() {
    local query="$1"
    local is_ko="$2"

    query=$(echo "$query" | tr '[:upper:]' '[:lower:]')

    if [ -z "$query" ]; then
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
    if [ $? -eq 1 ]; then
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
