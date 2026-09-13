function BudgetSummary({ summary }) {
  if (!summary) {
    return <p>Loading budget summary...</p>
  }

  return (
    <section className="card">
      <h2>Monthly Budget</h2>

      <div className="summary-grid">
        <div>
          <h3>Budget</h3>
          <p>{summary.budget} JD</p>
        </div>

        <div>
          <h3>Spent</h3>
          <p>{summary.total_spent} JD</p>
        </div>

        <div>
          <h3>Remaining</h3>
          <p>{summary.remaining} JD</p>
        </div>

        <div>
          <h3>Usage</h3>
          <p>{summary.usage_percentage}%</p>
        </div>

        <div>
          <h3>Status</h3>
          <p>{summary.budget_status}</p>
        </div>

        <div>
          <h3>Transactions</h3>
          <p>{summary.number_of_expenses}</p>
        </div>
      </div>
    </section>
  )
}

export default BudgetSummary