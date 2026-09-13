from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    func,
)

metadata = MetaData()


# =========================================================
# USERS
# =========================================================
users = Table(
    "users",
    metadata,
    Column(
        "user_id",
        Integer,
        primary_key=True,
    ),
    Column(
        "username",
        String(100),
        nullable=False,
    ),
    Column(
        "email",
        String(255),
        nullable=False,
        unique=True,
    ),
)


# =========================================================
# CATEGORIES
# =========================================================
categories = Table(
    "categories",
    metadata,
    Column(
        "category_id",
        Integer,
        primary_key=True,
    ),
    Column(
        "category_name",
        String(100),
        nullable=False,
        unique=True,
    ),
)


# =========================================================
# EXPENSES
# =========================================================
expenses = Table(
    "expenses",
    metadata,
    Column(
        "expense_id",
        Integer,
        primary_key=True,
    ),
    Column(
        "user_id",
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
    ),
    Column(
        "category_id",
        Integer,
        ForeignKey("categories.category_id"),
        nullable=True,
    ),
    Column(
        "description",
        String(255),
        nullable=False,
    ),
    Column(
        "amount",
        Numeric(10, 2),
        nullable=False,
    ),
    Column(
        "expense_date",
        Date,
        nullable=False,
    ),
    Column(
        "created_at",
        DateTime,
        server_default=func.now(),
        nullable=False,
    ),
)


# =========================================================
# BUDGETS
# =========================================================
budgets = Table(
    "budgets",
    metadata,
    Column(
        "budget_id",
        Integer,
        primary_key=True,
    ),
    Column(
        "user_id",
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
    ),
    Column(
        "monthly_limit",
        Numeric(10, 2),
        nullable=False,
    ),
    Column(
        "month",
        Integer,
        nullable=False,
    ),
    Column(
        "year",
        Integer,
        nullable=False,
    ),
)


# =========================================================
# ANALYSIS HISTORY
# =========================================================
analysis_history = Table(
    "analysis_history",
    metadata,
    Column(
        "id",
        Integer,
        primary_key=True,
    ),
    Column(
        "expense_id",
        Integer,
        ForeignKey("expenses.expense_id"),
        nullable=False,
    ),
    Column(
        "input_text",
        String(255),
        nullable=False,
    ),
    Column(
        "predicted_category_id",
        Integer,
        ForeignKey("categories.category_id"),
        nullable=False,
    ),
    Column(
        "confidence_score",
        Float,
        nullable=False,
    ),
    Column(
        "used_fallback",
        Boolean,
        nullable=False,
        server_default="false",
    ),
)
