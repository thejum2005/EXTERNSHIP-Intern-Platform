from dataclasses import dataclass


@dataclass
class Page:
    items: list
    page: int
    per_page: int
    total: int

    @property
    def pages(self) -> int:
        if self.per_page <= 0:
            return 1
        return max(1, (self.total + self.per_page - 1) // self.per_page)

    @property
    def has_prev(self) -> bool:
        return self.page > 1

    @property
    def has_next(self) -> bool:
        return self.page < self.pages

    @property
    def prev_num(self) -> int:
        return max(1, self.page - 1)

    @property
    def next_num(self) -> int:
        return min(self.pages, self.page + 1)


def paginate(query, page: int, per_page: int) -> Page:
    page = max(1, int(page or 1))
    per_page = max(1, int(per_page or 10))
    total = query.count()
    items = query.limit(per_page).offset((page - 1) * per_page).all()
    return Page(items=items, page=page, per_page=per_page, total=total)

