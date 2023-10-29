import streamlit as st
import pandas as pd
import os
import json
import numpy as np


# Define username and password for admin and participant access
admin_username = "admin"
admin_password = "54321"
participant_username = "register"
participant_password = "12345"

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
    judges = ['Judge 1', 'Judge 2', 'Judge 3']

    # Check if the scoring criteria file exists
    if not os.path.exists(scoring_criteria_file):
        st.write("Scoring criteria file is missing. Please upload it.")
        return

    # Load scoring criteria from scoring.csv
    scoring_df = pd.read_csv(scoring_criteria_file)

    # Create an empty scoresheet DataFrame
    scoresheet = roster_df[['Name', 'School']].copy()

    # Add columns for each judge's scores based on criteria
    for judge in judges:
        for index, row in scoring_df.iterrows():
            criteria = row['Criteria']
            scoresheet[f"{judge} {criteria}"] = np.nan  # Initialize with NaN

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

    # "Download Roster" button
    if os.path.exists('roster_prelim_jun.csv'):
        with open('roster_prelim_jun.csv', 'rb') as file:
            data = file.read()
        st.download_button(
            label="Download Roster",
            data=data,
            key="roster_prelim_jun.csv",
            file_name="roster_prelim_jun.csv",
        )

    if st.button("Generate Scoresheet"):
        generate_scoresheet()

    if os.path.exists('scoresheet_jun.csv'):
        scoresheet = pd.read_csv('scoresheet_jun.csv')
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

def main():
    st.title("KSV Interface")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if username.strip() == admin_username and password.strip() == admin_password:
        admin_panel()
    elif username.strip() == participant_username and password.strip() == participant_password:
        registration_panel()
    else:
        st.write("Please enter Valid Credentials")

if __name__ == "__main__":
    main()
