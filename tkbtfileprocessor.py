import sys
import pandas as pd
import re
import jaconv
import requests
from datetime import datetime


def main():

    #load csv file
    df = input_file()
    
    #choose cols to keep in df
    keep_cols = ["Word", "Translation"]
    df = df[keep_cols]

    #format df - create new cols, extract and input data accordingly, order columns
    df = format_df(df, df["Word"])

    #format text in Translation column - ", , " separates alt. translations/meanings
    df["Translation"] = df["Translation"].apply(lambda x: re.sub(r', , ', ' OR ', x))

    #write to csv
    output_file(df)


def input_file():

    if len(sys.argv) < 2:

        sys.exit("Missing raw file.")
    
    elif len(sys.argv) > 3:

        sys.exit("Too many inputs.")

    return pd.read_csv(sys.argv[1])


def output_file(df):

    if len(sys.argv) != 3:

        #set name of new csv file to current time and date
        current_datetime = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        file_name = current_datetime + ".csv"

        #output csv file
        df.to_csv(file_name, index = False)

    else:

        #output csv file
        df.to_csv(sys.argv[2], index = False)


def format_df(df, col):

    """
    This function takes a pandas dataframe and the column containing text data on words (e.g. df["Word"]) as input.

    This function creates new columns in the dataframe and fills them with relevant data using 3 helper functions:

    get_user_input(): Gets user input. User input determines columns created.

    get_data(): Gets relevant data for each new column, except Parts of Speech (pos).

    get_pos(): Gets pos data for pos column.

    Returns a pandas dataframe with ordered columns.
    """

    #final col order of df, assuming all cols are created and none were dropped beforehand
    col_order = [
        "List",
        "Word",
        "Pronunciation",
        "Romanisation",
        "Alternate Forms",
        "Parts of Speech",
        "Translation",
        ]

    #options for user
    options = {
        "word": "Word_new",
        "pr": "Pronunciation",
        "roma": "Romanisation",
        "alt": "Alternate Forms",
    }

    user_input = get_user_input()

    if "all" in user_input:

        for opt in options:

            #create new cols and input relevant data
            df[options[opt]] = col.apply(lambda x: get_data(x, opt))

        #create Parts of Speech (pos) col and get pos data
        df["Parts of Speech"] = col.apply(lambda x: get_pos(x))

    else:

        for opt in options:

            if opt in user_input:

                #create new cols and input relevant data
                df[options[opt]] = col.apply(lambda x: get_data(x, opt))

        if "pos" in user_input:

            #create pos col and get pos data
            df["Parts of Speech"] = col.apply(lambda x: get_pos(x))

    #if new Word col created, drop old Word col
    if "Word_new" in df:

        df = df.drop(["Word"], axis = 1)
        df = df.rename(columns = {"Word_new": "Word"})

    #edit col_order to align with cols in df
    col_order = list(filter(lambda x: x in df, col_order))

    #order cols in df
    df = df[col_order]

    return df


def get_user_input():

    """
    This function gets user input for format_df() and checks validity.

    Reprompts when invalid input is detected.

    Returns valid user input as a string.
    """

    accepted_inputs = [
        "word",
        "pr",
        "alt",
        "roma",
        "pos",
        "all",
    ]

    true_false = []

    user_input = input("Which columns? Input cols (word, pr, alt, roma, pos, or all) separated by whitespace. ").lower()

    while sum(true_false) < 1:

        #check that all characters in user_input are valid
        if re.fullmatch(r'[wordpaltms ]+', user_input):

            #verify validity of each "col" in user input
            for col in user_input.split():

                if col.strip() in accepted_inputs:

                    true_false.append(True)

                else:

                    true_false.append(False)

            #if all col inputs are true, return user input
            if all(true_false):

                return user_input

        #if input invalid, reset true_false and reprompt user
        print("Invalid input detected.")
        true_false = []
        user_input = input("Which columns? Input cols (word, pr, alt, roma, pos, or all) separated by whitespace. ").lower()


