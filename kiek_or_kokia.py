import solara
import pandas as pd
from io import StringIO
import csv
from typing import List, Tuple
import base64
import random

# Load the data from CSV file (adjust the URL to your actual data source)
numbers_df = pd.read_csv("https://raw.githubusercontent.com/jbwhit/lithuanianapp/main/numbers.csv")

def get_random_price_exercise() -> Tuple[str, str, pd.Series]:
    number_row = numbers_df.sample(1).iloc[0]
    price = f"€{number_row['number']}"
    exercise_type = random.choice(["kokia", "kiek"])
    item = random.choice(["knyga", "puodelis", "marškinėliai", "žurnalas", "kepurė"]) if exercise_type == "kiek" else None
    return exercise_type, price, item, number_row

def get_price_answer(exercise_type: str, number_row: pd.Series) -> str:
    if exercise_type == "kokia":
        if pd.notna(number_row['kokia_kaina_compound']):
            price_phrase = f"Kokia: {number_row['kokia_kaina']} {number_row['kokia_kaina_compound']} {number_row['euro_nom']}."
        else:
            price_phrase = f"Kokia: {number_row['kokia_kaina']} {number_row['euro_nom']}."
    else:  # kiek
        if pd.notna(number_row['kiek_kainuoja_compound']):
            price_phrase = f"Kiek: {number_row['kiek_kainuoja']} {number_row['kiek_kainuoja_compound']} {number_row['euro_acc']}."
        else:
            price_phrase = f"Kiek: {number_row['kiek_kainuoja']} {number_row['euro_acc']}."
    return price_phrase.capitalize()

@solara.component
def AnswerHistory(answers: List[Tuple[str, str, str, bool]]):
    with solara.Card("Answer History", margin=10):
        for exercise, user_guess, correct_answer, is_correct in answers:
            result_text = "✅ Correct" if is_correct else "❌ Incorrect"
            solara.Markdown(f"- **{exercise}**\n  Your answer: {user_guess}\n  Correct answer: {correct_answer}\n  ({result_text})")

@solara.component
def ProgressTracker(answers: List[Tuple[str, str, str, bool]]):
    total_exercises = len(answers)
    correct_answers = sum(1 for _, _, _, correct in answers if correct)
    incorrect_answers = total_exercises - correct_answers
    accuracy = (correct_answers / total_exercises) * 100 if total_exercises > 0 else 0

    with solara.Card("Progress", margin=10):
        solara.Markdown(f"Total Exercises: {total_exercises}")
        solara.Markdown(f"Correct Answers: {correct_answers}")
        solara.Markdown(f"Incorrect Answers: {incorrect_answers}")
        solara.Markdown(f"Accuracy: {accuracy:.2f}%")
        solara.ProgressLinear(value=accuracy, color="success")

def export_to_csv(answers: List[Tuple[str, str, str, bool]]) -> str:
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Prompt", "User's Answer", "Correct Answer", "Is Correct"])
    for exercise, user_guess, correct_answer, is_correct in answers:
        writer.writerow([exercise, user_guess, correct_answer, "Yes" if is_correct else "No"])
    return output.getvalue()

@solara.component
def Page():
    exercise_type, set_exercise_type = solara.use_state(None)
    price, set_price = solara.use_state(None)
    item, set_item = solara.use_state(None)
    number_row, set_number_row = solara.use_state(None)
    show_answer, set_show_answer = solara.use_state(False)
    answers, set_answers = solara.use_state([])
    user_answer, set_user_answer = solara.use_state("")
    csv_download_link, set_csv_download_link = solara.use_state("")

    def generate_download_link():
        csv_content = export_to_csv(answers)
        b64 = base64.b64encode(csv_content.encode()).decode()
        href = f"data:text/csv;base64,{b64}"
        set_csv_download_link(href)

    def new_exercise():
        new_exercise_type, new_price, new_item, new_number_row = get_random_price_exercise()
        set_exercise_type(new_exercise_type)
        set_price(new_price)
        set_item(new_item)
        set_number_row(new_number_row)
        set_show_answer(False)
        set_user_answer("")
        set_csv_download_link("")

    if exercise_type is None or price is None or number_row is None:
        new_exercise()

    exercise_text = f"Kokia kaina? {price}" if exercise_type == "kokia" else f"Kiek kainuoja {item}? {price}"
    correct_answer = get_price_answer(exercise_type, number_row) if number_row is not None else ""

    def check_answer():
        user_answer_stripped = user_answer.strip().lower().strip('.')
        correct_answer_stripped = correct_answer.split(': ', 1)[1].strip().lower().strip('.')
        is_correct = user_answer_stripped == correct_answer_stripped
        set_answers(answers + [(exercise_text, user_answer, correct_answer, is_correct)])
        set_show_answer(True)
        set_csv_download_link("")

    def reset_progress():
        set_answers([])
        set_csv_download_link("")
        new_exercise()

    with solara.Column(align="center", gap="20px"):
        with solara.Row(justify="center", gap="20px"):
            # Left Column
            with solara.Column(gap="20px", classes=["w-1/2"]):
                with solara.Card("Exercise", margin=10):
                    solara.Markdown(f"### {exercise_text}")
                    solara.InputText(label="Your answer", value=user_answer, on_value=set_user_answer)
                    if show_answer:
                        result = "Correct! 🎉" if answers[-1][3] else "Incorrect. Try again! 💪"
                        solara.Info(f"{result} The correct answer is: {correct_answer}")
                AnswerHistory(answers)

            # Right Column
            with solara.Column(gap="20px", classes=["w-1/2"]):
                with solara.Card("Controls", margin=10):
                    with solara.Column(gap="10px"):
                        solara.Button("Check Answer", on_click=check_answer, disabled=show_answer)
                        solara.Button("Next Question", on_click=new_exercise, disabled=not show_answer)
                        solara.Button("Reset Progress", on_click=reset_progress, color="error")
                        if answers:
                            solara.Button("Generate CSV Download Link", on_click=generate_download_link)
                            if csv_download_link:
                                solara.Markdown(f"[Download CSV]({csv_download_link})")
                
                if answers:
                    ProgressTracker(answers)
                else:
                    solara.Info("Start answering questions to see your progress!")