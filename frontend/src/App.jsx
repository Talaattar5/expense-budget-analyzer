import { useEffect, useState } from 'react'

import BudgetForm from './components/BudgetForm'
import BudgetSummary from './components/BudgetSummary'
import CategoryAnalysis from './components/CategoryAnalysis'
import ExpenseForm from './components/ExpenseForm'
import ExpenseList from './components/ExpenseList'

const API_BASE = 'http://127.0.0.1:8000'

async function fetchDashboardData() {
  const [
    categoriesResponse,
    expensesResponse,
    summaryResponse,
  ] = await Promise.all([
    fetch(`${API_BASE}/api/categories`),
    fetch(`${API_BASE}/api/expenses`),
    fetch(
      `${API_BASE}/api/dashboard/summary?user_id=1&month=9&year=2026`,
    ),
  ])

  if (
    !categoriesResponse.ok ||
    !expensesResponse.ok ||
    !summaryResponse.ok
  ) {
    throw new Error('Could not load dashboard data')
  }

  const categories = await categoriesResponse.json()
  const expenses = await expensesResponse.json()
  const summary = await summaryResponse.json()

  return {
    categories,
    expenses,
    summary,
  }
}

function App() {
  const [summary, setSummary] = useState(null)
  const [expenses, setExpenses] = useState([])
  const [categories, setCategories] = useState([])
  const [error, setError] = useState('')

  async function loadData() {
    try {
      const data = await fetchDashboardData()

      setCategories(data.categories)
      setExpenses(data.expenses)
      setSummary(data.summary)
      setError('')
    } catch {
      setError('Could not connect to the backend.')
    }
  }

  useEffect(() => {
    fetchDashboardData()
      .then((data) => {
        setCategories(data.categories)
        setExpenses(data.expenses)
        setSummary(data.summary)
        setError('')
      })
      .catch(() => {
        setError('Could not connect to the backend.')
      })
  }, [])

  return (
    <div className="app">
      <header>
        <h1>
          Smart Personal Expense & Budget Analyzer
        </h1>

        <p>
          Track expenses, manage your budget,
          and understand your spending.
        </p>
      </header>

      <main>
        {error && (
          <div className="error">
            {error}
          </div>
        )}

        <BudgetSummary summary={summary} />

        <BudgetForm
          onBudgetUpdated={loadData}
        />

        <ExpenseForm
          onExpenseCreated={loadData}
        />

        <CategoryAnalysis
          summary={summary}
        />

        <ExpenseList
          expenses={expenses}
          categories={categories}
          onExpensesChanged={loadData}
        />
      </main>
    </div>
  )
}

export default App