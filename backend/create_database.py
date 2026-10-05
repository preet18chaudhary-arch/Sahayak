from app.database.database import engine, Base
from app.database import models

Base.metadata.create_all(bind=engine)

print("Sahayak database created successfully.")
print("Database tables:")
for table in Base.metadata.sorted_tables:
    print(f" - {table.name}")
