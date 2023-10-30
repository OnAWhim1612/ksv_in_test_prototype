import streamlit as st
import pandas as pd
import os
import json
import numpy as np
import time


# Define username and password for admin and participant access
admin_username = "admin"
admin_password = "54321"
participant_username = "register"
participant_password = "12345"

junior_judge_credentials = {
        "Junior_judge1": "JJ1OODKSV",
        "Junior_judge2": "JJ2OODKSV",
        "Junior_judge3": "JJ3OODKSV"
    }


# Initialize the control_db with default values
control_db = {
    "Registration Juniors": {"status": True, "toggle": True},
    "Registration Sub Juniors": {"status": True, "toggle": True},
    "Registration Seniors": {"status": True, "toggle": True},
    "Registration Super Seniors": {"status": True, "toggle": True},
    "Finals": {"status": True, "toggle": True},
}

# File path for storing Category 1 data
juniors_data_file = "juniors_data.csv"
# File path for storing category status
category_status_file = "category_status.json"
scoring_criteria_file = "scoring.csv"



# Load or initialize Category 1 data
if os.path.exists(juniors_data_file):
    prelims_jun_all = pd.read_csv(juniors_data_file)
else:
    prelims_jun_all = pd.DataFrame(columns=["Name", "School", "Attendance"])

# Load or initialize category statuses from a JSON file
if os.path.exists(category_status_file):
    with open(category_status_file, "r") as file:
        control_db = json.load(file)

# Define a function to save control_db to a JSON file
def save_control_db_to_file():
    with open(category_status_file, "w") as file:
        json.dump(control_db, file)

# Define a function to save prelims_1_all data to a CSV file
def save_prelims_jun_all_to_csv(data):
    data.to_csv(juniors_data_file, index=False)

