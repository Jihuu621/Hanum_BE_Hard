# 라이브러리 import하는 부분

from fastapi import FastAPI
from sqlalchemy import create_engine, Table, MetaData, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel, SecretStr
from typing import List, Optional

base = declarative_base()
app = FastAPI()


# 데이터베이스 URL
DATABASE_URL = "mysql://root:qwojomoq1004@127.0.0.1/Hard"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

metadata = MetaData()

# DB에서 posts 테이블 가져오기
posts = Table('posts', metadata, autoload_with=engine)


# 모델 선언
class PostBase(BaseModel):
    id: int
    title: str
    author: str
    content: str
    # password는 표시하지 않음

class NewPost(BaseModel):
    id: Optional[int] = None # Int일수도 있고 None일수도 (아닐수도) 있습니다
    title: str
    author: str
    content: str
    password: SecretStr

class AltPost(base):
    __tablename__ = 'posts' # 테이블 이름은 posts

    id = Column(Integer, primary_key=True, index=True, autoincrement=True) # primary_key, 고유한 값을 가짐. index, 인덱스 생성함, audoincrement, 생성할때마다 자동으로 값 상승
    title = Column(String, index=True) 
    author = Column(String, index=True) 
    content = Column(String, index=True) 
    password = Column(String, index=True)



# 여기서부터 작동하는 부분



@app.get("/posts", response_model=List[PostBase])
def get_todo():
    db = SessionLocal()
    try:
        # posts 테이블의 모든 항목 가져오기
        post = db.query(posts).all()
        return post
    finally:
        db.close()

@app.get("/posts/{postid}", response_model=List[NewPost])
def get_todo(postid: int):
    db = SessionLocal()
    try:
        # posts 테이블의 모든 항목 가져오기
        post = db.query(posts).filter_by(id=postid)
        return post
    finally:
        db.close()

@app.post("/posts")
def create_post(post: NewPost):
    db = SessionLocal()
    newpost = AltPost( # NewPost로하면 에러뜸, AltPost로 새로 만들음
        title=post.title,
        author=post.author, 
        content=post.content, 
        password=post.password.get_secret_value()
    )

    db.add(newpost)
    db.commit()
    return {"postId": newpost.id} # 뉴포스트 id 리턴


@app.delete("/posts/{post_id}")
def delete_post(post_id: int, password: str):
    db = SessionLocal()
    post = db.query(AltPost).filter(AltPost.id == post_id).first()
    if post.password == password: # 비밀번호 맞는지 확인
        db.delete(post)
        db.commit()
        ok = True
    else:
        ok = False

    return {"ok": ok}


# 진짜 끝났다!!!!!!!!!!!!!!!!!