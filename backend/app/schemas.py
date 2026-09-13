from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(
        min_length=2,
        max_length=100,
    )
    email: str = Field(
        min_length=5,
        max_length=255,
    )


class ExpenseCreate(BaseModel):
    user_id: int
    category_id: int | None = None
    description: str = Field(
        min_length=1,
        max_length=255,
    )
    amount: Decimal = Field(gt=0)
    expense_date: date


class ExpenseUpdate(BaseModel):
    category_id: int | None = None
    description: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    amount: Decimal | None = Field(
        default=None,
        gt=0,
    )
    expense_date: date | None = None


class BudgetCreate(BaseModel):
    user_id: int = Field(gt=0)
    monthly_limit: Decimal = Field(gt=0)
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000)


class ExpenseClassificationRequest(BaseModel):
    description: str = Field(
        min_length=1,
        max_length=255,
    )
