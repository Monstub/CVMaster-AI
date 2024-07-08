###### Packages Used ######
import streamlit as st # core package used in this project
import pandas as pd
import base64, random
import time, datetime
import pymysql
import os
import socket
import platform
import geocoder
import secrets
import io, random
import plotly.express as px # to create visualisations at the admin session
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
# libraries used to parse the pdf files
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
from streamlit_tags import st_tags
from PIL import Image
# pre stored data for prediction purposes
from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos, interview_videos

import nltk

# Download NLTK data
nltk.download('stopwords')
nltk.download('punkt')

# Import NLTK stopwords after downloading
from nltk.corpus import stopwords

# Ensure stopwords are downloaded before further imports that depend on them
stopwords.words('english')



###### Preprocessing functions ######


# Generates a link allowing the data in a given panda dataframe to be downloaded in csv format 
def get_csv_download_link(df,filename,text):
    csv = df.to_csv(index=False)
    ## bytes conversions
    b64 = base64.b64encode(csv.encode()).decode()      
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


# Reads Pdf file and check_extractable
def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    ## close open handles
    converter.close()
    fake_file_handle.close()
    return text


# show uploaded file path to view pdf_display
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


# course recommendations which has data already loaded from Courses.py
def course_recommender(course_list):
    st.subheader("**Courses & Certificates Recommendations 👨‍🎓**")
    c = 0
    rec_course = []
    ## slider to choose from range 1-10
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course



###### Setting Page Configuration (favicon, Logo, Title) ######


st.set_page_config(
   layout="wide",
   page_title="CVMaster AI",
   page_icon='🤖',
)

