import ast


# ==========================================================
# DEVGUARD CODE QUALITY SETTINGS
# ==========================================================

MAX_LINE_LENGTH = 100
MAX_FUNCTION_LENGTH = 50
HIGH_COMPLEXITY_THRESHOLD = 10


# ==========================================================
# COMPLEXITY ANALYSIS
# ==========================================================

def calculate_function_complexity(function_node):
    """
    Calculate a simple cyclomatic-complexity-style metric
    for a single function.

    Base complexity = 1

    Decision points increase complexity:
    - if
    - for
    - while
    - except
    - boolean operators
    - comprehensions
    - ternary expressions
    - match cases
    """

    complexity = 1

    for node in ast.walk(function_node):

        # Do not include nested functions/classes
        # in the complexity of the parent function.
        if node is not function_node and isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        ):
            continue

        # if statements
        if isinstance(node, ast.If):
            complexity += 1

        # for loops
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            complexity += 1

        # while loops
        elif isinstance(node, ast.While):
            complexity += 1

        # exception handlers
        elif isinstance(node, ast.ExceptHandler):
            complexity += 1

        # Boolean operators
        elif isinstance(node, ast.BoolOp):
            complexity += max(0, len(node.values) - 1)

        # List/set/dict comprehensions and generator expressions
        elif isinstance(node, ast.comprehension):
            complexity += 1

        # Ternary expression:
        # value_if_true if condition else value_if_false
        elif isinstance(node, ast.IfExp):
            complexity += 1

        # Python match/case
        elif isinstance(node, ast.match_case):
            complexity += 1

    return complexity


# ==========================================================
# FUNCTION INFORMATION
# ==========================================================

def get_function_details(tree):
    """
    Extract function information from an AST tree.
    """

    functions = []

    for node in ast.walk(tree):

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):

            start_line = getattr(node, "lineno", 0)
            end_line = getattr(node, "end_lineno", start_line)

            function_length = end_line - start_line + 1

            # Check for docstring
            has_docstring = (
                ast.get_docstring(node) is not None
            )

            complexity = calculate_function_complexity(node)

            functions.append({
                "name": node.name,
                "start_line": start_line,
                "end_line": end_line,
                "line_count": function_length,
                "documented": has_docstring,
                "complexity": complexity,
                "high_complexity": (
                    complexity > HIGH_COMPLEXITY_THRESHOLD
                ),
            })

    return functions


# ==========================================================
# CLASS INFORMATION
# ==========================================================

def get_class_details(tree):
    """
    Extract class names from the AST tree.
    """

    classes = []

    for node in ast.walk(tree):

        if isinstance(node, ast.ClassDef):

            classes.append({
                "name": node.name,
                "line": getattr(node, "lineno", 0),
            })

    return classes


# ==========================================================
# PYTHON CODE ANALYZER
# ==========================================================

