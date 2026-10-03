import sympy as sp
import re

def my_jarvis_brain(question):
    q = question.lower().strip()
    try:
        x = sp.Symbol('x')
        # --- 1. Equation Solve (x dhundo) ---
        if "solve" in q or "=" in q or "x" in q:
            # jaise: solve x^2 - 5x + 6 = 0
            q_clean = q.replace("solve","").replace("^","**").replace("=","-(") + ")"
            if "=" not in question:
                q_clean = q.replace("^","**")
            try:
                # sympy se solve
                expr = sp.sympify(q_clean.split("-(")[0] if "-(" not in q_clean else q_clean)
                sol = sp.solve(expr, x)
                if sol:
                    return f"Boss Solution hai: x = {sol}"
            except:
                pass

        # --- 2. Differentiation ---
        if "differentiate" in q or "derivative" in q or "d/dx" in q:
            func = q.replace("differentiate","").replace("derivative","").replace("d/dx","").strip()
            func = func.replace("^","**")
            f = sp.sympify(func)
            ans = sp.diff(f, x)
            return f"Boss, d/dx of {func} = {ans}"

        # --- 3. Integration ---
        if "integrate" in q or "integration" in q:
            func = q.replace("integrate","").replace("integration","").strip()
            func = func.replace("^","**")
            f = sp.sympify(func)
            ans = sp.integrate(f, x)
            return f"Boss, Integration of {func} = {ans} + C"

        # --- 4. Basic to Advance Calculation ---
        # 50+20, 2^10, sqrt(16), factorial(5)
        q_math = question.replace("^","**")
        ans = sp.sympify(q_math)
        # agar sirf number hai to evaluate
        if ans!= x:
            evaluated = sp.N(ans) if ans.is_number == False else ans
            # Agar sympify ne solve kar diya
            if str(ans)!= question:
                return f"Boss, {question} = {ans}"

        return f"Boss, try aise pucho:\n- solve x^2 - 4 = 0\n- differentiate x^3 + 2x\n- integrate x^2\n- sqrt(144)\n- factorial(5)"

    except Exception as e:
        return f"Boss ye '{question}' samajh nahi aaya. Aise pucho: 'solve x^2 -5x+6=0'"

# Test
# print(my_jarvis_brain("solve x^2 -5x+6=0
