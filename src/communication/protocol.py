"""JSON-RPC协议定义"""
from typing import Any, Optional, Dict
from pydantic import BaseModel, Field


class JSONRPCRequest(BaseModel):
    """JSON-RPC请求"""

    jsonrpc: str = Field(default="2.0", description="JSON-RPC版本")
    method: str = Field(..., description="方法名")
    params: Optional[Dict[str, Any]] = Field(default=None, description="参数")
    id: Optional[str] = Field(default=None, description="请求ID")


class JSONRPCResponse(BaseModel):
    """JSON-RPC响应"""

    jsonrpc: str = Field(default="2.0", description="JSON-RPC版本")
    result: Optional[Any] = Field(default=None, description="结果")
    error: Optional[Dict[str, Any]] = Field(default=None, description="错误")
    id: Optional[str] = Field(default=None, description="请求ID")

    def is_error(self) -> bool:
        """是否为错误响应"""
        return self.error is not None


class JSONRPCError(BaseModel):
    """JSON-RPC错误"""

    code: int = Field(..., description="错误码")
    message: str = Field(..., description="错误消息")
    data: Optional[Any] = Field(default=None, description="错误数据")