def analyze_python_code(file_path, source_code):
    """
    Analyze a Python source file.

    Returns:
        Dictionary containing code-quality metrics.
    """

    lines = source_code.splitlines()

    total_lines = len(lines)

    blank_lines = sum(
        1 for line in lines
        if not line.strip()
    )

    comment_lines = sum(
        1 for line in lines
        if line.strip().startswith("#")
    )

    long_lines = []

    for line_number, line in enumerate(lines, start=1):

        if len(line) > MAX_LINE_LENGTH:

            long_lines.append({
                "line": line_number,
                "length": len(line),
                "content": line.strip(),
            })

    # ------------------------------------------------------
    # Ratios
    # ------------------------------------------------------

    if total_lines > 0:

        blank_line_ratio = round(
            (blank_lines / total_lines) * 100,
            2
        )

        comment_ratio = round(
            (comment_lines / total_lines) * 100,
            2
        )

    else:

        blank_line_ratio = 0
        comment_ratio = 0

    # ------------------------------------------------------
    # AST Analysis
    # ------------------------------------------------------

    syntax_errors = []

    functions = []

    classes = []

    try:

        tree = ast.parse(
            source_code,
            filename=file_path
        )

        functions = get_function_details(tree)

        classes = get_class_details(tree)

    except SyntaxError as error:

        syntax_errors.append({
            "line": error.lineno,
            "offset": error.offset,
            "message": error.msg,
        })

    # ------------------------------------------------------
    # Function metrics
    # ------------------------------------------------------

    total_functions = len(functions)

    documented_functions = sum(
        1
        for function in functions
        if function["documented"]
    )

    undocumented_functions = (
        total_functions - documented_functions
    )

    if total_functions > 0:

        average_function_length = round(
            sum(
                function["line_count"]
                for function in functions
            ) / total_functions,
            1
        )

        average_complexity = round(
            sum(
                function["complexity"]
                for function in functions
            ) / total_functions,
            2
        )

    else:

        average_function_length = 0

        average_complexity = 0

    # ------------------------------------------------------
    # Long functions
    # ------------------------------------------------------

    long_functions = [
        function
        for function in functions
        if function["line_count"] > MAX_FUNCTION_LENGTH
    ]

    # ------------------------------------------------------
    # High complexity functions
    # ------------------------------------------------------

    high_complexity_functions = [
        function
        for function in functions
        if function["complexity"] > HIGH_COMPLEXITY_THRESHOLD
    ]

    # ------------------------------------------------------
    # Return result
    # ------------------------------------------------------

    return {

        "file_path": file_path,

        "total_lines": total_lines,

        "blank_lines": blank_lines,

        "blank_line_ratio": blank_line_ratio,

        "comment_lines": comment_lines,

        "comment_ratio": comment_ratio,

        "long_lines": long_lines,

        "long_line_count": len(long_lines),

        "functions": functions,

        "total_functions": total_functions,

        "documented_functions": documented_functions,

        "undocumented_functions": undocumented_functions,

        "documentation_ratio": (
            round(
                (documented_functions / total_functions) * 100,
                2
            )
            if total_functions > 0
            else 0
        ),

        "average_function_length": average_function_length,

        "long_functions": long_functions,

        "long_function_count": len(long_functions),

        "average_complexity": average_complexity,

        "high_complexity_functions": high_complexity_functions,

        "high_complexity_count": len(
            high_complexity_functions
        ),

        "classes": classes,

        "class_count": len(classes),

        "syntax_errors": syntax_errors,

        "syntax_error_count": len(syntax_errors),

    }


# ==========================================================
# MULTI-FILE PYTHON ANALYSIS
# ==========================================================

def analyze_repository_python_files(
    python_files,
    source_loader
):
    """
    Analyze multiple Python files.

    Args:
        python_files:
            List of repository Python file paths.

        source_loader:
            Function that receives a file path and returns
            source code.

    Returns:
        List of analysis results.
    """

    results = []

    for file_path in python_files:

        try:

            source_code = source_loader(file_path)

            result = analyze_python_code(
                file_path,
                source_code
            )

            results.append(result)

        except Exception as error:

            results.append({
                "file_path": file_path,
                "error": str(error),
            })

    return results


# ==========================================================
# DEVGUARD QUALITY SCORE
# ==========================================================

def calculate_basic_quality_score(file_results):
    """
    Calculate the DevGuard heuristic quality score.

    NOTE:
    This is a custom DevGuard metric.
    It is NOT an industry-standard score.
    """

    score = 100.0

    for result in file_results:

        # Syntax errors
        score -= (
            result.get("syntax_error_count", 0) * 10
        )

        # Long lines
        score -= (
            result.get("long_line_count", 0) * 0.5
        )

        # Long functions
        score -= (
            result.get("long_function_count", 0) * 2
        )

    # Keep score between 0 and 100

    score = max(
        0,
        min(
            100,
            score
        )
    )

    return round(score, 2)