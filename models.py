from typing import List, Optional, Dict, Union
from pydantic import BaseModel, Field

class User(BaseModel):
    username: str
    password: str
    access: Optional[List[str]] = None
    is_active: Optional[bool] = None

class SciencePaperRequest(BaseModel):
    class_level: int = Field(6, alias='class', description="Grade level for the paper")
    subject: str = Field("science", description="Subject for the paper")
    chapters: List[str] = Field(["COMPONENTS OF FOOD"], description="Chapters to include")
    question_type: str = Field("mcq", description="Type of questions (mcq, descriptive, fillup, truefalse)")
    taxonomies: List[str] = Field(["remember", "understand"], description="Cognitive level of questions")
    num_questions: int = Field(9, description="Total number of questions")

    class Config:
        json_schema_extra = {
            "example": {
                "class": 6,
                "subject": "science",
                "chapters": ["COMPONENTS OF FOOD"],
                "question_type": "mcq",
                "taxonomies": ["remember", "understand"],
                "num_questions": 9
            }
        }


class EnglishPaperRequest(BaseModel):
    class_level: int = Field(6, alias='class', description="Grade level for the paper")
    subject: str = Field("english", description="Subject for the paper")
    chapters: List[str] = Field(["A TALE OF TWO BIRDS"], description="Chapters to include")
    question_type: str = Field("mcq", description="Type of questions (mcq, descriptive, fillup, truefalse)")
    taxonomies: List[str] = Field(["remember", "understand"], description="Cognitive level of questions")
    num_questions: int = Field(9, description="Total number of questions")

    class Config:
        json_schema_extra = {
            "example": {
                "class": 6,
                "subject": "english",
                "chapters": ["A TALE OF TWO BIRDS"],
                "question_type": "mcq",
                "taxonomies": ["remember", "understand"],
                "num_questions": 9
            }
        }
     
        
class QuestionOptionPair(BaseModel):
    question: str
    options: List[str]
    answer: str

class QuestionResponse(BaseModel):
    questions: List[QuestionOptionPair]


class ChatHistory(BaseModel):
    input: str
    output: str

class productAssistantChatRequest(BaseModel):
    input: str = Field(..., description="User input for the chat")
    session_id: Optional[str] = Field(None, description="Session ID for chat")
    type: str = Field(..., description="Type of chat request: 'specific' or 'generic'")
    product_name: Optional[str] = Field(None, description="Product name for specific queries")
    product_type: Optional[str] = Field(None, description="Product type for specific queries")

    class Config:
        json_schema_extra = {
            "example": {
                "input": "Tell me about Bima Ratna",
                "session_id": "5",
                "type": "specific",
                "product_name": "BimaRatna",
                "product_type": "EndowmentPlan"
            }
        }

class ChatResponse(BaseModel):
    input: str
    chat_history: List[ChatHistory]
    output: str
    session_id: str


class CaseStudyRequest(BaseModel):
    class_level: int = Field(6, alias='class', description="Grade level for the paper")
    subject: str  =  Field("science", description="Subject for the paper")
    chapters: List[str] =  Field(["COMPONENTS OF FOOD"], description="Chapters to include")
    num_questions: int = Field(5, description="Total number of questions")

    class Config:
        json_schema_extra = {
            "example": {
                "class_level": 6,
                "subject": "science",
                "chapters": ["COMPONENTS OF FOOD"],            
                "num_questions": 5
            }
        }


class QuestionResponseCaseStudy(BaseModel):
    statusCode: int
    response: Union[
        Dict[str, List[Dict[str, Union[str, List[str]]]]],
        List[Dict[str, Union[str, List[Dict[str, Union[str, List[str]]]]]]]
    ]

class QuestionResponseReadingComprehension(BaseModel):
    statusCode: int
    response: Dict[str, Union[str, List[Dict[str, Union[str, List[str]]]]]]


class ReadingCompRequest(BaseModel):
    class_level: int = Field(6, alias='class', description="Grade level for the paper")
    subject: str  = Field("english", description="Subject for the paper")
    compre_theme:str = Field("Environmental Conservation" , description="Theme for comprehension")
    num_questions: int = Field(5, description="Total number of questions")

    class Config:
        json_schema_extra = {
            "example": {
                "class_level": 6,
                "subject": "english",
                "compre_theme": "Environmental Conservation",            
                "num_questions": 5
            }
        }



class EKMChatRequest(BaseModel):
    input: str = Field(..., description="User input for the chat")    

    class Config:
        json_schema_extra = {
            "example": {
                "input": "What is GST and how can I register for it?"                
            }
        }

class imageAssistantChatRequest(BaseModel):
    input: str = Field(..., description="User input for the chat")
    session_id: Optional[str] = Field(None, description="Session ID for chat")
    product_name: Optional[str] = Field(None, description="Product name for specific queries")
    product_type: Optional[str] = Field(None, description="Product type for specific queries")

    class Config:
        json_schema_extra = {
            "example": {
                "input": "Tell me features in this product",
                "session_id": "5",
                "product_name": "LP0815WNR",
                "product_type": "AC"
            }
        }

