# data/seed_data.py
import duckdb, random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()
con = duckdb.connect("duckdb/poc.db")

con.execute("""
  CREATE TABLE IF NOT EXISTS raw_orders (
    order_id VARCHAR, customer_id VARCHAR, product_id VARCHAR,
    order_date DATE, gross_amount FLOAT, discount FLOAT,
    net_amount FLOAT, status VARCHAR, region VARCHAR
  )
""")
con.execute("""
  CREATE TABLE IF NOT EXISTS raw_customers (
    customer_id VARCHAR, customer_name VARCHAR,
    email VARCHAR, segment VARCHAR, created_at DATE
  )
""")
con.execute("""
  CREATE TABLE IF NOT EXISTS raw_products (
    product_id VARCHAR, product_name VARCHAR,
    category VARCHAR, cost FLOAT, list_price FLOAT
  )
""")

statuses = ['completed', 'returned', 'pending', 'cancelled']
regions  = ['North', 'South', 'East', 'West']
segments = ['Enterprise', 'SMB', 'Consumer']

customers = []
for _ in range(200):
    cid = fake.uuid4()
    customers.append(cid)
    con.execute("INSERT INTO raw_customers VALUES (?,?,?,?,?)", [
        cid, fake.name(), fake.email(),
        random.choice(segments),
        fake.date_between('-2y', 'today')
    ])

products = []
for _ in range(30):
    pid = fake.uuid4()
    cost = round(random.uniform(10, 500), 2)
    products.append(pid)
    con.execute("INSERT INTO raw_products VALUES (?,?,?,?,?)", [
        pid, fake.catch_phrase(),
        random.choice(['SaaS','Hardware','Services']),
        cost, round(cost * random.uniform(1.3, 2.5), 2)
    ])

base_date = datetime.today() - timedelta(days=730)
for i in range(2000):
    gross = round(random.uniform(50, 5000), 2)
    disc  = round(gross * random.uniform(0, 0.3), 2)
    con.execute("INSERT INTO raw_orders VALUES (?,?,?,?,?,?,?,?,?)", [
        fake.uuid4(), random.choice(customers), random.choice(products),
        (base_date + timedelta(days=random.randint(0,730))).date(),
        gross, disc, round(gross - disc, 2),
        random.choice(statuses), random.choice(regions)
    ])

print("Seeded 200 customers, 30 products, 2000 orders.")
con.close()