import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field


class Base(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def touch(self) -> None:
        self.updated_at = datetime.now(UTC)
