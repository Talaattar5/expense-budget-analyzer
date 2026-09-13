# Smart Personal Expense & Budget Analyzer

A full-stack personal expense management application that allows users to record expenses, automatically classify transactions using machine learning, manage a monthly budget, and analyze spending through a dashboard.

The project was developed using React, FastAPI, PostgreSQL, SQLAlchemy Core, Alembic, and Scikit-learn.

---

## Features

- Add personal expenses
- View all expenses
- Edit expenses
- Delete expenses
- Filter expenses by category and date
- Automatically categorize expense descriptions
- Machine-learning expense classification
- Keyword fallback classification
- Monthly budget management
- Budget status calculation
- Spending analysis by category
- Highest expense detection
- Most-used spending category
- Monthly spending summary
- PostgreSQL database
- SQLAlchemy Core database operations
- Alembic database migrations
- Responsive React frontend
- FastAPI REST API

---

## Technology Stack

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy Core
- PostgreSQL
- Alembic
- Scikit-learn
- Pandas
- Joblib
- Ruff

### Frontend

- React
- Vite
- JavaScript
- CSS
- Fetch API

### Machine Learning

- TF-IDF Vectorization
- Logistic Regression
- Keyword-based fallback classification

---

## Project Architecture

```text
React Frontend
      |
      v
FastAPI Backend
      |
      +----------------------+
      |                      |
      v                      v
Expense Classification   Budget Analysis
      |
      v
TF-IDF + Logistic Regression
      |
      v
SQLAlchemy Core
      |
      v
PostgreSQL