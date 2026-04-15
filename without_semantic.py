# without_semantic.py
import duckdb, ollama

con = duckdb.connect("duckdb/poc.db", read_only=False)


# Give the LLM the raw schema — just table names and columns, no business logic
def get_raw_schema():
    schema = {}
    for table in ['raw_orders', 'raw_customers', 'raw_products']:
        cols = con.execute(f"PRAGMA table_info({table})").fetchall()
        schema[table] = [c[1] for c in cols]
    return schema

def ask_without_semantic(question: str) -> dict:
    schema = get_raw_schema()
    schema_text = "\n".join(
        f"Table: {t}\nColumns: {', '.join(cols)}"
        for t, cols in schema.items()
    )

    prompt = f"""You are a SQL expert. Given these raw database tables, write a DuckDB SQL query to answer the question.
Return ONLY the SQL query, nothing else.

Schema:
{schema_text}

Question: {question}

SQL:"""

    response = ollama.chat(model='llama3.2:3b', messages=[
        {'role': 'user', 'content': prompt}
    ])

    sql = response['message']['content'].strip()
    sql = sql.replace('```sql', '').replace('```', '').strip()

    try:
        result = con.execute(sql).fetchdf()
        return {"sql": sql, "result": result, "error": None}
    except Exception as e:
        return {"sql": sql, "result": None, "error": str(e)}