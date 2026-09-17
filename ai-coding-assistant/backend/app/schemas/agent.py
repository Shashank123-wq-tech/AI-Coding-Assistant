from pydantic import BaseModel


class AgentRequest(BaseModel):

    repository_path: str

    request: str


class AgentResponse(BaseModel):

    status: str

    message: str
