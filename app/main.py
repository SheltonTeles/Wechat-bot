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
    message = message.strip()

    if not message:
        raise HTTPException(status_code=400, detail="Empty message")

    parts = message.split()
    lowered_parts = [part.lower() for part in parts]

    if "help" in lowered_parts:
        return {
            "response": (
                "Available commands:\n"
                "help\n"
                "login <user_code>\n"
                "grades <user_code>\n"
                "grades <user_code> <course_code>\n"
                "You can also try:\n"
                "show grades <user_code>\n"
                "get grades <user_code> <course_code>"
            )
        }

    elif "login" in lowered_parts:
        login_index = lowered_parts.index("login")
        user_input = " ".join(parts[login_index + 1:]).strip().lower()

        if not user_input:
            raise HTTPException(status_code=400, detail="Usage: login <user_code>")

        df_users = load_users()
        df_users["user_code_clean"] = (
            df_users["user_code"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        user = df_users[df_users["user_code_clean"] == user_input]

        if user.empty:
            raise HTTPException(status_code=404, detail="User not found")

        student_name = user.iloc[0]["student_name"]
        student_id = int(user.iloc[0]["student_id"])

        return {
            "response": f"Login successful for {student_name} (student_id: {student_id})"
        }

    elif "grades" in lowered_parts:
        grades_index = lowered_parts.index("grades")
        remaining_parts = parts[grades_index + 1:]

        # remove filler words if they appear after "grades"
        filler_words = {"for", "of", "my"}
        remaining_parts = [p for p in remaining_parts if p.lower() not in filler_words]

        if not remaining_parts:
            raise HTTPException(
                status_code=400,
                detail="Usage: grades <user_code> [course_code]"
            )

        possible_last = remaining_parts[-1]

        if len(remaining_parts) >= 2 and (
            possible_last.isupper() or any(ch.isdigit() for ch in possible_last)
        ):
            course_code = possible_last.strip().upper()
            user_input = " ".join(remaining_parts[:-1]).strip().lower()
        else:
            course_code = None
            user_input = " ".join(remaining_parts).strip().lower()

        df_users = load_users()
        df_users["user_code_clean"] = (
            df_users["user_code"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        user = df_users[df_users["user_code_clean"] == user_input]

        if user.empty:
            raise HTTPException(status_code=404, detail="User not found")

        student_id = int(user.iloc[0]["student_id"])
        student_name = user.iloc[0]["student_name"]

        df = load_grades()
        validate_grade_columns(df)
        df["course_code"] = df["course_code"].astype(str).str.strip().str.upper()

        filtered_df = filter_grades(df, student_id, course_code)
        handle_empty_grades(filtered_df, "user_code", user_input, course_code)

        lines = [f"Grades for {student_name}:"]
        for _, row in filtered_df.iterrows():
            lines.append(
                f"{row['course_code']} -> "
                f"CA: {row['continuous_assessment']}, "
                f"Exam: {row['exam_grade']}, "
                f"Final: {row['final_grade']}"
            )

        return {
            "response": "\n".join(lines)
        }

    else:
        raise HTTPException(
            status_code=400,
            detail="Unknown command. Type 'help' to see available commands."
        )
    


'''
the path on terminal should be the root of the project, where the app folder is located run the following command to start the server: uvicorn app.main:app --reload

in my case the path is: C:\\Users\\HP\\Desktop\\chatbot> python -m uvicorn app.main:app --reload

'''