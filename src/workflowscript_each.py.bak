#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import urllib.request
import unicodedata

# 현재 작업 디렉토리 기준
GITMOJIS_JSON = "gitmojis.json"
ICONS_DIR = "icons"

def show_progress(title, subtitle):
    """진행 상태를 보여주는 함수"""
    print(json.dumps({
        "rerun": 0.1,  # 0.1초 후 다시 실행
        "items": [{
            "title": title,
            "subtitle": subtitle,
            "valid": False
        }]
    }))
    sys.stdout.flush()

def load_gitmojis():
    """gitmojis.json 파일을 로드합니다."""
    try:
        with open(GITMOJIS_JSON, "r", encoding="utf-8") as f:
            return json.loads(f.read())
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        show_progress("Error", "Invalid JSON format")
        sys.exit(1)
    except Exception as e:
        show_progress("Error", f"Error loading file: {str(e)}")
        sys.exit(1)

def initialize_gitmojis():
    """초기화 함수: 필요한 파일들을 다운로드합니다."""
    needs_initialization = False

    # icons 폴더가 없으면 생성
    if not os.path.exists(ICONS_DIR):
        os.makedirs(ICONS_DIR)

    # gitmojis.json 파일이 없으면 다운로드
    if not os.path.exists(GITMOJIS_JSON):
        needs_initialization = True
        show_progress("Downloading", "Getting gitmojis.json...")
        try:
            url = "https://raw.githubusercontent.com/eugenejeonme/alfred-gitmoji/refs/heads/main/src/gitmojis/assets/gitmojis.json"
            urllib.request.urlretrieve(url, GITMOJIS_JSON)
            return True
        except Exception as e:
            show_progress("Error", f"Failed to download gitmojis.json: {str(e)}")
            return True

    # gitmojis.json 읽기
    gitmojis = load_gitmojis()
    if not gitmojis:
        return True

    # 각 gitmoji의 아이콘 다운로드
    for gitmoji in gitmojis:
        emoji_name = gitmoji['name']
        icon_path = os.path.join(ICONS_DIR, f"{emoji_name}.png")

        if not os.path.exists(icon_path):
            needs_initialization = True
            show_progress("Downloading", f"Getting icon: {emoji_name}.png")
            try:
                emoji_url = f"https://raw.githubusercontent.com/eugenejeonme/alfred-gitmoji/refs/heads/main/src/gitmojis/assets/icons/{emoji_name}.png"
                urllib.request.urlretrieve(emoji_url, icon_path)
                return True
            except Exception as e:
                show_progress("Error", f"Failed to download icon {emoji_name}: {str(e)}")
                return True

    return needs_initialization

def search_gitmojis(query, is_koKR=False):
    """gitmojis 검색 함수"""
    query_terms = [unicodedata.normalize('NFC', term) for term in query.split()]
    gitmojis = load_gitmojis()
    results = []

    if gitmojis is None:
      return []

    try:
        for gitmoji in gitmojis:
            description_en = gitmoji["description"]["en"].lower()
            description_ko = unicodedata.normalize('NFC', gitmoji["description"]["ko"]) # description_ko 정규화
            name = gitmoji["name"].lower()
            keywords = " ".join(gitmoji.get("keywords", [])).lower() if gitmoji.get("keywords") else ""

            matches_all_terms = all(
                any(term in text for text in [description_en, description_ko, name, keywords] if text)
                for term in query_terms
            )

            if not query or matches_all_terms:
                icon_path = f"./{ICONS_DIR}/{gitmoji['name']}.png"
                results.append({
                    "valid": True,
                    "uid": f"{'ko' if is_koKR else 'en'}_{gitmoji['name']}",
                    "title": gitmoji['description']['ko'] if is_koKR else gitmoji['description']['en'],
                    "subtitle": f"{gitmoji['code']} - {gitmoji['description']['en'] if is_koKR else gitmoji['description']['ko']}",
                    "arg": gitmoji['emoji'],
                    "text": {
                        "copy": gitmoji['emoji'],
                        "largetype": f"{gitmoji['emoji']} ({gitmoji['code']}) - {gitmoji['description']['ko']}"
                    },
                    "mods": {
                        "alt": {
                            "valid": True,
                            "subtitle": f"Copy \"{gitmoji['code']}\" to clipboard",
                            "arg": gitmoji['code'],
                            "text": {
                                "copy": gitmoji['code'],
                                "largetype": f"Copy \"{gitmoji['code']}\" to clipboard",
                            },
                        },
                        "shift": {
                            "valid": True,
                            "subtitle": f"Copy \"{gitmoji['entity']}\" to clipboard",
                            "arg": gitmoji['entity'],
                            "text": {
                                "copy": gitmoji['entity'],
                                "largetype": f"Copy \"{gitmoji['entity']}\" to clipboard",
                            },
                        },
                    },
                    "icon": {
                        "path": icon_path if os.path.exists(icon_path) else ""
                    },
                })

        return results if results else [{"title": "No matches found", "subtitle": "Try a different search term"}]
    except Exception as e:
        show_progress("Error", str(e))
        return []

def main():
    """메인 함수"""
    # 초기화가 필요한지 확인
    if initialize_gitmojis():
        sys.exit(0)

    # 검색어 처리
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    is_koKR = False

    if query.startswith("-ko "):
        is_koKR = True
        query = query[4:]
    elif query.startswith("-k "):
        is_koKR = True
        query = query[3:]

    # 검색 실행 및 결과 반환
    results = search_gitmojis(query, is_koKR)
    print(json.dumps({"items": results}))
    sys.stdout.flush()

if __name__ == "__main__":
    main()
