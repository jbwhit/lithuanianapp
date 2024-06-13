import solara
from utilities import get_random_exercise, get_answer

@solara.component
def AnswerHistory(answers):
    with solara.Card():
        solara.Markdown("### History of Answers")
        for exercise, answer, correct in answers:
            result_text = "Correct" if correct else "Incorrect"
            solara.Markdown(f"- {exercise} -> {answer} ({result_text})")

@solara.component
def ProgressTracker(answers):
    total_exercises = len(answers)
    correct_answers = sum(1 for _, _, correct in answers if correct)
    incorrect_answers = total_exercises - correct_answers
    accuracy = (correct_answers / total_exercises) * 100 if total_exercises > 0 else 0

    with solara.Card():
        solara.Markdown("### Progress")
        solara.Markdown(f"Total Exercises: {total_exercises}")
        solara.Markdown(f"Correct Answers: {correct_answers}")
        solara.Markdown(f"Incorrect Answers: {incorrect_answers}")
        solara.Markdown(f"Accuracy: {accuracy:.2f}%")

        # with solara.ProgressLinear(value=accuracy, color="blue"):
        #     pass

@solara.component
def Page():
    nominative_pronoun, set_nominative_pronoun = solara.use_state(None)
    number_row, set_number_row = solara.use_state(None)
    show_answer, set_show_answer = solara.use_state(False)
    answers, set_answers = solara.use_state([])

    if nominative_pronoun is None or number_row is None:
        nominative_pronoun, number_row = get_random_exercise()
        set_nominative_pronoun(nominative_pronoun)
        set_number_row(number_row)

    exercise_text = f"{nominative_pronoun['nominative']}, {number_row['number']}"
    answer_text = get_answer(nominative_pronoun, number_row)

    with solara.Column(gap="20px"):
        with solara.Card():
            solara.Markdown(f"### Exercise: {exercise_text}")

            if solara.Button("Reveal Answer", on_click=lambda: set_show_answer(True)):
                if show_answer:
                    solara.Markdown(f"**Answer:** {answer_text}")
                    with solara.Row(gap="10px"):
                        solara.Button("Correct", on_click=lambda: set_answers(answers + [(exercise_text, answer_text, True)]), color='green')
                        solara.Button("Incorrect", on_click=lambda: set_answers(answers + [(exercise_text, answer_text, False)]), color='red')

                    with solara.Row(gap="10px"):
                        solara.Button("Next Question", on_click=lambda: (
                            set_nominative_pronoun(None),
                            set_number_row(None),
                            set_show_answer(False)
                        ))

        ProgressTracker(answers)
        AnswerHistory(answers)