import string
import random
from database import SessionLocal, UserDB, ProblemDB

def generate_token(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def seed_db():
    db = SessionLocal()
    
    logins = ["ixchele", "zbengued", "student42"]
    
    print("--- Generated Credentials ---")
    
    for login in logins:
        existing_user = db.query(UserDB).filter(UserDB.username == login).first()
        if not existing_user:
            password = generate_token()
            new_user = UserDB(
                username=login, 
                hashed_password=password, 
                role="student"
            )
            db.add(new_user)
            print(f"Login: {login:<12} | Password: {password}")
        else:
            print(f"Login: {login:<12} | [Already exists]")

    print("\n--- Problems ---")
    existing_problem = db.query(ProblemDB).filter(ProblemDB.id == 1).first()
    if not existing_problem:
        problem = ProblemDB(
            title="Two Sum",
            description="Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
            subject="""
# Two Sum

Étant donné un tableau d'entiers `nums` et un entier `target`, retournez les indices des deux nombres dont la somme vaut `target`. 

Chaque entrée possède exactement une solution et un même élément ne peut pas être utilisé deux fois.

### Exemple
- **Entrée :** `nums = [2, 7, 11, 15]`, `target = 9`
- **Sortie :** `[0, 1]`

### Contraintes
- `2 <= nums.length <= 10^4`
- `-10^9 <= nums[i] <= 10^9`
- `-10^9 <= target <= 10^9`
            """,
            difficulty="Easy",
            time_limit=2.0
        )
        db.add(problem)
        print("Added Problem: Two Sum")
    else:
        print("Problem 'Two Sum' already exists.")

    db.commit()
    db.close()

if __name__ == "__main__":
    seed_db()
