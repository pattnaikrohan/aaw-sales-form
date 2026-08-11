import os
from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str
    name: str
    
class UserResponse(BaseModel):
    name: str
    email: str

class SpeechRequest(BaseModel):
    name: str
    contentBytes: str
    
class SpeechResponse(BaseModel):
    transcript: str = ""
    clientName: str = ""
    subject: str = ""
    method: str = ""
    purpose: str = ""
    status: str = ""
    primaryContact: str = ""
    actualDate: str = ""
    notes: str = ""

class ChatRequest(BaseModel):
    message: str
    conversationHistory: list
    currentFormState: dict
    
class ChatResponse(BaseModel):
    reply: str
    extractedFields: dict

class ExtractFieldsRequest(BaseModel):
    userMessage: str
    botReply: str
    currentFormState: dict

class ExtractFieldsResponse(BaseModel):
    extractedFields: dict

class CompanySearchRequest(BaseModel):
    companySearchText: str
    
class CompanySearchResponse(BaseModel):
    companies: list

class SubmitRequest(BaseModel):
    clientName: Optional[str] = ""
    subject: Optional[str] = ""
    method: Optional[str] = ""
    purpose: Optional[str] = ""
    status: Optional[str] = ""
    primaryContact: Optional[str] = ""
    actualDate: Optional[str] = ""
    scheduledDate: Optional[str] = ""
    notes: Optional[str] = ""
    submittedBy: Optional[str] = "AAW Demo User"
    
class SubmitResponse(BaseModel):
    status: str
    message: str

class TranscriptRequest(BaseModel):
    content: str
