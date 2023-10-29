import streamlit as st
import pandas as pd
import os
import json
import numpy as np



admin_username = "admin"
admin_password = "54321"
participant_username = "register"
participant_password = "12345"


control_db = {
    "Registration Juniors": {"status": True, "toggle": True},
    "Registration Sub Juniors": {"status": True, "toggle": True},
    "Registration Seniors": {"status": True, "toggle": True},
    "Registration Super Seniors": {"status": True, "toggle": True},
    "Finals": {"status": True, "toggle": True},
}


juniors_data_file = "juniors_data.csv"

category_status_file = "category_status.json"
scoring_criteria_file = "scoring.csv"




if os.path.exists(juniors_data_file):
    prelims_jun_all = pd.read_csv(juniors_data_file)
else:
    prelims_jun_all = pd.DataFrame(columns=["Name", "School", "Attendance"])


if os.path.exists(category_status_file):
    with open(category_status_file, "r") as file:
        control_db = json.load(file)


def save_control_db_to_file():
    with open(category_status_file, "w") as file:
        json.dump(control_db, file)


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
   
    if not os.path.exists('roster_prelim_jun.csv'):
        st.write("Roster file is missing. Please prepare the roster before generating the scoresheet.")
        return

 
    roster_df = pd.read_csv('roster_prelim_jun.csv')

    
    judges = ['Judge 1', 'Judge 2', 'Judge 3']

   
    if not os.path.exists(scoring_criteria_file):
        st.write("Scoring criteria file is missing. Please upload it.")
        return

    scoring_df = pd.read_csv(scoring_criteria_file)


    scoresheet = roster_df[['Name', 'School']].copy()

 
    for judge in judges:
        for index, row in scoring_df.iterrows():
            criteria = row['Criteria']
            scoresheet[f"{judge} {criteria}"] = np.nan  # Initialize with NaN


    scoresheet.to_csv('scoresheet_jun.csv', index=False)
    st.write("Scoresheet generated successfully.")





def control_panel():
    st.title("Control Panel")
    for reg_category, data in control_db.items():
        data["toggle"] = st.checkbox(reg_category, data["toggle"])
        data["status"] = data["toggle"]
     
        save_control_db_to_file()

    st.title("Scoring Criteria")
    scoring_criteria = st.file_uploader("Upload a spreadsheet of scoring criteria", type=["csv", "xlsx"])
    if scoring_criteria is not None:
      
        scoring_df = pd.read_excel(scoring_criteria) 
     
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
    global prelims_jun_all 
    st.title("Category 1")
    st.write("Upload a spreadsheet with participant names and school names.")

   
    uploaded_file = st.file_uploader("Upload a spreadsheet", type=["csv", "xlsx"])

    if uploaded_file is not None:
        if st.button("Process and Save"):
            data = pd.read_excel(uploaded_file)  # Modify this according to your data format (csv, xlsx, etc.)

            
            prelims_jun_all = data
        
            save_prelims_jun_all_to_csv(prelims_jun_all)

    st.title("Juniors All")
    st.dataframe(prelims_jun_all)
 
    if st.button("Generate Roster"):
        
        present_participants = prelims_jun_all[prelims_jun_all['Attendance'] == 'Present']

        if not present_participants.empty:
        
            present_participants.drop(columns=['Attendance'], inplace=True)
            present_participants.to_csv('roster_prelim_jun.csv', index=False)
            st.write("Generated Roster:")
            st.dataframe(present_participants)

        else:
            st.write("No participants with 'Present' status. Roster not generated.")

  
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


    judging_status = st.checkbox('Open Judging', current_judging_status.get("status", False))

   
    if current_judging_status.get("status") is None or current_judging_status.get("status") != judging_status:
        current_judging_status["status"] = judging_status

   
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
           
            prelims_jun_all.loc[(prelims_jun_all['Name'] == selected_name) & (
                        prelims_jun_all['School'] == selected_school), 'Attendance'] = "Present"
          
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
