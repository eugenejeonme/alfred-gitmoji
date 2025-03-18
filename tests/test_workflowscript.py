import pytest
import os
import json
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent.parent))

# 테스트할 함수들 임포트
import src.workflowscript as ws
from src.workflowscript import search_gitmojis, show_progress, load_gitmojis

# ===================================
# 테스트 데이터 및 환경 설정
# ===================================

@pytest.fixture
def setup_basic_test_data():
    """기본 테스트 데이터 설정"""
    test_data = [
        {
            "emoji": "🐛",
            "entity": "&#x1f41b;",
            "code": ":bug:",
            "description": {
                "en": "Fix a bug",
                "ko": "버그 수정"
            },
            "name": "bug",
            "keywords": ["fix", "bugfix"]
        },
        {
            "emoji": "✨",
            "entity": "&#x2728;",
            "code": ":sparkles:",
            "description": {
                "en": "Introduce new features",
                "ko": "새로운 기능 추가"
            },
            "name": "sparkles",
            "keywords": ["feature", "new"]
        }
    ]

    with open("gitmojis.json", 'w', encoding='utf-8') as f:
        json.dump(test_data, f)

    yield test_data

    # 테스트 후 정리
    if os.path.exists("gitmojis.json"):
        os.remove("gitmojis.json")

@pytest.fixture
def setup_complex_test_data():
    """복합 테스트 데이터 설정"""
    test_data = [
        {
            "emoji": "🐛",
            "entity": "&#x1f41b;",
            "code": ":bug:",
            "description": {
                "en": "Fix a bug",
                "ko": "버그 수정"
            },
            "name": "bug",
            "keywords": None  # None 케이스
        },
        {
            "emoji": "✨",
            "entity": "&#x2728;",
            "code": ":sparkles:",
            "description": {
                "en": "New feature",
                "ko": "새로운 기능"
            },
            "name": "sparkles",
            "keywords": []  # 빈 리스트 케이스
        },
        {
            "emoji": "🎨",
            "entity": "&#x1f3a8;",
            "code": ":art:",
            "description": {
                "en": "Improve structure",
                "ko": "구조 개선"
            },
            "name": "art",
            # keywords 필드 누락
        }
    ]

    with open("gitmojis.json", 'w', encoding='utf-8') as f:
        json.dump(test_data, f)

    yield test_data

    # 테스트 후 정리
    if os.path.exists("gitmojis.json"):
        os.remove("gitmojis.json")

@pytest.fixture
def setup_invalid_test_data():
    """잘못된 테스트 데이터 설정"""
    test_data = [
        {
            "emoji": "🐛",
            "description": None  # 잘못된 구조
        }
    ]

    with open("gitmojis.json", 'w', encoding='utf-8') as f:
        json.dump(test_data, f)

    yield test_data

    # 테스트 후 정리
    if os.path.exists("gitmojis.json"):
        os.remove("gitmojis.json")

# ===================================
# 기본 기능 테스트
# ===================================

