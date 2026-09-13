from datetime import date

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.exc import IntegrityError

from app.database import engine
from app.ml.classifier import classify_expense
from app.models import (
    analysis_history,
    budgets,
    categories,
    expenses,
    users,
)
from app.schemas import (
    BudgetCreate,
    ExpenseClassificationRequest,
    ExpenseCreate,
    ExpenseUpdate,
    UserCreate,
)

app = FastAPI(
    title="Smart Personal Expense & Budget Analyzer",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# ROOT
# =========================================================
@app.get("/")
def root():
    return {"message": "Expense Budget Analyzer API is running"}


# =========================================================
# HEALTH CHECK
# =========================================================
@app.get("/health")
def health():
    return {"status": "ok"}


# =========================================================
# CATEGORIES
# =========================================================
@app.get("/api/categories")
def get_categories():
    with engine.connect() as conn:
        result = conn.execute(select(categories)).mappings().all()

    return result


# =========================================================
# USERS
# =========================================================
@app.post(
    "/api/users",
    status_code=status.HTTP_201_CREATED,
)
def create_user(data: UserCreate):
    statement = (
        insert(users)
        .values(
            username=data.username,
            email=data.email,
        )
        .returning(users)
    )

    try:
        with engine.begin() as conn:
            result = conn.execute(statement).mappings().one()

        return result

    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="Email already exists",
        ) from None


# =========================================================
# CREATE EXPENSE
# =========================================================
@app.post(
    "/api/expenses",
    status_code=status.HTTP_201_CREATED,
)
def create_expense(data: ExpenseCreate):
    with engine.begin() as conn:
        # Check user
        user_exists = conn.execute(
            select(users.c.user_id).where(users.c.user_id == data.user_id)
        ).first()

        if not user_exists:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

        selected_category_id = data.category_id
        prediction = None

        # -------------------------------------------------
        # AUTOMATIC CLASSIFICATION
        # -------------------------------------------------
        if selected_category_id is None:
            prediction = classify_expense(data.description)

            predicted_category = prediction["category"]

            category_row = conn.execute(
                select(categories.c.category_id).where(
                    categories.c.category_name == predicted_category
                )
            ).first()

            if category_row is None:
                raise HTTPException(
                    status_code=500,
                    detail=("Predicted category was not found in database"),
                )

            selected_category_id = category_row[0]

        # -------------------------------------------------
        # MANUAL CATEGORY VALIDATION
        # -------------------------------------------------
        else:
            category_exists = conn.execute(
                select(categories.c.category_id).where(
                    categories.c.category_id == selected_category_id
                )
            ).first()

            if not category_exists:
                raise HTTPException(
                    status_code=404,
                    detail="Category not found",
                )

        # -------------------------------------------------
        # INSERT EXPENSE
        # -------------------------------------------------
        expense_statement = (
            insert(expenses)
            .values(
                user_id=data.user_id,
                category_id=selected_category_id,
                description=data.description,
                amount=data.amount,
                expense_date=data.expense_date,
            )
            .returning(expenses)
        )

        created_expense = conn.execute(expense_statement).mappings().one()

        # -------------------------------------------------
        # SAVE ML ANALYSIS
        # -------------------------------------------------
        if prediction is not None:
            history_statement = insert(analysis_history).values(
                expense_id=created_expense["expense_id"],
                input_text=data.description,
                predicted_category_id=(selected_category_id),
                confidence_score=prediction["confidence"],
                used_fallback=prediction["used_fallback"],
            )

            conn.execute(history_statement)

    response = dict(created_expense)

    if prediction is not None:
        response["classification"] = prediction

    return response


# =========================================================
# GET ALL EXPENSES
# =========================================================
@app.get("/api/expenses")
def get_expenses(
    category_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
):
    statement = select(expenses)

    if category_id is not None:
        statement = statement.where(expenses.c.category_id == category_id)

    if date_from is not None:
        statement = statement.where(expenses.c.expense_date >= date_from)

    if date_to is not None:
        statement = statement.where(expenses.c.expense_date <= date_to)

    with engine.connect() as conn:
        result = conn.execute(statement).mappings().all()

    return result