# CSS for sidebar
st.markdown(
    """
    <style>
    body {
        background-color: #f8f9fa;
        color: #343a40;
        font-family: 'sans serif';
    }
    .sidebar .sidebar-content {
        background-image: linear-gradient(#ceeafd,#ceeafd);
        color: white;
    }
    /* Input fields, buttons, and other widgets */
    .stTextInput, .stTextArea, .stSelectbox, .stRadio, .stCheckbox, .stButton {
        color: #000;
        border: 2px solid #ceeafd;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
    }
    
    /* Image styling */
    .responsive-img {
        width: 100%;
        height: auto;
        border-radius: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


###### Main function run() ######


def run():
    
    with st.sidebar:

        st.markdown(
                """
                
                Follow me on:

                GitHub → [@Monstub](https://github.com/Monstub)

                LinkedIn → [Shubham Rathod](https://linkedin.com/in/monstub)
                
                ---

                """
            )
        
        st.sidebar.caption("Made by an [Shubham Rathod](https://linkedin.com/in/monstub/)")



    st.title('Welcome to the CVMaster AI 🤖')

    with st.expander('What is this app about?'):
        st.info("""
            The CVMaster AI 🤖 is a powerful tool designed to help users enhance their resumes by providing insightful analysis and smart recommendations. 
            This application scans your resume, extracts relevant information, and offers tailored suggestions to improve your job application prospects.
            """)
        st.write('''
            **Working:**
            - **Upload Resume:** Users can upload their resume in PDF format.
            - **Data Extraction:** The application uses pyresparser to parse and extract key details from the resume such as contact information, skills, and experience.
            - **Analysis:** The extracted data is analyzed to identify strengths and areas for improvement.
            - **Recommendations:** Based on the analysis, the app recommends additional skills, relevant courses, and interview preparation resources.
            - **Downloadable Report:** Users can download a CSV report of the analyzed data for their records.

            ---

            **Features:**
            - **Resume Parsing:** Extracts personal details, skills, and experiences from uploaded resumes.
            - **Skill Recommendations:** Suggests skills to add based on the content of the resume.
            - **Course Suggestions:** Recommends relevant online courses to enhance the user's profile.
            - **Interview Preparation:** Provides common interview questions and useful preparation videos.
            - **Resume Writing Tips:** Offers tips to improve the structure and content of the resume.
            - **Downloadable CSV:** Users can download the analyzed data and recommendations as a CSV file.

            ---

            **Technologies Used:**
            - **Python:** The core programming language used for building the application.
            - **Streamlit:** For creating the interactive web interface.
            - **Pyresparser:** For parsing and extracting data from resumes.
            - **Pandas:** For handling and manipulating data.
            - **Plotly:** For creating interactive visualizations.
            - **NLTK:** For natural language processing tasks.

            ---

            This comprehensive app is an essential tool for job seekers looking to optimize their resumes and improve their chances of landing their dream job.
        ''')
    
    st.markdown('''<h5 style='text-align: left; color: #021659;'> Fill the following basic details in order to start</h5>''',unsafe_allow_html=True)


    # Collecting Miscellaneous Information
    act_name = st.text_input('Name*')
    act_mail = st.text_input('Mail*')
    act_mob  = st.text_input('Mobile Number*')
    

    
    ## file upload in pdf format
    pdf_file = st.file_uploader("Upload Your Resume, And Get Smart Recommendations", type=["pdf"])
    if pdf_file is not None:
        with st.spinner('Hang On While We Cook Magic For You...'):
            time.sleep(4)
    
        ### saving the uploaded resume to folder
        save_image_path = './Uploaded_Resumes/'+pdf_file.name
        pdf_name = pdf_file.name
        with open(save_image_path, "wb") as f:
            f.write(pdf_file.getbuffer())
        show_pdf(save_image_path)

        ### parsing and extracting whole resume 
        resume_data = ResumeParser(save_image_path).get_extracted_data()
        if resume_data:

            st.header("🗄 Database")
            create_tab, alter_tab, drop_tab, describe_tab = \
            st.tabs(["INFO", "SKILLS", "TIPS", "RECOMMENDATIONS"])

            with create_tab:
            
                ## Get the whole resume data into resume_text
                resume_text = pdf_reader(save_image_path)

                ## Showing Analyzed data from (resume_data)
                s
                ---t.header("**Resume Analysis 🤘**")
                st.success("Hello "+ resume_data['name'])
                st.subheader("**Your Basic info 👀**")
                try:
                    st.text('Name: '+resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Degree: '+str(resume_data['degree']))                    
                    st.text('Resume pages: '+str(resume_data['no_of_pages']))

                except:
                    pass
                

                ## Predicting Candidate Experience Level 

                cand_level = ''
                intermediate_keywords = ['INTERNSHIP', 'INTERNSHIPS', 'Internship', 'Internships']
                experience_keywords = ['EXPERIENCE', 'WORK EXPERIENCE', 'Experience', 'Work Experience']

                if resume_data['no_of_pages'] < 1:
                    cand_level = "NA"
                    st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>You are at Fresher level!</h4>''', unsafe_allow_html=True)

                elif any(keyword in resume_text for keyword in intermediate_keywords):
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''', unsafe_allow_html=True)

                elif any(keyword in resume_text for keyword in experience_keywords):
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!</h4>''', unsafe_allow_html=True)

                else:
                    # Default case if none of the conditions are met
                    cand_level = "Fresher"
                    st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>You are at Fresher level!</h4>''', unsafe_allow_html=True)


                resume_score = 0

                # Predicting whether these key points are added to the resume
                if 'Objective' in resume_text or 'Summary' in resume_text:
                    resume_score += 6

                if any(keyword in resume_text for keyword in ['Education', 'School', 'College']):
                    resume_score += 12

                if any(keyword in resume_text for keyword in ['EXPERIENCE', 'Experience']):
                    resume_score += 16
                    
                if any(keyword in resume_text for keyword in ['INTERNSHIPS', 'INTERNSHIP', 'Internships', 'Internship']):
                    resume_score += 6
                    
                if any(keyword in resume_text for keyword in ['SKILLS', 'Skill', 'Skills', 'skill']):
                    resume_score += 7
                    
                if 'HOBBIES' in resume_text or 'Hobbies' in resume_text:
                    resume_score += 4
                    
                if 'INTERESTS' in resume_text or 'Interests' in resume_text:
                    resume_score += 5
                    
                if 'ACHIEVEMENTS' in resume_text or 'Achievements' in resume_text:
                    resume_score += 13
                    
                if 'CERTIFICATIONS' in resume_text or 'Certifications' in resume_text or 'Certification' in resume_text:
                    resume_score += 12
                    
                if 'PROJECTS' in resume_text or 'PROJECT' in resume_text or 'Projects' in resume_text or 'Project' in resume_text:
                    resume_score += 19

                st.subheader("**Resume Score 📝**")

                # Visual enhancement for progress bar
                st.markdown(
                    """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: #d73b5c;
                        }
                    </style>""",
                    unsafe_allow_html=True,
                )

                # Displaying progress bar with dynamic score calculation
                my_bar = st.progress(0)
                for percent_complete in range(resume_score):
                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1)

                # Displaying final resume score
                st.success(f'**Your Resume Writing Score: {resume_score}**')
                st.warning("**Note: This score is calculated based on the content in your resume.**")
                    
            with alter_tab:

                ## Skills Analyzing and Recommendation
                st.subheader("**Skills Recommendation 💡**")
                
                ### Current Analyzed Skills
                keywords = st_tags(label='### Your Current Skills',
                text='See our skools recommendation below',value=resume_data['skills'],key = '1  ')

                ### Keywords for Recommendations
                ds_keyword = ['tensorflow','keras','pytorch','machine learning','deep Learning','flask','streamlit']
                web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress','javascript', 'angular js', 'C#', 'Asp.net', 'flask']
                android_keyword = ['android','android development','flutter','kotlin','xml','kivy']
                ios_keyword = ['ios','ios development','swift','cocoa','cocoa touch','xcode']
                uiux_keyword = ['ux','adobe xd','figma','zeplin','balsamiq','ui','prototyping','wireframes','storyframes','adobe photoshop','photoshop','editing','adobe illustrator','illustrator','adobe after effects','after effects','adobe premier pro','premier pro','adobe indesign','indesign','wireframe','solid','grasp','user research','user experience']
                n_any = ['english','communication','writing', 'microsoft office', 'leadership','customer management', 'social media']
                ### Skill Recommendations Starts                
                recommended_skills = []
                reco_field = ''
                rec_course = ''

                ### condition starts to check skills from keywords and predict field
                for i in resume_data['skills']:
                
                    #### Data science recommendation
                    if i.lower() in ds_keyword:
                        print(i.lower())
                        reco_field = 'Data Science'
                        st.success("** Our analysis says you are looking for Data Science Jobs.**")
                        recommended_skills = ['Data Visualization','Predictive Analysis','Statistical Modeling','Data Mining','Clustering & Classification','Data Analytics','Quantitative Analysis','Web Scraping','ML Algorithms','Keras','Pytorch','Probability','Scikit-learn','Tensorflow',"Flask",'Streamlit']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '2')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(ds_course)
                        break

                    #### Web development recommendation
                    elif i.lower() in web_keyword:
                        print(i.lower())
                        reco_field = 'Web Development'
                        st.success("** Our analysis says you are looking for Web Development Jobs **")
                        recommended_skills = ['React','Django','Node JS','React JS','php','laravel','Magento','wordpress','Javascript','Angular JS','c#','Flask','SDK']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '3')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(web_course)
                        break

                    #### Android App Development
                    elif i.lower() in android_keyword:
                        print(i.lower())
                        reco_field = 'Android Development'
                        st.success("** Our analysis says you are looking for Android App Development Jobs **")
                        recommended_skills = ['Android','Android development','Flutter','Kotlin','XML','Java','Kivy','GIT','SDK','SQLite']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '4')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(android_course)
                        break

                    #### IOS App Development
                    elif i.lower() in ios_keyword:
                        print(i.lower())
                        reco_field = 'IOS Development'
                        st.success("** Our analysis says you are looking for IOS App Development Jobs **")
                        recommended_skills = ['IOS','IOS Development','Swift','Cocoa','Cocoa Touch','Xcode','Objective-C','SQLite','Plist','StoreKit',"UI-Kit",'AV Foundation','Auto-Layout']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '5')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(ios_course)
                        break

                    #### Ui-UX Recommendation
                    elif i.lower() in uiux_keyword:
                        print(i.lower())
                        reco_field = 'UI-UX Development'
                        st.success("** Our analysis says you are looking for UI-UX Development Jobs **")
                        recommended_skills = ['UI','User Experience','Adobe XD','Figma','Zeplin','Balsamiq','Prototyping','Wireframes','Storyframes','Adobe Photoshop','Editing','Illustrator','After Effects','Premier Pro','Indesign','Wireframe','Solid','Grasp','User Research']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '6')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(uiux_course)
                        break

                    #### For Not Any Recommendations
                    elif i.lower() in n_any:
                        print(i.lower())
                        reco_field = 'NA'
                        st.warning("** Currently our tool only predicts and recommends for Data Science, Web, Android, IOS and UI/UX Development**")
                        recommended_skills = ['No Recommendations']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Currently No Recommendations',value=recommended_skills,key = '6')
                        st.markdown('''<h5 style='text-align: left; color: #092851;'>Maybe Available in Future Updates</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = "Sorry! Not Available for this Field"
                        break

            with drop_tab:

                st.subheader("**Resume Tips & Ideas 🥂**")
                resume_score = 0

                # Predicting whether these key points are added to the resume
                if 'Objective' in resume_text or 'Summary' in resume_text:
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Objective/Summary</h4>''', unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add your career objective, it will give your career intention to the Recruiters.</h4>''', unsafe_allow_html=True)

                if any(keyword in resume_text for keyword in ['Education', 'School', 'College']):
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Education Details</h4>''', unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Education. It will show your qualification level to the recruiter.</h4>''', unsafe_allow_html=True)

                if any(keyword in resume_text for keyword in ['EXPERIENCE', 'Experience']):
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Experience</h4>''', unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Experience. It will help you to stand out from the crowd.</h4>''', unsafe_allow_html=True)

                if any(keyword in resume_text for keyword in ['INTERNSHIPS', 'INTERNSHIP', 'Internships', 'Internship']):
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''', unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Internships. It will help you to stand out from the crowd.</h4>''', unsafe_allow_html=True)

                if any(keyword in resume_text for keyword in ['SKILLS', 'Skill', 'Skills', 'skill']):
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''', unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Skills. It will help you a lot.</h4>''', unsafe_allow_html=True)

                if 'HOBBIES' in resume_text or 'Hobbies' in resume_text:
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies</h4>''', unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Hobbies. It will show your personality to the Recruiters and give an assurance that you are fit for this role.</h4>''', unsafe_allow_html=True)

                if 'INTERESTS' in resume_text or 'Interests' in resume_text:
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Interests</h4>''', unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Interests. It will show your interests other than job-related ones.</h4>''', unsafe_allow_html=True)

                if 'ACHIEVEMENTS' in resume_text or 'Achievements' in resume_text:
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements</h4>''', unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Achievements. It will show that you are capable for the required position.</h4>''', unsafe_allow_html=True)

                if 'CERTIFICATIONS' in resume_text or 'Certifications' in resume_text or 'Certification' in resume_text:
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Certifications</h4>''', unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Certifications. It will show that you have done some specialization for the required position.</h4>''', unsafe_allow_html=True)

                if 'PROJECTS' in resume_text or 'PROJECT' in resume_text or 'Projects' in resume_text or 'Project' in resume_text:
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''', unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Projects. It will show that you have done work related to the required position.</h4>''', unsafe_allow_html=True)


            with describe_tab:
                ## Recommending Resume Writing Video
                st.header("**Bonus Video for Resume Writing Tips💡**")
                resume_vid = random.choice(resume_videos)
                st.video(resume_vid)

                ## Recommending Interview Preparation Video
                st.header("**Bonus Video for Interview Tips💡**")
                interview_vid = random.choice(interview_videos)
                st.video(interview_vid)

        else:
            st.error('Something went wrong..')                

    
# Calling the main (run()) function to make the whole process run
run()
