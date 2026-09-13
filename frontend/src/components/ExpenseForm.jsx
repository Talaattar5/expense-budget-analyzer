import { useState } from 'react'

const API_BASE = 'http://127.0.0.1:8000'

function ExpenseForm({ onExpenseCreated }) {
  const [description, setDescription] = useState('')
  const [amount, setAmount] = useState('')
  const [expenseDate, setExpenseDate] = useState('')
  const [prediction, setPrediction] = useState(null)
  const [message, setMessage] = useState('')

  async function handleAutoCategorize() {
    if (!description.trim()) {
      setMessage('Enter a description first.')
      return
    }

    try {
      const response = await fetch(
        `${API_BASE}/api/classify-expense`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            description,
          }),
        },
      )

      if (!response.ok) {
        throw new Error('Classification failed')
      }

      const data = await response.json()

      setPrediction(data)
      setMessage('')
    } catch {
      setMessage('Could not classify expense.')
    }
  }

  async function handleSubmit(event) {
    event.preventDefault()

    try {
      const response = await fetch(
        `${API_BASE}/api/expenses`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: 1,
            category_id: null,
            description,
            amount: Number(amount),
            expense_date: expenseDate,
          }),
        },
      )

      if (!response.ok) {
        throw new Error('Expense creation failed')
      }

      setDescription('')
      setAmount('')
      setExpenseDate('')
      setPrediction(null)
      setMessage('Expense added successfully.')

      onExpenseCreated()
    } catch {
      setMessage('Could not add expense.')
    }
  }

  return (
    <section className="card">
      <h2>Add Expense</h2>

      <form onSubmit={handleSubmit}>
        <label>
          Description
          <input
            type="text"
            value={description}
            onChange={(event) =>
              setDescription(event.target.value)
            }
            required
          />
        </label>

        <button
          type="button"
          onClick={handleAutoCategorize}
        >
          Auto Categorize
        </button>

        {prediction && (
          <div className="prediction">
            <strong>Predicted Category:</strong>{' '}
            {prediction.category}

            <br />

            <strong>Confidence:</strong>{' '}
            {(prediction.confidence * 100).toFixed(1)}%
          </div>
        )}

        <label>
          Amount
          <input
            type="number"
            step="0.01"
            min="0.01"
            value={amount}
            onChange={(event) =>
              setAmount(event.target.value)
            }
            required
          />
        </label>

        <label>
          Date
          <input
            type="date"
            value={expenseDate}
            onChange={(event) =>
              setExpenseDate(event.target.value)
            }
            required
          />
        </label>

        <button type="submit">
          Add Expense
        </button>

        {message && <p>{message}</p>}
      </form>
    </section>
  )
}

export default ExpenseForm