st.markdown(
    """
    <style>
    .sidebar .sidebar-content {
        background-color: #333;
        color: white;
        padding: 20px;
    }
    .sidebar .sidebar-content a {
        display: block;
        padding: 10px 0;
        color: white;
        text-decoration: none;
    }
    .sidebar .sidebar-content a:hover {
        background-color: #555;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def admin_panel():
    st.write("Welcome to the Admin Panel")
    selected_page = st.sidebar.radio("Navigate", ["Control Panel", "Juniors", "Sub Juniors", "Seniors", "Super Seniors", "Finals"])

    if selected_page == "Control Panel":
        control_panel()
    elif selected_page == "Juniors":
        jun_admin()



def generate_scoresheet():
    # Check if the required files exist
    if not os.path.exists('roster_prelim_jun.csv'):
        st.write("Roster file is missing. Please prepare the roster before generating the scoresheet.")
        return

    # Load the roster from roster_prelim_cat1.csv
    roster_df = pd.read_csv('roster_prelim_jun.csv')

    # Create a list of judges (You can modify this to add more judges)
    judges = ['judge1', 'judge2', 'judge3']

    # Check if the scoring criteria file exists
    if not os.path.exists(scoring_criteria_file):
        st.write("Scoring criteria file is missing. Please upload it.")
        return

    # Load scoring criteria from scoring.csv
    scoring_df = pd.read_csv(scoring_criteria_file)

    # Create an empty scoresheet DataFrame
    scoresheet = roster_df[['Name', 'School']].copy()

    # Add columns for each judge's scores based on criteria

    # Save the generated scoresheet to scoresheet_cat_1.csv
    scoresheet.to_csv('scoresheet_jun.csv', index=False)
    st.write("Scoresheet generated successfully.")





def control_panel():
    st.title("Control Panel")
    for reg_category, data in control_db.items():
        data["toggle"] = st.checkbox(reg_category, data["toggle"])
        data["status"] = data["toggle"]
        # Save the updated status
        save_control_db_to_file()

    st.title("Scoring Criteria")
    scoring_criteria = st.file_uploader("Upload a spreadsheet of scoring criteria", type=["csv", "xlsx"])
    if scoring_criteria is not None:
        # Read the uploaded file
        scoring_df = pd.read_excel(scoring_criteria)  # Modify according to your data format
        # Save the scoring criteria to a new CSV file or replace the existing one
        scoring_df.to_csv(scoring_criteria_file, index=False)


    if os.path.exists(scoring_criteria_file):
        scoring_df = pd.read_csv(scoring_criteria_file)
        st.dataframe(scoring_df)
    else:
        st.write("No scoring criteria uploaded.")

@st.cache
def load_prelims_jun_all():
    return pd.DataFrame(columns=["Name", "School", "Attendance"])


def jun_admin():
    global prelims_jun_all  # Add this line to indicate that prelims_1_all is a global variable
    st.title("Category 1")
    st.write("Upload a spreadsheet with participant names and school names.")

    # File uploader
    uploaded_file = st.file_uploader("Upload a spreadsheet", type=["csv", "xlsx"])

    if uploaded_file is not None:
        if st.button("Process and Save"):
            data = pd.read_excel(uploaded_file)  # Modify this according to your data format (csv, xlsx, etc.)

            # Clear the existing data and replace it with the new data
            prelims_jun_all = data
            # Save the data to the CSV file
            save_prelims_jun_all_to_csv(prelims_jun_all)

    st.title("Juniors All")
    st.dataframe(prelims_jun_all)
    # "Generate Roster" button
    if st.button("Generate Roster"):
        # Filter participants with 'Present' status
        present_participants = prelims_jun_all[prelims_jun_all['Attendance'] == 'Present']

        if not present_participants.empty:
            # Save the roster as CSV without the 'Attendance' column
            present_participants.drop(columns=['Attendance'], inplace=True)
            present_participants.to_csv('roster_prelim_jun.csv', index=False)
            st.write("Generated Roster:")
            st.dataframe(present_participants)

        else:
            st.write("No participants with 'Present' status. Roster not generated.")

    if st.button("Generate Scoresheet"):
        generate_scoresheet()

    if os.path.exists('scoresheet_jun.csv'):
        scoresheet = pd.read_csv('scoresheet_jun.csv')

        # Check if 'Total' column already exists, if not, calculate and save the totals in the CSV
        if 'Total' not in scoresheet.columns:
            scoresheet['Total'] = scoresheet.iloc[:, 2:].sum(axis=1)
            scoresheet.to_csv('scoresheet_jun.csv', index=False)  # Save the 'Total' column in the CSV

        st.write("Scoresheet:")
        st.dataframe(scoresheet)

        # Add a button to download the scoresheet
        with open('scoresheet_jun.csv', 'rb') as file:
            data = file.read()
        st.download_button(
            label="Download Scoresheet",
            data=data,
            key="scoresheet_jun.csv",
            file_name="scoresheet_jun.csv",
        )

        if st.button("Refresh Scoresheet"):
            scoresheet = pd.read_csv('scoresheet_jun.csv')

            # Calculate Total column, excluding first two columns and the 'Total' column itself
            cols_to_sum = [col for col in scoresheet.columns if col not in ['Name', 'School', 'Total']]
            scoresheet['Total'] = scoresheet[cols_to_sum].sum(axis=1)

            scoresheet.to_csv('scoresheet_jun.csv', index=False)
            st.write("Scoresheet Reloaded:")
            st.dataframe(scoresheet)

    juniors_judging_file = "juniors_judging_status.json"
    if os.path.exists(juniors_judging_file):
        with open(juniors_judging_file, "r") as file:
            current_judging_status = json.load(file)
    else:
        current_judging_status = {"status": False}  # Set the default status if the file doesn't exist

    # Toggle judging status only if it doesn't exist or explicitly set by the user
    judging_status = st.checkbox('Open Judging', current_judging_status.get("status", False))

    # Update the judging status only if changed explicitly by the user
    if current_judging_status.get("status") is None or current_judging_status.get("status") != judging_status:
        current_judging_status["status"] = judging_status

        # Save the updated judging status to the file
        with open(juniors_judging_file, "w") as file:
            json.dump(current_judging_status, file)

    st.write("Judging Status: " + ("Open" if judging_status else "Closed"))

    if st.button("Generate Finalists"):
        judging_status_file = "juniors_judging_status.json"
        finalists_file = "jun_finalists.csv"
        all_participants_file = "jun_all_participants.csv"

        with open(judging_status_file, "r") as file:
            current_judging_status = json.load(file)

        if current_judging_status.get("status", False):
            st.write("Judging is still open. Cannot generate finalists until judging is closed.")
        else:
            if os.path.exists('scoresheet_jun.csv'):
                scoresheet = pd.read_csv('scoresheet_jun.csv')
                if 'Total' not in scoresheet.columns:
                    st.write("Total column not found in the scoresheet.")
                else:
                    # Creating sum columns for tie-breakers (if columns don't exist)
                    tie_breaker_cols = ['Voice Modulation', 'Clarity', 'Pronunciation']
                    for col in tie_breaker_cols:
                        for judge in range(1, 4):
                            scoresheet[f'judge{judge} {col}'] = scoresheet.filter(like=f'judge{judge} {col}').sum(
                                axis=1)

                    top_5 = scoresheet.nlargest(5, 'Total')

                    # Sorting the top 5 based on tie-breakers
                    top_5 = top_5.sort_values(
                        ['judge1 Voice Modulation', 'judge2 Voice Modulation', 'judge3 Voice Modulation',
                         'judge1 Clarity', 'judge2 Clarity', 'judge3 Clarity',
                         'judge1 Pronunciation', 'judge2 Pronunciation', 'judge3 Pronunciation'],
                        ascending=False)

                    # Assign ranks to the participants
                    top_5['Rank'] = range(1, len(top_5) + 1)

                    # Save the top 5 finalists to a CSV file (with only required columns)
                    finalists_data = top_5[['Name', 'School', 'Total', 'Rank']]
                    finalists_data.to_csv(finalists_file, index=False)
                    st.write("Top 5 finalists generated and saved to jun_finalists.csv.")

                    # Save details of all participants (with only required columns)
                    all_participants_data = scoresheet[['Name', 'School', 'Total']]
                    all_participants_data['Rank'] = all_participants_data['Total'].rank(method='min', ascending=False)
                    all_participants_data.to_csv(all_participants_file, index=False)
                    st.write("All participants' details saved to jun_all_participants.csv.")

                    # Generate individual files for each participant with their ranks and totals
                    for _, participant in top_5.iterrows():
                        file_name = f"{participant['Name']}_{participant['School']}_details.csv"
                        participant_data = participant[['Name', 'School', 'Total', 'Rank']]
                        participant_data.to_csv(file_name, index=False)

                    st.write("Individual participant files with ranks and totals generated.")

                    st.download_button(label="Download Finalists", data=open(finalists_file, 'rb'),
                                       file_name='jun_finalists.csv')
                    st.download_button(label="Download All Participants", data=open(all_participants_file, 'rb'),
                                       file_name='jun_all_participants.csv')

                    for _, participant in top_5.iterrows():
                        file_name = f"{participant['Name']}_{participant['School']}_details.csv"
                        st.download_button(label=f"Download {participant['Name']} - {participant['School']} Details",
                                           data=open(file_name, 'rb'), file_name=file_name)
            else:
                st.write("Scoresheet not found. Please generate the scoresheet first.")



def registration_panel():
    st.write("Welcome to the Registration Panel")
    selected_page = st.sidebar.radio("Navigate", ["Registration Juniors", "Registration Sub Juniors", "Registration Seniors", "Registration Category 4", "Finals"])
    status_message = "Registrations Open" if control_db.get(selected_page, {}).get("status", True) else "Registrations Closed"
    st.write(f"{selected_page}: {status_message}")

    if selected_page == "Registration Juniors" and control_db["Registration Juniors"]["status"]:
        st.title("Select a participant to register:")
        selected_participant = st.selectbox("Choose a participant",
                                            [f"{row['Name']}, {row['School']}" for _, row in prelims_jun_all.iterrows()])
        if st.button("Register"):
            selected_name, selected_school = selected_participant.split(", ")
            # Update the attendance status for the selected participant
            prelims_jun_all.loc[(prelims_jun_all['Name'] == selected_name) & (
                        prelims_jun_all['School'] == selected_school), 'Attendance'] = "Present"
            # Save the data to the CSV file
            save_prelims_jun_all_to_csv(prelims_jun_all)
            st.write(f"Registered {selected_name} from {selected_school}")





def junior_judge_panel(username):
    judging_status_file = "juniors_judging_status.json"

    with open(judging_status_file, "r") as file:
        current_judging_status = json.load(file)

    if not current_judging_status.get("status", False):
        st.write("Judging is not currently Open. Please wait.")
        return

    scoresheet_file = "scoresheet_jun.csv"
    scoring_file = "scoring.csv"
    judge_file = f"prelim_jun_{username.split('_')[1]}.csv"

    scoresheet = pd.read_csv(scoresheet_file)
    scoring_df = pd.read_csv(scoring_file)

    st.write(f"Welcome {username} to the Junior Judge Panel")

    selected_page = st.sidebar.radio("Navigate", ["Score", "Overview"])

    if selected_page == "Score":
        selected_participant = st.selectbox("Choose a participant", scoresheet["Name"] + ", " + scoresheet["School"])

        if selected_participant:
            participant_index = scoresheet[(scoresheet["Name"] + ", " + scoresheet["School"]) == selected_participant].index[0]
            for criteria, pos_neg, score in zip(scoring_df["Criteria"], scoring_df["Pos/ Neg"], scoring_df["Score"]):
                if pos_neg == "Pos":
                    score_value = st.slider(criteria, 0, score, 0)
                else:
                    score_value = st.slider(criteria, score, 0, 0) # Modified line to handle negative scores correctly
                scoresheet.at[participant_index, f"{username.split('_')[1]} {criteria}"] = score_value

            if st.button("Submit"):
                scoresheet.to_csv(scoresheet_file, index=False)
                judge_scores = scoresheet[["Name", "School"] + [col for col in scoresheet.columns if username.split('_')[1] in col]]
                judge_scores["Total"] = judge_scores[[col for col in judge_scores.columns if username.split('_')[1] in col and col != "Total"]].sum(axis=1)
                judge_scores.to_csv(judge_file, index=False)
                st.write("Scores submitted successfully.")

    elif selected_page == "Overview":
        if os.path.exists(judge_file):
            judge_scores = pd.read_csv(judge_file)
            positive_columns = [col for col in judge_scores.columns if username.split('_')[1] in col and col != "Total" and not col.startswith("Judge")]
            judge_scores["Total"] = judge_scores[positive_columns].sum(axis=1) - judge_scores[[col for col in judge_scores.columns if "Neg" in col]].sum(axis=1)
            st.write("Overview of Scores:")
            st.dataframe(judge_scores)
        else:
            st.write("No scores available yet.")


def update_score(selected_participant, selected_score, score, score_sheet):
    name, school = selected_participant.split(', ')
    score_sheet.loc[(score_sheet['Name'] == name) & (score_sheet['School'] == school), selected_score] = score
    score_sheet.to_csv('scoresheet_jun.csv', index=False)


def main():
    st.title("KSV Interface")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if (username, password) in junior_judge_credentials.items():
        junior_judge_panel(username)
    elif username.strip() == admin_username and password.strip() == admin_password:
        admin_panel()
    elif username.strip() == participant_username and password.strip() == participant_password:
        registration_panel()
    else:
        st.write("Please enter Valid Credentials")



if __name__ == "__main__":
    main()
