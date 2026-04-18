from fastapi import FastAPI, HTTPException
import pandas as pd

"""
This is a demo endpoint that returns a list of grades for different courses. In a real application, you would replace this with actual logic to retrieve grades from a database or another data source(in this case a .xlsx file).

"""

app = FastAPI()
#endpoint; get HTTP method, this tells FASTAPI that this function will be called when a GET request is made to the /grades endpoint

#simulated login mappping
#Later this can be replaced by wechat openid
#Now users are stored in users.xlsx instead of hardcoded


def load_users():
    try:
        return pd.read_excel("app/users.xlsx")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="users.xlsx file not found")


def load_grades():
    try:
        return pd.read_excel("app/grades.xlsx")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="grades.xlsx file not found")


def validate_grade_columns(df):
    required_columns = {
        "student_id",
        "student_name",
        "course_code",
        "continuous_assessment",
        "exam_grade",
        "final_grade"
    }

    if not required_columns.issubset(df.columns):
        raise HTTPException(
            status_code=500,
            detail="grades.xlsx file is missing one or more required columns"
        )


def filter_grades(df, student_id, course_code=None):
    filtered_df = df[df["student_id"] == student_id]

    if course_code:
        filtered_df = filtered_df[filtered_df["course_code"] == course_code]

    return filtered_df


def handle_empty_grades(filtered_df, identifier_name: str, identifier_value: str, course_code: str = None):
    if filtered_df.empty:
        if course_code:
            raise HTTPException(
                status_code=404,
                detail=f"No grades found for {identifier_name} {identifier_value} in course {course_code}"
            )
        raise HTTPException(
            status_code=404,
            detail=f"No grades found for {identifier_name} {identifier_value}"
        )


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/grades")
def get_grades(student_id: int, course_code: str = None):
    df = load_grades()
    validate_grade_columns(df)

    filtered_df = filter_grades(df, student_id, course_code)
    handle_empty_grades(filtered_df, "student_id", student_id, course_code)

    return filtered_df.to_dict(orient="records")


#login simulation endpoint
@app.get("/login")
def login(user_code: str):
    df_users = load_users()

    user = df_users[df_users["user_code"] == user_code]

    if user.empty:
        raise HTTPException(status_code=404, detail="User not found")

    student_id = int(user.iloc[0]["student_id"])

    return {
        "message": f"Login successful for {user_code}",
        "student_id": student_id
    }


#endpoint to get grades using user_code instead of student_id
@app.get("/my-grades")
def my_grades(user_code: str, course_code: str = None):
    df_users = load_users()

    user = df_users[df_users["user_code"] == user_code]

    if user.empty:
        raise HTTPException(status_code=404, detail="User not found")

    student_id = int(user.iloc[0]["student_id"])

    df = load_grades()
    validate_grade_columns(df)

    filtered_df = filter_grades(df, student_id, course_code)
    handle_empty_grades(filtered_df, "user_code", user_code, course_code)

    return filtered_df.to_dict(orient="records")

@app.get("/chat")
def chat(message: str):
    parts = message.strip().split()

    if not parts: 
        raise HTTPException(status_code=400, detail="Empty message")
    
    command = parts[0].lower()

    if command == "help":
        return{
            "response":(
                "Available commands:\n"
                "help\n"
                "login <user_code>\n"
                "grades <user_code>\n"
                "grades <user_code> <course_code>"
            )
        }
    elif command == "login":
        if len(parts) < 2:
            raise HTTPException(status_code=400, detail="Usage: login <user_code>")
        
        user_code = parts[1]
        df_users = load_users()

        user = df_users[df_users["user_code"] == user_code]

        if user.empty:
            raise HTTPException(status_code=404, detail="User not found")
        
        student_name = user.iloc[0]["student_name"]
        student_id = int(user.iloc[0]["student_id"])

        return {
            "response": f"Login successful for {student_name} (student_id: {student_id})"
        }
    
    elif command == "grades":
        if len(parts) < 2:
            raise HTTPException(status_code=400, detail="Usage: grades <user_code> [course_code]")
        
        user_code = parts[1]
        course_code = parts[2] if len(parts) >= 3 else None

        df_users = load_users()
        user = df_users[df_users["user_code"] == user_code]

        if user.empty:
            raise HTTPException(status_code=404, detail="User not found")
        
        student_id = int(user.iloc[0]["student_id"])
        student_name = user.iloc[0]["student_name"]

        df = load_grades()
        validate_grade_columns(df)

        filtered_df = filter_grades(df, student_id, course_code)
        handle_empty_grades(filtered_df, "user_code", user_code, course_code)

        lines = [f"Grades for {student_name}:"]
        for _, row in filtered_df.iterrows():
            lines.append(
                f"{row['course_code']} ->"
                f"CA: {row['continuous_assessment']}, "
                f"Exam:{row['exam_grade']}"
                f"Final:{row['final_grade']}"
            )

        return {
            
            "response": "\n".join(lines)
        }
    else:
        raise HTTPException(status_code=400,
                            detail="Unknown command. Type 'help' to see available commands."
                            )
    


'''
the path on terminal should be the root of the project, where the app folder is located run the following command to start the server: uvicorn app.main:app --reload

in my case the path is: C:\\Users\\HP\\Desktop\\chatbot> python -m uvicorn app.main:app --reload

'''