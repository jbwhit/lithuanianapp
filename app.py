import pandas as pd
import solara

# Load the data from CSV files
pronouns_df = pd.read_csv("lithuanianapp/lithuanianapp/pronouns.csv")
numbers_df = pd.read_csv("lithuanianapp/lithuanianapp/numbers.csv")

# Function to get a random nominative pronoun and a number
def get_random_exercise():
    nominative_pronoun = pronouns_df.sample(1).iloc[0]
    number_row = numbers_df.sample(1).iloc[0]
    return nominative_pronoun, number_row

# Function to fetch the dative and compound year
def get_answer(nominative_pronoun, number_row):
    dative = pronouns_df.loc[pronouns_df['nominative'] == nominative_pronoun['nominative'], 'dative'].values[0]
    year_phrase = f"{number_row['neoficialiai']} {number_row['compound']} {number_row['years']}" if pd.notna(number_row['compound']) else f"{number_row['neoficialiai']} {number_row['years']}"
    return f"{dative.title()} {year_phrase}."

@solara.component
def Page():
    # State to hold the current exercise
    nominative_pronoun, set_nominative_pronoun = solara.use_state(None)
    number_row, set_number_row = solara.use_state(None)
    show_answer, set_show_answer = solara.use_state(False)
    answers, set_answers = solara.use_state([])  # State to hold the history of answers
    
    if nominative_pronoun is None or number_row is None:
        nominative_pronoun, number_row = get_random_exercise()
        set_nominative_pronoun(nominative_pronoun)
        set_number_row(number_row)

    exercise_text = f"{nominative_pronoun['nominative']}, {number_row['number']}"
    answer_text = get_answer(nominative_pronoun, number_row)
    

    with solara.Column(gap="10px"):
        # Display the exercise
        solara.Markdown(f"### Exercise: {exercise_text}")
        
        # Button to reveal the answer
        if solara.Button("Reveal Answer", on_click=lambda: set_show_answer(True)):
            if show_answer:
                solara.Markdown(f"**Answer:** {answer_text}")
                # Buttons to record whether the answer was correct or incorrect
                with solara.Row():
                    solara.Button("Correct", on_click=lambda: set_answers(answers + [(exercise_text, answer_text, True)]), color='blue')
                    solara.Button("Incorrect", on_click=lambda: set_answers(answers + [(exercise_text, answer_text, False)]), color='red')
                
                # Button to move to the next question
                with solara.Row():
                    solara.Button("Next Question", on_click=lambda: (
                        set_nominative_pronoun(None), 
                        set_number_row(None), 
                        set_show_answer(False)
                    ))
        
        # Display the history of answers
        solara.Markdown("### History of Answers")
        for exercise, answer, correct in answers:
            result_text = "Correct" if correct else "Incorrect"
            solara.Markdown(f"- {exercise} -> {answer} ({result_text})")
