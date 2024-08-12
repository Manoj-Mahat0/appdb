from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
import os

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True)
    unique_id = Column(String(50))
    punch_in_time = Column(DateTime)
    punch_out_time = Column(DateTime)

Base.metadata.create_all(bind=engine)

class Punch(BaseModel):
    unique_id: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/punch_in")
def punch_in(punch: Punch, db: Session = Depends(get_db)):
    new_entry = Attendance(unique_id=punch.unique_id, punch_in_time=datetime.now())
    db.add(new_entry)
    db.commit()
    return {"message": "Punched In", "time": new_entry.punch_in_time}

@app.post("/punch_out")
def punch_out(punch: Punch, db: Session = Depends(get_db)):
    entry = db.query(Attendance).filter(Attendance.unique_id == punch.unique_id, Attendance.punch_out_time.is_(None)).first()
    if not entry:
        raise HTTPException(status_code=400, detail="No active punch-in found")
    entry.punch_out_time = datetime.now()
    db.commit()
    return {"message": "Punched Out", "time": entry.punch_out_time}