# =========================================================
# GET EXPENSE ANALYSIS
# =========================================================
@app.get("/api/expenses/{expense_id}/analysis")
def get_expense_analysis(
    expense_id: int,
):
    statement = (
        select(
            analysis_history.c.id,
            analysis_history.c.expense_id,
            analysis_history.c.input_text,
            categories.c.category_name.label("predicted_category"),
            analysis_history.c.confidence_score,
            analysis_history.c.used_fallback,
        )
        .join(
            categories,
            analysis_history.c.predicted_category_id == categories.c.category_id,
        )
        .where(analysis_history.c.expense_id == expense_id)
    )

    with engine.connect() as conn:
        result = conn.execute(statement).mappings().all()

    return result


# =========================================================
# GET ONE EXPENSE
# =========================================================
@app.get("/api/expenses/{expense_id}")
def get_expense(expense_id: int):
    statement = select(expenses).where(expenses.c.expense_id == expense_id)

    with engine.connect() as conn:
        result = conn.execute(statement).mappings().first()

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Expense not found",
        )

    return result


# =========================================================
# UPDATE EXPENSE
# =========================================================
@app.put("/api/expenses/{expense_id}")
def update_expense(
    expense_id: int,
    data: ExpenseUpdate,
):
    values = data.model_dump(exclude_unset=True)

    if not values:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update",
        )

    with engine.begin() as conn:
        expense_exists = conn.execute(
            select(expenses.c.expense_id).where(expenses.c.expense_id == expense_id)
        ).first()

        if not expense_exists:
            raise HTTPException(
                status_code=404,
                detail="Expense not found",
            )

        if "category_id" in values and values["category_id"] is not None:
            category_exists = conn.execute(
                select(categories.c.category_id).where(
                    categories.c.category_id == values["category_id"]
                )
            ).first()

            if not category_exists:
                raise HTTPException(
                    status_code=404,
                    detail="Category not found",
                )

        statement = (
            update(expenses)
            .where(expenses.c.expense_id == expense_id)
            .values(**values)
            .returning(expenses)
        )

        result = conn.execute(statement).mappings().one()

    return result


# =========================================================
# DELETE EXPENSE
# =========================================================
# =========================================================
# DELETE EXPENSE
# =========================================================
@app.delete("/api/expenses/{expense_id}")
def delete_expense(expense_id: int):
    with engine.begin() as conn:
        # Check expense exists
        expense_exists = conn.execute(
            select(expenses.c.expense_id).where(expenses.c.expense_id == expense_id)
        ).first()

        if expense_exists is None:
            raise HTTPException(
                status_code=404,
                detail="Expense not found",
            )

        # Delete related ML analysis first
        conn.execute(
            delete(analysis_history).where(analysis_history.c.expense_id == expense_id)
        )

        # Delete expense
        conn.execute(delete(expenses).where(expenses.c.expense_id == expense_id))

    return {
        "message": "Expense deleted successfully",
        "expense_id": expense_id,
    }


# =========================================================
# CREATE OR UPDATE BUDGET
# =========================================================
@app.post("/api/budgets")
def create_budget(data: BudgetCreate):
    with engine.begin() as conn:
        user_exists = conn.execute(
            select(users.c.user_id).where(users.c.user_id == data.user_id)
        ).first()

        if not user_exists:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

        existing_budget = (
            conn.execute(
                select(budgets).where(
                    budgets.c.user_id == data.user_id,
                    budgets.c.month == data.month,
                    budgets.c.year == data.year,
                )
            )
            .mappings()
            .first()
        )

        if existing_budget:
            statement = (
                update(budgets)
                .where(budgets.c.budget_id == existing_budget["budget_id"])
                .values(monthly_limit=(data.monthly_limit))
                .returning(budgets)
            )

        else:
            statement = (
                insert(budgets)
                .values(
                    user_id=data.user_id,
                    monthly_limit=(data.monthly_limit),
                    month=data.month,
                    year=data.year,
                )
                .returning(budgets)
            )

        result = conn.execute(statement).mappings().one()

    return result


