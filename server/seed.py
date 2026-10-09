import os
from database import engine, Base, SessionLocal, ProblemDB, TestCaseDB

Base.metadata.create_all(bind=engine)

def force_seed():
    db = SessionLocal()
    
    # Setup problem directory
    problem_dir = "data/problems/echo"
    os.makedirs(problem_dir, exist_ok=True)
    
    subject_file = os.path.join(problem_dir, "subject.md")
    with open(subject_file, "w") as f:
        f.write("# Echo Program\nRead a string from stdin and print it to stdout.")
    
    in_1_file = os.path.join(problem_dir, "in_1.txt")
    out_1_file = os.path.join(problem_dir, "out_1.txt")
    
    with open(in_1_file, "w") as f: f.write("Hello 1337\n")
    with open(out_1_file, "w") as f: f.write("Hello 1337")

    problem = ProblemDB(
        title="Echo Program",
        description="Read a string from stdin and print it to stdout.",
        subject=subject_file,
        difficulty="Easy",
        time_limit=2,
        memory_limit=256,
        base_points=100
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)

    tc1 = TestCaseDB(
        stdin=in_1_file,
        expected_output=out_1_file,
        id_problem=problem.id
    )
    
    db.add(tc1)
    db.commit()
    
    print("[ OK ] Problem added with ID: " + str(problem.id))
    db.close()

if __name__ == "__main__":
    force_seed()
