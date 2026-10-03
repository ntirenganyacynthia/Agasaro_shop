from app.database import Base, engine
import app.models  # registers all models with Base

Base.metadata.create_all(bind=engine)
print("Created tables:", sorted(Base.metadata.tables))
