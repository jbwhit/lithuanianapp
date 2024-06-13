import pandas as pd
import solara

# Load the data from CSV files
pronouns_df = pd.read_csv("data/pronouns.csv")
numbers_df = pd.read_csv("data/numbers.csv")

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
