function CategoryAnalysis({ summary }) {
  if (!summary) {
    return null
  }

  return (
    <section className="card">
      <h2>Category Analysis</h2>

      {summary.category_totals.length === 0 ? (
        <p>No category data available.</p>
      ) : (
        <div>
          {summary.category_totals.map((item) => (
            <div
              className="category-row"
              key={item.category}
            >
              <span>{item.category}</span>

              <strong>
                {item.total} JD
              </strong>
            </div>
          ))}
        </div>
      )}

      <hr />

      <p>
        <strong>Highest Category:</strong>{' '}
        {summary.highest_category || 'None'}
      </p>

      {summary.highest_expense && (
        <p>
          <strong>Highest Expense:</strong>{' '}
          {summary.highest_expense.description}
          {' - '}
          {summary.highest_expense.amount} JD
        </p>
      )}
    </section>
  )
}

export default CategoryAnalysis