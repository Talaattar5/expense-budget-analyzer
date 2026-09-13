import { useState } from 'react'

const API_BASE = 'http://127.0.0.1:8000'

function ExpenseList({
  expenses,
  categories,
  onExpensesChanged,
}) {
  const [editingId, setEditingId] = useState(null)
  const [editDescription, setEditDescription] = useState('')
  const [editAmount, setEditAmount] = useState('')

  function getCategoryName(categoryId) {
    const category = categories.find(
      (item) => item.category_id === categoryId,
    )

    return category
      ? category.category_name
      : 'Unknown'
  }

  function startEdit(expense) {
    setEditingId(expense.expense_id)
    setEditDescription(expense.description)
    setEditAmount(expense.amount)
  }

  function cancelEdit() {
    setEditingId(null)
    setEditDescription('')
    setEditAmount('')
  }

  async function saveEdit(expenseId) {
    if (!editDescription.trim()) {
      alert('Description cannot be empty.')
      return
    }

    if (
      !editAmount ||
      Number(editAmount) <= 0
    ) {
      alert('Amount must be greater than 0.')
      return
    }

    try {
      const response = await fetch(
        `${API_BASE}/api/expenses/${expenseId}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            description: editDescription,
            amount: Number(editAmount),
          }),
        },
      )

      if (!response.ok) {
        throw new Error('Update failed')
      }

      cancelEdit()
      onExpensesChanged()
    } catch {
      alert('Could not update expense.')
    }
  }

  async function deleteExpense(expenseId) {
    const confirmed = window.confirm(
      'Are you sure you want to delete this expense?',
    )

    if (!confirmed) {
      return
    }

    try {
      const response = await fetch(
        `${API_BASE}/api/expenses/${expenseId}`,
        {
          method: 'DELETE',
        },
      )

      if (!response.ok) {
        throw new Error('Delete failed')
      }

      onExpensesChanged()
    } catch {
      alert('Could not delete expense.')
    }
  }

  return (
    <section className="card">
      <h2>Recent Expenses</h2>

      {expenses.length === 0 ? (
        <p>No expenses found.</p>
      ) : (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Description</th>
                <th>Category</th>
                <th>Amount</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {expenses.map((expense) => (
                <tr key={expense.expense_id}>
                  <td>
                    {editingId ===
                    expense.expense_id ? (
                      <input
                        type="text"
                        value={editDescription}
                        onChange={(event) =>
                          setEditDescription(
                            event.target.value,
                          )
                        }
                      />
                    ) : (
                      expense.description
                    )}
                  </td>

                  <td>
                    {getCategoryName(
                      expense.category_id,
                    )}
                  </td>

                  <td>
                    {editingId ===
                    expense.expense_id ? (
                      <input
                        type="number"
                        min="0.01"
                        step="0.01"
                        value={editAmount}
                        onChange={(event) =>
                          setEditAmount(
                            event.target.value,
                          )
                        }
                      />
                    ) : (
                      `${expense.amount} JD`
                    )}
                  </td>

                  <td>
                    {expense.expense_date}
                  </td>

                  <td>
                    {editingId ===
                    expense.expense_id ? (
                      <>
                        <button
                          type="button"
                          onClick={() =>
                            saveEdit(
                              expense.expense_id,
                            )
                          }
                        >
                          Save
                        </button>

                        <button
                          type="button"
                          onClick={cancelEdit}
                        >
                          Cancel
                        </button>
                      </>
                    ) : (
                      <>
                        <button
                          type="button"
                          onClick={() =>
                            startEdit(expense)
                          }
                        >
                          Edit
                        </button>

                        <button
                          type="button"
                          onClick={() =>
                            deleteExpense(
                              expense.expense_id,
                            )
                          }
                        >
                          Delete
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}

export default ExpenseList