from collections.abc import Callable
from typing import Any, Literal, TypeVar, overload

from app.exceptions.base import AppError

T = TypeVar("T")


class NotFoundError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__("MISSING_ITEM", message, 404)


class MockTable[T]:
    def __init__(self, table: list[T] | None = None) -> None:
        self.table: list[T] = table or []

    def _match(self, item: T, filters: dict[str, Any]) -> bool:
        return all(getattr(item, k, None) == v for k, v in filters.items())

    def insert(self, item: T) -> T:
        self.table.append(item)
        return item

    def all(self) -> list[T]:
        return self.table

    @overload
    def first(self, *, raise_if_missing: Literal[False] = False) -> T | None: ...
    @overload
    def first(self, *, raise_if_missing: Literal[True]) -> T: ...

    def first(self, *, raise_if_missing: bool = False) -> T | None:
        if self.table:
            return self.table[0]

        if raise_if_missing:
            raise NotFoundError("No items found")

        return None

    @overload
    def get(
        self,
        filters: dict[str, Any],
        *,
        raise_if_missing: Literal[False] = False,
    ) -> T | None: ...

    @overload
    def get(
        self,
        filters: dict[str, Any],
        *,
        raise_if_missing: Literal[True] = True,
    ) -> T: ...

    def get(
        self,
        filters: dict[str, Any],
        *,
        raise_if_missing: bool = False,
    ) -> T | None:
        """
        Get single item matching fields
        Example:
            users.get(id=1)
            users.get(email="john@example.com")
        """
        for item in self.table:
            if self._match(item, filters):
                return item

        if raise_if_missing:
            raise NotFoundError(f"Item not found for {filters}")

        return None

    def filter(self, filters: dict[str, Any]) -> list[T]:
        """
        Filter items matching fields
        Example:
            users.filter(role="admin")
        """
        return [item for item in self.table if self._match(item, filters)]

    def where(self, condition: Callable[[T], bool]) -> list[T]:
        """
        Custom filter function
        Example:
            users.where(lambda u: u.age > 18)
        """
        return [item for item in self.table if condition(item)]

    def exists(self, filters: dict[str, Any]) -> bool:
        return any(self._match(item, filters) for item in self.table)

    def update(self, filters: dict[str, Any], values: dict[str, Any]) -> T | None:
        """
        Update first matched item
        Example:
            users.update(
                {"id": 1},
                {"name": "Updated Name"}
            )
        """
        item = self.get(filters)

        if not item:
            return None

        for key, value in values.items():
            setattr(item, key, value)

        return item

    @overload
    def update_by(
        self,
        filters: dict[str, Any],
        values: dict[str, Any],
        *,
        raise_if_missing: Literal[False] = False,
    ) -> T | None: ...

    @overload
    def update_by(
        self,
        filters: dict[str, Any],
        values: dict[str, Any],
        *,
        raise_if_missing: Literal[True] = True,
    ) -> T: ...

    def update_by(
        self,
        filters: dict[str, Any],
        values: dict[str, Any],
        *,
        raise_if_missing: bool = False,
    ) -> T | None:
        if not raise_if_missing:
            item = self.get(filters, raise_if_missing=False)
        else:
            item = self.get(filters, raise_if_missing=True)

        if item is None:
            return None

        for key, value in values.items():
            setattr(item, key, value)

        return item

    def update_many(self, filters: dict[str, Any], values: dict[str, Any]) -> list[T]:
        """
        Update all matching items
        """
        items = self.filter(filters)

        for item in items:
            for key, value in values.items():
                setattr(item, key, value)

        return items

    def delete(self, filters: dict[str, Any]) -> T | None:
        """
        Delete first matched item
        """
        item = self.get(filters)

        if item:
            self.table.remove(item)

        return item

    @overload
    def delete_by(
        self,
        filters: dict[str, Any],
        *,
        raise_if_missing: Literal[False] = False,
    ) -> T | None: ...

    @overload
    def delete_by(
        self,
        filters: dict[str, Any],
        *,
        raise_if_missing: Literal[True] = True,
    ) -> T: ...

    def delete_by(
        self,
        filters: dict[str, Any],
        *,
        raise_if_missing: bool = False,
    ) -> T | None:
        if not raise_if_missing:
            item = self.get(filters, raise_if_missing=False)
        else:
            item = self.get(filters, raise_if_missing=True)

        if item:
            self.table.remove(item)

        return item

    def delete_many(self, filters: dict[str, Any]) -> list[T]:
        """
        Delete all matching items
        """
        items = self.filter(filters)

        for item in list(items):
            self.table.remove(item)

        return items

    def clear(self) -> None:
        self.table.clear()
