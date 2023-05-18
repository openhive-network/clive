# distutils: language = c++
from libcpp.string cimport string

from wax cimport error_code, result, protocol
from .wax_result import python_result, python_error_code

def handle_exception(ex: Exception) -> python_result:
    return python_result(value=0, content="", exception_message=str(ex))


def validate_operation(operation: bytes) -> python_result:
    cdef protocol obj
    try:
        result = obj.cpp_validate_operation(operation)
        return python_result(status=python_error_code(result.value), result=result.content, exception_message=result.exception_message)
    except Exception as ex:
        return handle_exception(ex)

def validate_transaction(transaction: bytes) -> python_result:
    cdef protocol obj
    try:
        result = obj.cpp_validate_transaction(transaction)
        return python_result(status=python_error_code(result.value), result=result.content, exception_message=result.exception_message)
    except Exception as ex:
        return handle_exception(ex)

def calculate_digest(transaction: bytes, chain_id: bytes) -> python_result:
    cdef protocol obj
    try:
        result = obj.cpp_calculate_digest(transaction, chain_id)
        return python_result(status=python_error_code(result.value), result=result.content, exception_message=result.exception_message)
    except Exception as ex:
        return handle_exception(ex)

def serialize_transaction(transaction: bytes) -> python_result:
    cdef protocol obj
    try:
        result = obj.cpp_serialize_transaction(transaction)
        return python_result(status=python_error_code(result.value), result=result.content, exception_message=result.exception_message)
    except Exception as ex:
        return handle_exception(ex)
