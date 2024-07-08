import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import DevelopmentConfig, ProductionConfig

def verify_db():
    if os.environ.get('APP_MODE') == 'production':
        config = ProductionConfig()
    else:
        config = DevelopmentConfig()

    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        crime_data = session.execute(text("SELECT COUNT(*) FROM crime_data")).fetchone()
        print(f"crime_data table has {crime_data[0]} records.")

        unfounded_data = session.execute(text("SELECT COUNT(*) FROM unfounded_data")).fetchone()
        print(f"unfounded_data table has {unfounded_data[0]} records.")

        meta_data = session.execute(text("SELECT COUNT(*) FROM meta_data")).fetchone()
        print(f"meta_data table has {meta_data[0]} records.")

        meta = session.execute(text("SELECT * FROM meta_data")).fetchone()
        print(f"meta_data: {meta}")

        raw_data = session.execute(text("SELECT COUNT(*) FROM raw_data")).fetchone()
        print(f"raw_data table has {raw_data[0]} records.")
    except Exception as e:
        print(f"Error verifying database: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    verify_db()