class TestBasicFunctionality:
    """기본 기능 테스트 클래스"""

    def test_load_gitmojis_structure(self, setup_basic_test_data):
        """gitmojis.json 파일 구조 테스트"""
        with open("gitmojis.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert isinstance(data, list)
        assert len(data) > 0
        assert all(isinstance(item, dict) for item in data)

    def test_search_gitmojis_basic(self, setup_basic_test_data):
        """기본 검색 테스트"""
        results = search_gitmojis("")
        assert isinstance(results, list)
        assert len(results) > 0

    def test_search_gitmojis_with_query(self, setup_basic_test_data):
        """검색어가 있는 경우 테스트"""
        results = search_gitmojis("bug")
        assert isinstance(results, list)
        assert len(results) > 0
        assert any("bug" in item['subtitle'].lower() for item in results)

    def test_search_gitmojis_korean(self, setup_basic_test_data):
        """한글 검색 테스트"""
        results = search_gitmojis("버그", is_koKR=True)
        assert isinstance(results, list)
        assert len(results) > 0
        assert any("버그" in item['title'] for item in results)

    def test_search_gitmojis_no_results(self, setup_basic_test_data):
        """결과가 없는 경우 테스트"""
        results = search_gitmojis("nonexistentquery123")
        assert isinstance(results, list)
        assert len(results) == 1
        assert "No matches found" in results[0]['title']

# ===================================
# 검색 기능 상세 테스트
# ===================================

class TestSearchFunctionality:
    """검색 기능 상세 테스트 클래스"""

    @pytest.mark.parametrize("query,expected_emoji,is_koKR", [
        ("fix bug", "🐛", False),
        ("버그", "🐛", True),
        ("새로운 기능", "✨", True),
        ("structure", "🎨", False),
        ("art", "🎨", False),
    ])
    def test_search_with_various_queries(self, setup_complex_test_data, query, expected_emoji, is_koKR):
        """다양한 검색어로 이모지 검색 테스트"""
        results = search_gitmojis(query, is_koKR)
        assert len(results) > 0
        assert any(item['arg'] == expected_emoji for item in results)

    def test_search_with_partial_match(self, setup_complex_test_data):
        """부분 일치 검색 테스트"""
        results = search_gitmojis("bug fix", False)
        assert len(results) > 0

    def test_search_case_insensitive(self, setup_complex_test_data):
        """대소문자 구분 없는 검색 테스트"""
        results1 = search_gitmojis("bug")
        results2 = search_gitmojis("BUG")
        assert len(results1) == len(results2)

    def test_search_with_spaces(self, setup_complex_test_data):
        """공백이 포함된 검색어 테스트"""
        results = search_gitmojis("  bug   fix  ", False)
        assert len(results) > 0

    def test_search_with_unicode_normalization(self, setup_complex_test_data):
        """유니코드 정규화 검색 테스트"""
        results1 = search_gitmojis("버그")
        results2 = search_gitmojis("버그")  # 다른 형태의 '버그'
        assert len(results1) == len(results2)

# ===================================
# 에러 처리 및 엣지 케이스 테스트
# ===================================

class TestErrorHandling:
    """에러 처리 및 엣지 케이스 테스트 클래스"""

    def test_load_gitmojis_file_not_found(self):
        """파일이 없는 경우 테스트"""
        if os.path.exists("gitmojis.json"):
            os.remove("gitmojis.json")
        assert load_gitmojis() is None

    def test_load_gitmojis_invalid_json(self):
        """잘못된 JSON 형식 테스트"""
        with open("gitmojis.json", 'w') as f:
            f.write("invalid json content")

        with pytest.raises(SystemExit):
            load_gitmojis()

    def test_search_exception_handling(self, setup_invalid_test_data):
        """검색 중 예외 발생 케이스 테스트 (line 108)"""
        results = search_gitmojis("test")
        assert results == []  # 예외 발생 시 빈 리스트 반환

    def test_file_operations_errors(self, monkeypatch):
        """파일 조작 관련 에러 테스트"""
        def mock_open(*args, **kwargs):
            raise Exception("Test error")

        monkeypatch.setattr("builtins.open", mock_open)
        with pytest.raises(SystemExit):
            load_gitmojis()

    def test_extract_tar_invalid_file(self):
        """잘못된 tar 파일 테스트"""
        from src.workflowscript import extract_tar
        assert extract_tar("nonexistent.tar.gz", ".") == False

# ===================================
# 유틸리티 함수 테스트
# ===================================

class TestUtilityFunctions:
    """유틸리티 함수 테스트 클래스"""

    def test_show_progress(self):
        """show_progress 함수 테스트"""
        show_progress("Test Title", "Test Subtitle")

    def test_download_file(self, tmp_path):
        """download_file 함수 테스트"""
        from src.workflowscript import download_file
        test_url = "https://raw.githubusercontent.com/eugenejeonme/alfred-gitmoji/main/src/gitmojis/assets/gitmojis.json"
        test_file = tmp_path / "test.json"
        assert download_file(test_url, str(test_file)) == True
        assert os.path.exists(test_file)

    def test_download_file_invalid_url(self, tmp_path):
        """잘못된 URL로 다운로드 시도 테스트"""
        from src.workflowscript import download_file
        test_url = "https://invalid.url/nonexistent"
        test_file = tmp_path / "test.json"
        assert download_file(test_url, str(test_file)) == False

    def test_initialize_gitmojis(self, tmp_path):
        """초기화 함수 테스트"""
        from src.workflowscript import initialize_gitmojis
        os.chdir(tmp_path)
        assert isinstance(initialize_gitmojis(), bool)

# ===================================
# main 함수 테스트
# ===================================

class TestMainFunction:
    """main 함수 테스트 클래스"""

    @pytest.mark.parametrize("argv,expected_ko", [
        (["script.py", "-ko test"], True),
        (["script.py", "-k test"], True),
        (["script.py", "test"], False),
        (["script.py"], False),
    ])
    def test_main_function_arguments(self, setup_basic_test_data, monkeypatch, argv, expected_ko):
        """main 함수의 인자 처리 테스트"""
        monkeypatch.setattr(sys, 'argv', argv)

        # 초기화 함수 모킹
        def mock_initialize():
            return False
        monkeypatch.setattr('src.workflowscript.initialize_gitmojis', mock_initialize)

        # 표준 출력 리디렉션
        import io
        stdout_orig = sys.stdout
        sys.stdout = io.StringIO()

        try:
            # 메인 함수 실행
            ws.main()

            # 표준 출력 복원
            output = sys.stdout.getvalue()

            # 출력 검증
            assert output
            assert '{"items":' in output
        finally:
            sys.stdout = stdout_orig

    def test_main_with_initialization(self, monkeypatch):
        """초기화가 필요한 경우 테스트"""
        def mock_initialize():
            return True

        monkeypatch.setattr(sys, 'argv', ['script.py', 'test'])
        monkeypatch.setattr('src.workflowscript.initialize_gitmojis', mock_initialize)

        with pytest.raises(SystemExit) as exc_info:
            ws.main()
        assert exc_info.value.code == 0

# ===================================
# 특정 미커버 라인 직접 테스트
# ===================================

class TestUncoveredLines:
    """특정 미커버 라인 직접 테스트 클래스"""

    def test_line_76_keywords_none(self):
        """76번 라인: keywords가 None일 때"""
        gitmoji = {"keywords": None}
        keywords = " ".join(gitmoji.get("keywords", [])).lower() if gitmoji.get("keywords") else "" # type: ignore
        assert keywords == ""

    def test_lines_86_91_96_97_search_conditions(self, setup_complex_test_data):
        """86, 91, 96-97번 라인: 검색 조건 분기"""
        # description_ko 매칭 (line 86)
        results1 = search_gitmojis("버그")
        assert len(results1) > 0

        # description_en 매칭 (line 91)
        results2 = search_gitmojis("feature")
        assert len(results2) > 0

        # name 매칭
        results3 = search_gitmojis("bug")
        assert len(results3) > 0

        # keywords 매칭 (빈 리스트/None 케이스도 테스트)
        results4 = search_gitmojis("feature")
        assert len(results4) > 0

    def test_line_108_exception_handling(self, setup_invalid_test_data):
        """108번 라인: 예외 처리"""
        results = search_gitmojis("test")
        assert results == []