# =========================================================
# GET MONTHLY BUDGET
# =========================================================
@app.get("/api/budgets/{user_id}")
def get_budget(
    user_id: int,
    month: int,
    year: int,
):
    statement = select(budgets).where(
        budgets.c.user_id == user_id,
        budgets.c.month == month,
        budgets.c.year == year,
    )

    with engine.connect() as conn:
        result = conn.execute(statement).mappings().first()

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Budget not found",
        )

    return result


# =========================================================
# DASHBOARD SUMMARY
# =========================================================
@app.get("/api/dashboard/summary")
def dashboard_summary(
    user_id: int,
    month: int,
    year: int,
):
    with engine.connect() as conn:
        # Get monthly budget
        budget = (
            conn.execute(
                select(budgets).where(
                    budgets.c.user_id == user_id,
                    budgets.c.month == month,
                    budgets.c.year == year,
                )
            )
            .mappings()
            .first()
        )

        if budget is None:
            raise HTTPException(
                status_code=404,
                detail="Budget not found",
            )

        monthly_limit = float(budget["monthly_limit"])

        # Get expenses
        expense_rows = (
            conn.execute(
                select(expenses).where(
                    expenses.c.user_id == user_id,
                    func.extract(
                        "month",
                        expenses.c.expense_date,
                    )
                    == month,
                    func.extract(
                        "year",
                        expenses.c.expense_date,
                    )
                    == year,
                )
            )
            .mappings()
            .all()
        )

        # Total spent
        total_spent = sum(float(expense["amount"]) for expense in expense_rows)

        # Remaining
        remaining = monthly_limit - total_spent

        # Usage
        if monthly_limit > 0:
            usage_percentage = (total_spent / monthly_limit) * 100
        else:
            usage_percentage = 0

        # Budget status
        if usage_percentage < 75:
            budget_status = "Normal"

        elif usage_percentage < 100:
            budget_status = "Warning"

        else:
            budget_status = "Exceeded"

        # Highest expense
        highest_expense = None

        if expense_rows:
            highest = max(
                expense_rows,
                key=lambda expense: float(expense["amount"]),
            )

            highest_expense = {
                "expense_id": highest["expense_id"],
                "description": highest["description"],
                "amount": float(highest["amount"]),
            }

        # Category totals
        category_query = (
            select(
                categories.c.category_name,
                func.sum(expenses.c.amount).label("total"),
            )
            .join(
                expenses,
                categories.c.category_id == expenses.c.category_id,
            )
            .where(
                expenses.c.user_id == user_id,
                func.extract(
                    "month",
                    expenses.c.expense_date,
                )
                == month,
                func.extract(
                    "year",
                    expenses.c.expense_date,
                )
                == year,
            )
            .group_by(categories.c.category_name)
        )

        category_rows = conn.execute(category_query).mappings().all()

        category_totals = [
            {
                "category": row["category_name"],
                "total": float(row["total"]),
            }
            for row in category_rows
        ]

        # Highest category
        highest_category = None

        if category_totals:
            highest_category = max(
                category_totals,
                key=lambda item: item["total"],
            )["category"]

    return {
        "budget": monthly_limit,
        "total_spent": round(
            total_spent,
            2,
        ),
        "remaining": round(
            remaining,
            2,
        ),
        "usage_percentage": round(
            usage_percentage,
            2,
        ),
        "budget_status": budget_status,
        "category_totals": category_totals,
        "highest_category": highest_category,
        "highest_expense": highest_expense,
        "number_of_expenses": len(expense_rows),
    }


# =========================================================
# CLASSIFY EXPENSE
# =========================================================
@app.post("/api/classify-expense")
def classify_expense_api(
    data: ExpenseClassificationRequest,
):
    return classify_expense(data.description)
