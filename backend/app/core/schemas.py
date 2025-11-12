from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional, Literal


class UserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    institution: Optional[str] = None
    field_of_study: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    institution: Optional[str] = None
    field_of_study: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ArticleBase(BaseModel):
    title: str
    authors: Optional[List[str]] = []
    abstract: Optional[str] = None
    keywords: Optional[List[str]] = []
    publication_year: Optional[int] = None
    journal: Optional[str] = None
    doi: Optional[str] = None


class ArticleCreate(ArticleBase):
    category_id: Optional[int] = None


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    abstract: Optional[str] = None
    keywords: Optional[List[str]] = None
    category_id: Optional[int] = None


class ArticleResponse(ArticleBase):
    id: int
    file_path: Optional[str]
    category_id: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime
    auto_topics: Optional[List[str]] = []

    class Config:
        from_attributes = True


class UserLibraryBase(BaseModel):
    status: Optional[str] = "unread"
    notes: Optional[str] = None
    rating: Optional[int] = None


class UserLibraryCreate(BaseModel):
    article_id: int


class UserLibraryUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    rating: Optional[int] = None
    topics: Optional[List[str]] = None


class UserLibraryResponse(UserLibraryBase):
    id: int
    user_id: int
    article_id: int
    added_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class AnnotationBase(BaseModel):
    highlighted_text: str
    page_number: Optional[int] = None
    position_data: Optional[dict] = None
    color: Optional[str] = "yellow"
    note: Optional[str] = None
    tags: Optional[List[str]] = []


class AnnotationCreate(AnnotationBase):
    article_id: int


class AnnotationUpdate(BaseModel):
    highlighted_text: Optional[str] = None
    page_number: Optional[int] = None
    position_data: Optional[dict] = None
    color: Optional[str] = None
    note: Optional[str] = None
    tags: Optional[List[str]] = None


class AnnotationResponse(AnnotationBase):
    id: int
    article_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LibraryEntryUpdate(BaseModel):
    status: Optional[Literal["unread", "reading", "read"]] = None
    notes: Optional[str] = None
    rating: Optional[int] = None


class BatchSummaryRequest(BaseModel):
    article_ids: List[int]
    method: Literal["auto", "local", "groq"] = "auto"
    max_sentences: int = 5
    level: Literal["executive", "detailed", "exhaustive"] = "detailed"
    combined: bool = False
    combined_max_sentences: Optional[int] = None


class SummaryResult(BaseModel):
    article_id: int
    title: Optional[str] = None
    success: bool
    summary: Optional[str] = None
    method: Optional[str] = None
    error: Optional[str] = None


class BatchSummaryResponse(BaseModel):
    results: List[SummaryResult]
    combined_summary: Optional[str] = None
    combined_method: Optional[str] = None


class UserIndexBase(BaseModel):
    name: str
    keywords: List[str]
    color: Optional[str] = "#2563eb"


class UserIndexCreate(UserIndexBase):
    pass


class UserIndexResponse(UserIndexBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
