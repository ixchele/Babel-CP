import os
import subprocess
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import SubmissionDB, ResolveDB, UserDB, ProblemDB

# Configure DB connection matching your FastAPI setup
DATABASE_URL = "sqlite:///./babel.db" # Replace with your Postgres URL if different
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def execute_code_in_sandbox(code: str, stdin: str, language: str) -> dict:
    with tempfile.TemporaryDirectory() as temp_dir:
        exec_path = os.path.join(temp_dir, "program")
        compile_cmd = None
        
        if language == "cpp":
            source_path = os.path.join(temp_dir, "main.cpp")
            compile_cmd = ["g++", "-std=c++98", "-Wall", "-Wextra", "-Werror", source_path, "-o", exec_path]
            run_target = ["/app/program"]
        elif language == "c":
            source_path = os.path.join(temp_dir, "main.c")
            compile_cmd = ["gcc", "-Wall", "-Wextra", "-Werror", source_path, "-o", exec_path]
            run_target = ["/app/program"]
        elif language == "python":
            source_path = os.path.join(temp_dir, "main.py")
            run_target = ["python3", "/app/main.py"]
        elif language == "bash":
            source_path = os.path.join(temp_dir, "main.sh")
            run_target = ["bash", "/app/main.sh"]
        else:
            return {"status": "Internal Error", "logs": "Unsupported language"}

        with open(source_path, "w") as f:
            f.write(code)

        if compile_cmd:
            compile_res = subprocess.run(compile_cmd, capture_output=True, text=True)
            if compile_res.returncode != 0:
                return {"status": "Compilation Error", "compile_output": compile_res.stderr}

        run_cmd = [
            "bwrap",
            "--ro-bind", "/usr", "/usr",
            "--ro-bind-try", "/lib", "/lib",
            "--ro-bind-try", "/lib64", "/lib64",
            "--ro-bind-try", "/bin", "/bin",
            "--ro-bind-try", "/sbin", "/sbin",
            "--proc", "/proc",
            "--dev", "/dev",
            "--bind", temp_dir, "/app",
            "--unshare-pid",
            "--unshare-ipc",
            "--unshare-uts",
            "--die-with-parent",
            "--chdir", "/app"
        ] + run_target

        try:
            run_res = subprocess.run(run_cmd, input=stdin, text=True, capture_output=True, timeout=2.0)
            if run_res.returncode != 0:
                return {"status": "Runtime Error", "logs": run_res.stderr}
            return {"status": "Accepted", "stdout": run_res.stdout, "time": "0.00s"}
        except subprocess.TimeoutExpired:
            return {"status": "Time Limit Exceeded", "time": "2.00s"}

def evaluate_submission(submission_id: int):
    db = SessionLocal()
    try:
        submission = db.query(SubmissionDB).filter(SubmissionDB.id == submission_id).first()
        if not submission:
            return

        submission.status = "Running"
        db.commit()

        problem = db.query(ProblemDB).filter(ProblemDB.id == submission.id_problem).first()
        if not problem or not problem.test_cases:
            submission.status = "Internal Error"
            submission.logs = "No test cases found."
            db.commit()
            return

        all_passed = True
        
        for test in problem.test_cases:
            try:
                with open(test.stdin, "r") as f_in:
                    stdin_data = f_in.read()
                with open(test.expected_output, "r") as f_out:
                    expected_data = f_out.read()
            except IOError:
                submission.status = "Internal Error"
                submission.logs = "Failed to read testcase files."
                all_passed = False
                break

            result = execute_code_in_sandbox(
                submission.code_submited, 
                stdin_data, 
                submission.language.lower()
            )
            
            if result["status"] != "Accepted":
                submission.status = result["status"]
                submission.logs = result.get("logs", "")
                all_passed = False
                break
                
            clean_output = result["stdout"].strip()
            clean_expected = expected_data.strip()
            
            if clean_output != clean_expected:
                submission.status = "Wrong Answer"
                submission.logs = f"Expected:\n{clean_expected}\nGot:\n{clean_output}"
                all_passed = False
                break
        if all_passed:
            submission.status = "Accepted"
            
            user = db.query(UserDB).filter(UserDB.id == submission.id_user).first()
            already_resolved = db.query(ResolveDB).filter(
                ResolveDB.id_user == user.id,
                ResolveDB.id_problem == problem.id
            ).first()
            
            if not already_resolved:
                failed_attempts = db.query(SubmissionDB).filter(
                    SubmissionDB.id_user == user.id,
                    SubmissionDB.id_problem == problem.id,
                    SubmissionDB.status != "Accepted",
                    SubmissionDB.id != submission.id
                ).count()

                base_points = problem.base_points or 0
                penalty = int(base_points * 0.10 * failed_attempts)
                max_penalty = int(base_points * 0.50)
                points_earned = base_points - min(penalty, max_penalty)
                
                user.score = (user.score or 0) + points_earned
                
                new_resolve = ResolveDB(
                    id_user=user.id,
                    id_problem=problem.id,
                    number_of_tries=failed_attempts + 1,
                    points=points_earned
                )
                db.add(new_resolve)
                
        db.commit()
    finally:
        db.close()