def get_data(text, mode):

    """
    This function extracts text from text data outputted by a dictionary app.

    Typical structure of text data: "word, pronunciation, alternate forms" (e.g. "締め上げる, しめあげる, 絞め上げる"). Pronunciation and alternate forms are not always available.

    This function has 4 different outputs depending on the mode:

    word - returns word
    pr - returns pronunciation for non-hiragana words if present in text, else returns "-"
    alt - returns alternate forms if present in text, else returns "-". the hiragana form is recognised as an alternate form for katakana words and vice versa.
    romaji - returns pronunciation of the word in its romanised form if word or pronunciation outputs are syllabic in nature, else returns "-"

    Example outputs:

    居眠り: word > 居眠り, pr > -, alt > -, roma > -
    居眠り, いねむり: word > 居眠り, pr > いねむり, alt > -, roma > inemuri
    居眠り, いねむり, 居睡り: word > 居眠り, pr > いねむり, alt > 居睡り, roma > inemuri

    しがない: word > しがない, pr > -, alt > -, roma > shiganai
    でか, デカ: word > でか, pr > -, alt > デカ, roma > deka
    ズキズキ, ずきずき: word > ズキズキ, pr > ずきずき, alt > ずきずき, roma > zukizuki

    This function calls on one helper function: check_kana(). Check_kana() checks if a given string contains hiragana or katakana.
    """

    #capture word, pronunciation and alternate forms from data entries in Word col
    result = re.match(r'([一-龯ぁ-んァ-ン]+),? ?([ぁ-んァ-ン]+)?,? ?([一-龯ぁ-んァ-ンー, ]+)*', text)
    word, pr, alt = result.groups()

    #adjust output according to different modes
    match mode:

        case "word":

            return word

        case "pr":

            if pr is not None:

                #check pr for hiragana
                if check_kana(pr, "hira"):

                    #convert any katakana in pr to hiragana
                    pr = jaconv.kata2hira(pr)
                    return pr

                else:

                    return "-"

            return "-"

        case "roma":

            if pr is not None:

                #convert pronunciation text to romanised form
                pr = jaconv.kata2hira(pr)
                pr = jaconv.kana2alphabet(pr)
                return pr

            elif re.fullmatch(r'[ぁ-んァ-ン]+', word):

                #convert word text to romanised form
                word = jaconv.kata2hira(word)
                word = jaconv.kana2alphabet(word)
                return word

            return "-"

        case "alt":

            if alt is not None:

                #check pr and word for katakana
                if check_kana(pr, "kata") or check_kana(word, "kata"):

                    return f"{pr}, {alt}"

                return alt

            else:

                #check pr and word for katakana
                if check_kana(pr, "kata") or check_kana(word, "kata"):

                    return pr

                return "-"

        case _:

            sys.exit("Invalid input in get_data().")


def check_kana(text, form):

    """
    This function checks whether input text contains hiragana or katakana.
    """

    try:

        if form == "hira":

            #checks that text contains hiragana
            if re.search(r'[ぁ-ん]+', text):

                return True

            return False

        elif form == "kata":

            #checks that text contains katakana
            if re.search(r'[ァ-ン]+', text):

                return True

            return False

    except TypeError:

        pass


def get_pos(text):

    """
    This function takes the input text (a word), calls the jisho.org api, and returns the parts of speech of the word as a string.
    """

    #call jisho.org (online japanese-english dictionary) api
    response = requests.get("https://jisho.org/api/v1/search/words?keyword=" + str(text))
    output = response.json()

    #output is a dict with 2 key-values pairs
    #key 1 is 'meta', value is a dict which contains status (200, 404 etc.)
    #key 2 is 'data', value is a list of dicts. the 0th dict contains data on the exact word we are querying

    data = output["data"][0]

    #in data (variable), there is a key-value pair with key 'sense'. the value is a list containing a dict
    #this dict contains the 'parts_of_speech' key-value pair

    pos = data["senses"][0]["parts_of_speech"]

    #format the pos output
    pos_final = ", ".join(pos).lower()

    return pos_final


if __name__ == "__main__":
    main()