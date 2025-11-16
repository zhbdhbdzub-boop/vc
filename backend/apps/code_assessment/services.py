"""
Code execution service using Docker containers
Provides sandboxed code execution with time and memory limits
"""
import docker
import json
import time
from typing import Dict, Any, List
from django.conf import settings


class CodeExecutor:
    """Execute code in isolated Docker containers"""
    
    LANGUAGE_IMAGES = {
        'python': 'python:3.11-alpine',
        'javascript': 'node:18-alpine',
        'java': 'openjdk:17-alpine',
    }
    
    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception as e:
            print(f"Docker client initialization failed: {e}")
            self.client = None
    
    def execute_python(self, code: str, input_data: str, time_limit: int = 5, memory_limit: int = 256) -> Dict[str, Any]:
        """Execute Python code"""
        try:
            if not self.client:
                return self._mock_execution(code, input_data)
            
            # Prepare execution script
            execution_script = f"""
import sys
import json
import time
import traceback

# User code
{code}

# Main execution
try:
    start_time = time.time()
    
    # Parse input
    input_data = {repr(input_data)}
    
    # Execute solution
    if 'solution' in dir():
        result = solution(input_data)
    else:
        result = None
    
    execution_time = (time.time() - start_time) * 1000  # Convert to ms
    
    print(json.dumps({{
        'success': True,
        'output': str(result),
        'execution_time_ms': execution_time,
        'error': None
    }}))
except Exception as e:
    print(json.dumps({{
        'success': False,
        'output': None,
        'execution_time_ms': 0,
        'error': str(e) + '\\n' + traceback.format_exc()
    }}))
"""
            
            # Run in Docker container
            container = self.client.containers.run(
                self.LANGUAGE_IMAGES['python'],
                command=['python', '-c', execution_script],
                detach=True,
                mem_limit=f"{memory_limit}m",
                network_disabled=True,
                remove=True,
            )
            
            # Wait for completion with timeout
            start = time.time()
            while container.status != 'exited' and (time.time() - start) < time_limit:
                time.sleep(0.1)
                container.reload()
            
            if container.status != 'exited':
                container.kill()
                return {
                    'success': False,
                    'output': None,
                    'execution_time_ms': time_limit * 1000,
                    'error': 'Time limit exceeded'
                }
            
            # Get output
            logs = container.logs().decode('utf-8')
            result = json.loads(logs)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'output': None,
                'execution_time_ms': 0,
                'error': f'Execution error: {str(e)}'
            }
    
    def execute_javascript(self, code: str, input_data: str, time_limit: int = 5, memory_limit: int = 256) -> Dict[str, Any]:
        """Execute JavaScript code"""
        try:
            if not self.client:
                return self._mock_execution(code, input_data)
            
            execution_script = f"""
const inputData = {json.dumps(input_data)};

try {{
    const startTime = Date.now();
    
    {code}
    
    const result = typeof solution === 'function' ? solution(inputData) : null;
    const executionTime = Date.now() - startTime;
    
    console.log(JSON.stringify({{
        success: true,
        output: String(result),
        execution_time_ms: executionTime,
        error: null
    }}));
}} catch (error) {{
    console.log(JSON.stringify({{
        success: false,
        output: null,
        execution_time_ms: 0,
        error: error.message + '\\n' + error.stack
    }}));
}}
"""
            
            container = self.client.containers.run(
                self.LANGUAGE_IMAGES['javascript'],
                command=['node', '-e', execution_script],
                detach=True,
                mem_limit=f"{memory_limit}m",
                network_disabled=True,
                remove=True,
            )
            
            start = time.time()
            while container.status != 'exited' and (time.time() - start) < time_limit:
                time.sleep(0.1)
                container.reload()
            
            if container.status != 'exited':
                container.kill()
                return {
                    'success': False,
                    'output': None,
                    'execution_time_ms': time_limit * 1000,
                    'error': 'Time limit exceeded'
                }
            
            logs = container.logs().decode('utf-8')
            result = json.loads(logs)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'output': None,
                'execution_time_ms': 0,
                'error': f'Execution error: {str(e)}'
            }
    
    def _mock_execution(self, code: str, input_data: str) -> Dict[str, Any]:
        """Mock execution for development without Docker"""
        try:
            # Simple eval-based execution (NOT SAFE FOR PRODUCTION)
            import sys
            from io import StringIO
            
            # Capture output
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            start = time.time()
            
            # Execute code
            exec(code)
            if 'solution' in locals():
                result = locals()['solution'](input_data)
            else:
                result = None
            
            execution_time = (time.time() - start) * 1000
            
            # Restore stdout
            sys.stdout = old_stdout
            
            return {
                'success': True,
                'output': str(result),
                'execution_time_ms': execution_time,
                'error': None
            }
        except Exception as e:
            sys.stdout = old_stdout
            return {
                'success': False,
                'output': None,
                'execution_time_ms': 0,
                'error': str(e)
            }
    
    def run_test_cases(self, code: str, language: str, test_cases: List[Dict]) -> Dict[str, Any]:
        """Run code against multiple test cases"""
        results = []
        total_time = 0
        passed = 0
        
        for test_case in test_cases:
            if language == 'python':
                result = self.execute_python(
                    code,
                    test_case['input_data'],
                    time_limit=test_case.get('time_limit', 5),
                    memory_limit=test_case.get('memory_limit', 256)
                )
            elif language == 'javascript':
                result = self.execute_javascript(
                    code,
                    test_case['input_data'],
                    time_limit=test_case.get('time_limit', 5),
                    memory_limit=test_case.get('memory_limit', 256)
                )
            else:
                result = {
                    'success': False,
                    'output': None,
                    'execution_time_ms': 0,
                    'error': f'Unsupported language: {language}'
                }
            
            # Check if output matches expected
            passed_test = (
                result['success'] and 
                str(result['output']).strip() == str(test_case['expected_output']).strip()
            )
            
            if passed_test:
                passed += 1
            
            results.append({
                'test_case_id': test_case.get('id'),
                'passed': passed_test,
                'actual_output': result['output'],
                'expected_output': test_case['expected_output'],
                'execution_time_ms': result['execution_time_ms'],
                'error': result['error']
            })
            
            total_time += result['execution_time_ms']
        
        return {
            'passed_count': passed,
            'total_count': len(test_cases),
            'total_time_ms': total_time,
            'results': results,
            'all_passed': passed == len(test_cases)
        }


# Global executor instance
executor = CodeExecutor()
