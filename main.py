from fastapi import  FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models


app = FastAPI()
models.Base.metadata.create_all(bind=engine)


class ChoiceBase(BaseModel):
    id: int
    choice_text: str
    is_correct: bool
    
    class Config:
        orm_mode = True
    

class QuestionBase(BaseModel):
    id: int
    question_text: str
    choices: List[ChoiceBase]
    
    class Config:
        orm_mode = True
    

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        


@app.post('/questions/')
async def create_questions(question: QuestionBase, db: Session = Depends(get_db)):
    db_question = models.Questions(question_text=question.question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    
    for choice in question.choices:
        db_choice = models.Choices(
            choice_text=choice.choice_text,
            is_correct=choice.is_correct,
            question_id=db_question.id
            )
        db.add(db_choice)
    db.commit()

    return db_question


@app.get('/questions/', response_model=List[QuestionBase])
async def get_questions(db: Session = Depends(get_db)):
    result = db.query(models.Questions).all()
    if not result:
        raise HTTPException(status_code=404, detail='Question is not available')
    return result


@app.get('/questions/{question_id}')
async def get_questions(question_id: int, db: Session = Depends(get_db)):
    result = db.query(models.Questions).filter(
        models.Questions.id == question_id
    ).first()
    if not result:
        raise HTTPException(status_code=404, detail='Question is not available')
    
    return result


