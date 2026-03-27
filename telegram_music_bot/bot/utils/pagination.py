from __future__ import annotations


def paginate(items: list, page: int, page_size: int) -> tuple[list, int, int]:
    if page_size <= 0:
        page_size = 10
    total_pages = max(1, (len(items) + page_size - 1) // page_size)
    page = min(max(1, page), total_pages)
    start = (page - 1) * page_size
    return items[start : start + page_size], page, total_pages
