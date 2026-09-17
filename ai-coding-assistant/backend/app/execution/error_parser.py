import re


class ErrorParser:
    TRACEBACK_PATTERN = re.compile(
        r'File "(.+?)", line (\d+), in (.+)'
    )

    EXCEPTION_PATTERN = re.compile(
        r"(?m)^\s*(?:E\s+)?"
        r"([A-Za-z_][A-Za-z0-9_.]*"
        r"(?:Error|Exception|Exit|Interrupt|Warning))"
        r":\s*(.*)$"
    )

    PYTEST_EXCEPTION_PATTERN = re.compile(
        r"(?m)^(.+?):(\d+):\s*"
        r"([A-Za-z_][A-Za-z0-9_.]*"
        r"(?:Error|Exception|Exit|Interrupt|Warning))\s*$"
    )
    
    PYTEST_ASSERTION_PATTERN = re.compile(
    r"(?m)^\s*E\s+assert\s+(.+)$"
    )

    PYTEST_FAILURE_PATTERN = re.compile(
        r"(?m)^FAILED\s+(.+?)::([^\s]+)"
    )
    PYTEST_TEST_NAME_PATTERN = re.compile(
    r"_{3,}\s*(test_[A-Za-z0-9_]+)\s*_{3,}"
    )

    def parse(
        self,
        stderr: str,
        stdout: str = "",
    ):
        stderr = stderr or ""
        stdout = stdout or ""

        combined_output = "\n".join(
            part for part in [stdout, stderr] if part
        )

        traceback_matches = self.TRACEBACK_PATTERN.findall(
            combined_output
        )
        
        pytest_test_name_matches = (
            self.PYTEST_TEST_NAME_PATTERN.findall(
                combined_output
            )
        )

        exception_matches = self.EXCEPTION_PATTERN.findall(
            combined_output
        )

        pytest_exception_matches = (
            self.PYTEST_EXCEPTION_PATTERN.findall(
                combined_output
            )
        )

        pytest_failures = self.PYTEST_FAILURE_PATTERN.findall(
            combined_output
        )

        file_path = None
        line_number = None
        function = None
        
        if pytest_test_name_matches:
            function = pytest_test_name_matches[-1]

        if traceback_matches:
            file_path, line_number, function = traceback_matches[-1]
            line_number = int(line_number)

        error_type = None
        message = None

        if exception_matches:
            error_type, message = exception_matches[-1]

        elif pytest_exception_matches:
            (
                pytest_file,
                pytest_line,
                pytest_error_type,
            ) = pytest_exception_matches[-1]

            error_type = pytest_error_type
            file_path = pytest_file
            line_number = int(pytest_line)
            
        assertion_matches = self.PYTEST_ASSERTION_PATTERN.findall(
            combined_output
        )
        if assertion_matches:
            message = assertion_matches[-1].strip()
        
        elif pytest_exception_matches and error_type:
            message = error_type    
            

        has_error = bool(
            stderr.strip()
            or pytest_failures
            or exception_matches
            or pytest_exception_matches
            or traceback_matches
        )
        
        return {
            "has_error": has_error,
            "error_type": error_type,
            "message": message,
            "file": file_path,
            "line": line_number,
            "function": function,
            "pytest_failures": [
                {
                    "file": file_path,
                    "test": test_name,
                }
                for file_path, test_name in pytest_failures
            ],
            "stderr": stderr,
            "stdout": stdout,
        }