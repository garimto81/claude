"""
Archive MAM - Media Asset Management for Staff/Editor

병렬 개발을 위한 모듈 구조:
- asset/   : Worker A - 자산 관리
- tag/     : Worker B - 태그 시스템
- search/  : Worker C - 검색
- workflow/: Worker D - 클리핑, 작업 큐
- production/: Worker E - EDL, 컬렉션
- admin/   : Worker F - 관리 도구
"""
