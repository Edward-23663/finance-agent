"""JSON-RPC协议测试"""
import pytest
from src.communication.protocol import JSONRPCRequest, JSONRPCResponse, JSONRPCError


class TestJSONRPCRequest:
    """JSONRPCRequest 测试"""

    def test_create_request(self):
        """测试创建请求"""
        request = JSONRPCRequest(method="test.method", params={"key": "value"}, id="1")

        assert request.method == "test.method"
        assert request.params == {"key": "value"}
        assert request.id == "1"
        assert request.jsonrpc == "2.0"

    def test_request_with_default_values(self):
        """测试默认参数"""
        request = JSONRPCRequest(method="test.method")

        assert request.params is None
        assert request.id is None
        assert request.jsonrpc == "2.0"


class TestJSONRPCResponse:
    """JSONRPCResponse 测试"""

    def test_create_success_response(self):
        """测试成功响应"""
        response = JSONRPCResponse(result={"data": "test"}, id="1")

        assert response.result == {"data": "test"}
        assert response.id == "1"
        assert response.error is None
        assert not response.is_error()

    def test_create_error_response(self):
        """测试错误响应"""
        response = JSONRPCResponse(error={"code": -32600, "message": "Invalid Request"}, id="1")

        assert response.error is not None
        assert response.error["code"] == -32600
        assert response.is_error()

    def test_response_default_values(self):
        """测试默认参数"""
        response = JSONRPCResponse()

        assert response.result is None
        assert response.error is None
        assert response.id is None
        assert response.jsonrpc == "2.0"


class TestJSONRPCError:
    """JSONRPCError 测试"""

    def test_create_error(self):
        """测试创建错误"""
        error = JSONRPCError(code=-32600, message="Invalid Request", data={"extra": "info"})

        assert error.code == -32600
        assert error.message == "Invalid Request"
        assert error.data == {"extra": "info"}

    def test_error_without_data(self):
        """测试不带数据的错误"""
        error = JSONRPCError(code=-32601, message="Method not found")

        assert error.data is None
