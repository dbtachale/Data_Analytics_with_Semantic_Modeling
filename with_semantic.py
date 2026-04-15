# with_semantic.py
import duckdb, ollama
import yaml

con = duckdb.connect("duckdb/poc.db", read_only=False)

def load_semantic_context():
    try:
        with open("dbt_project/metrics/revenue.yml", "r") as f:
            revenue_metrics = yaml.safe_load(f)
        
        metrics_desc = ""
        for metric in revenue_metrics.get("metrics", []):
            metrics_desc += f"- {metric['name']}: {metric.get('description', '')}\n"
            metrics_desc += f"  Calculation: {metric['calculation_method']} of {metric['expression']} from {metric['model']}\n"
            if 'dimensions' in metric:
                metrics_desc += f"  Dimensions: {', '.join(metric['dimensions'])}\n"
            
        return f"""
You have access to ONE governed view: fct_revenue

This view already:
- Filters to completed orders only (revenue definition)
- Joins customers and products correctly
- Calculates net_amount = gross_amount - discount
- Calculates gross_profit = net_amount - product cost

Available columns:
- net_amount       : the actual revenue for each order (ALWAYS use this for revenue)
- gross_amount     : pre-discount amount (do NOT use for revenue)
- discount         : discount applied
- gross_profit     : profitability per order
- order_date       : date of order
- order_month      : truncated to month
- order_quarter    : truncated to quarter
- region           : North, South, East, West
- customer_segment : Enterprise, SMB, Consumer
- product_category : SaaS, Hardware, Services
- customer_name    : customer name

Metric definitions derived from revenue.yml:
{metrics_desc}

NEVER query raw_orders, raw_customers, or raw_products directly.
ALWAYS use fct_revenue.
"""
    except Exception as e:
        print(f"Error loading revenue.yml: {e}")
        return ""

SEMANTIC_CONTEXT = load_semantic_context()

def ask_with_semantic(question: str) -> dict:
    prompt = f"""You are a data analyst. Use ONLY the semantic layer described below to write a DuckDB SQL query.
Return ONLY the SQL query, nothing else.

{SEMANTIC_CONTEXT}

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
