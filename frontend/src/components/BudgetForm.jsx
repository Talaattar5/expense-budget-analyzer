import { useState } from 'react'

const API_BASE = 'http://127.0.0.1:8000'

function BudgetForm({ onBudgetUpdated }) {
  const [monthlyLimit, setMonthlyLimit] = useState('')
  const [message, setMessage] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()

    try {
      const response = await fetch(
        `${API_BASE}/api/budgets`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: 1,
            monthly_limit: Number(monthlyLimit),
            month: 9,
            year: 2026,
          }),
        },
      )

      if (!response.ok) {
        throw new Error('Budget update failed')
      }

      setMessage('Budget updated successfully.')
      setMonthlyLimit('')

      onBudgetUpdated()
    } catch {
      setMessage('Could not update budget.')
    }
  }

  return (
    <section className="card">
      <h2>Set Monthly Budget</h2>

      <form onSubmit={handleSubmit}>
        <label>
          Monthly Budget (JD)
          <input
            type="number"
            min="1"
            step="0.01"
            value={monthlyLimit}
            onChange={(event) =>
              setMonthlyLimit(event.target.value)
            }
            required
          />
        </label>

        <button type="submit">
          Save Budget
        </button>

        {message && <p>{message}</p>}
      </form>
    </section>
  )
}

export default BudgetForm