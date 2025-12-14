import pandas as pd
from sqlalchemy import create_engine
import os
import re

print("Running SQL Analytics...\n")

# Connect to database
engine = create_engine('sqlite:///data/food_delivery.db')

# Create output folder
os.makedirs('data/exports', exist_ok=True)

# List of SQL files to execute
sql_files = [
    'sql/02_core_metrics.sql',
    'sql/03_delivery_person_analysis.sql',
    'sql/04_advanced_queries.sql'
]

results = {}

for sql_file in sql_files:
    if not os.path.exists(sql_file):
        print(f"[WARNING] File not found: {sql_file}")
        continue
    
    print(f"\n{'='*60}")
    print(f"Executing: {sql_file}")
    print(f"{'='*60}\n")
    
    # Read SQL file
    with open(sql_file, 'r') as f:
        sql_content = f.read()
    
    # Extract queries using regex - look for comments with "QUERY" followed by SELECT statement
    # Pattern: -- QUERY <number>: <name> followed by SELECT...;
    pattern = r'--\s*QUERY\s+\d+:\s*(.+?)\n(.*?)(?=--\s*QUERY|\Z)'
    matches = re.finditer(pattern, sql_content, re.DOTALL | re.IGNORECASE)
    
    for match in matches:
        query_name = match.group(1).strip()
        sql_query = match.group(2).strip()
        
        # Clean up the SQL - remove comment lines at the beginning
        sql_lines = [line for line in sql_query.split('\n') if line.strip() and not line.strip().startswith('--')]
        sql_query = ' '.join([line.strip() for line in sql_lines])
        
        if not sql_query or 'SELECT' not in sql_query.upper():
            continue
        
        try:
            # Execute query
            df = pd.read_sql(sql_query, engine)
            
            # Display results (truncate if too many columns)
            print(f"\n[{query_name}]")
            print(f"{'-'*60}")
            if len(df) > 0:
                print(df.head(20).to_string(index=False))
                if len(df) > 20:
                    print(f"... ({len(df) - 20} more rows)")
            print(f"Rows returned: {len(df)}")
            
            # Save to CSV
            safe_name = query_name.replace(' ', '_').replace(':', '').replace('/', '_').lower()
            output_file = f"data/exports/{safe_name}.csv"
            df.to_csv(output_file, index=False)
            print(f"[Saved to: {output_file}]")
            
            results[query_name] = df
            
        except Exception as e:
            print(f"[ERROR in {query_name}: {str(e)}]")

print(f"\n{'='*60}")
print(f"[SQL ANALYTICS COMPLETE!]")
print(f"{'='*60}")
print(f"\nTotal queries executed: {len(results)}")
print(f"Results saved to: data/exports/")