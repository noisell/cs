import enum
from typing import Any
from pydantic import BaseModel, Field


class StatusTypes(enum.Enum):
    success = "success"
    error = "error"


class TokenPayload(BaseModel):
    user_id: int
    banned: bool


class AdminPayload(BaseModel):
    user_id: int
    level: int


class ErrorResponse(BaseModel):
    detail: str = Field(description="Описание ошибки", title="")


def get_error_responses() -> dict[int, dict[str, Any]]:
    return {
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "schema": ErrorResponse.schema()
                }
            }
        },
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "schema": ErrorResponse.schema()
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "schema": ErrorResponse.schema()
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "schema": ErrorResponse.schema()
                }
            }
        }
    }