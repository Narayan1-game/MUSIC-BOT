from __future__ import annotations


def paginate(total_items: int, page_size: int, page: int) -> tuple[int, int, int]:
    total_pages = max(1, (total_items + page_size - 1) // page_size)
    page = min(max(page, 1), total_pages)
    start = (page - 1) * page_size
    end = start + page_size
    return page, start, end
