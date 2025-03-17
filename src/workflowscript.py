#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import tarfile
import urllib.request
import unicodedata
from pathlib import Path

# 현재 작업 디렉토리 기준
GITMOJIS_JSON = "gitmojis.json"
ICONS_DIR = "icons"
ICONS_TAR = "icons.tar.gz"
BASE_URL = "https://raw.githubusercontent.com/eugenejeonme/alfred-gitmoji/refs/heads/main/src/gitmojis/assets"

def show_progress(title, subtitle):
    """진행 상태를 보여주는 함수"""
    print(json.dumps({
        "rerun": 0.1,  # 0.1초 후 다시 실행
        "items": [{
            "title": title,
            "subtitle": subtitle,
            "valid": False
        }]
    }, ensure_ascii=False))
    sys.stdout.flush()

def download_file(url, filename):
    """파일 다운로드 함수"""
    try:
        urllib.request.urlretrieve(url, filename)
        return True
    except Exception as e:
        show_progress("Error", f"Failed to download {filename}: {str(e)}")
        return False

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

def extract_tar(tar_file, extract_path):
    """tar 파일 압축해제 함수"""
    try:
        with tarfile.open(tar_file, 'r:gz') as tar:
            tar.extractall(path=extract_path)
        return True
    except Exception as e:
        show_progress("Error", f"Failed to extract {tar_file}: {str(e)}")
        return False

def initialize_gitmojis():
    """초기화 함수: 필요한 파일들을 다운로드합니다."""
    needs_initialization = False

    # 작업 디렉토리 생성 (exist_ok 옵션으로 이미 존재하면 무시함)
    os.makedirs(ICONS_DIR, exist_ok=True)

    # gitmojis.json 파일이 없으면 다운로드
    if not os.path.exists(GITMOJIS_JSON):
        needs_initialization = True
        show_progress("Downloading", "Getting gitmojis.json...")
        json_url = f"{BASE_URL}/gitmojis.json"
        if not download_file(json_url, GITMOJIS_JSON):
            return True

    # icons 디렉토리가 비어있는지 확인
    if not os.path.exists(ICONS_DIR) or not any(Path(ICONS_DIR).iterdir()):
        needs_initialization = True
        show_progress("Downloading", "Getting icons.tar.gz...")

        # tar 파일 다운로드
        tar_url = f"{BASE_URL}/icons.tar.gz"
        if not download_file(tar_url, ICONS_TAR):
            return True

        # tar 파일 압축해제
        show_progress("Extracting", "Unpacking icons...")
        if not extract_tar(ICONS_TAR, "."):
            return True

        # 압축 해제 후 tar 파일 삭제
        try:
            os.remove(ICONS_TAR)
        except:
            pass  # 삭제 실패해도 진행

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

            # keywords가 None인 경우 빈 문자열 처리
            keywords = " ".join(gitmoji.get("keywords", [])).lower() if gitmoji.get("keywords") else ""

            # 각 검색어에 대해
            matches_all_terms = True
            for term in query_terms:
                term_lower = term.lower()  # 영문 검색을 위한 소문자 변환
                # 한글 검색은 원본 term 사용, 영문 검색은 소문자 변환된 term 사용
                if not (term in description_ko or  # 한글 검색
                        term_lower in description_en or  # 영문 검색
                        term_lower in name or  # 이름 검색
                        term_lower in keywords or # 영문 키워드 검색
                        term in keywords):  # 한글 키워드 검색
                    matches_all_terms = False
                    break

            if not query or matches_all_terms:
                icon_path = f"./{ICONS_DIR}/{gitmoji['name']}.png"
                results.append({
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
                            "subtitle": f"Copy \"{gitmoji['code']}\" to clipboard",
                            "arg": gitmoji['code'],
                            "text": {
                                "copy": gitmoji['code'],
                                "largetype": f"Copy \"{gitmoji['code']}\" to clipboard",
                            },
                            "valid": True,
                        },
                        "shift": {
                            "subtitle": f"Copy \"{gitmoji['entity']}\" to clipboard",
                            "arg": gitmoji['entity'],
                            "text": {
                                "copy": gitmoji['entity'],
                                "largetype": f"Copy \"{gitmoji['entity']}\" to clipboard",
                            },
                            "valid": True,
                        },
                    },
                    "icon": {
                        "path": icon_path if os.path.exists(icon_path) else ""
                    },
                    "valid": True,
                })

        return results if results else [{"title": "No matches found", "subtitle": f"Try a different search term, {query_terms}"}]
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
    print(json.dumps({"items": results}, ensure_ascii=False))
    sys.stdout.flush()

if __name__ == "__main__":
    main()
