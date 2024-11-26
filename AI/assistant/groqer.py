import os
from groq import Groq
from docx_generator import generate_document
# from pdf_generator import generate_document
from random import choice
from convert_docx_to_pdf import convert
import sys

sys.path.append('../')
from utils import util

_job_documents_dir = "job_documents"

groq_api_key = os.environ.get("GROQ_API_KEY")
groq_url = "https://api.groq.com/openai/v1/models"

def log(msg):
  util.log(msg, "GROQER")

groq_client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def use_groq(query="", prompt="you are a helpful assistant", model="llama3-8b-8192"):
    log(f"Model: [{model}]")
#   log(f"Prompt: {prompt}")
#   log(f"Query: {query}")
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": query,
            },
            {
                "role": "system",
                "content": prompt
            }
        ],
        model=model
        # model="llama3-70b-8192",
        # model="llama-3.2-90b-text-preview",
    )
    output = chat_completion.choices[0].message.content
#   log(f"Response: {output}")
    return output

AI_MODELS = { 
    "great": [ 
        "llama3-70b-8192", 
#        "llama-3.2-90b-text-preview", 
        "llama3-groq-70b-8192-tool-use-preview"
    ],
    "good": [ 
        "llama-3.1-70b-versatile", 
        "llama-3.2-11b-text-preview", 
        "llama3-8b-8192",
#           "llama-guard-3-8b",
#        "gemma2-9b-it"
    ],
    "okay": [ 
#        "llama-3.1-8b-instant", 
        "llama3-groq-8b-8192-tool-use-preview", 
        "llama-3.2-3b-preview", 
        "llama-3.2-1b-preview", 
#        "llava-v1.5-7b-4096-preview", 
        "gemma-7b-it"
    ]
}

def get_great_model():
    return choice(AI_MODELS["great"])

def get_good_model():
    return choice(AI_MODELS["good"])

def get_okay_model():
    return choice(AI_MODELS["okay"])

def evaluate_job(query, prompt='''
You are salt of the Earth. 
You've worked every job under the sun; blue collar, white collar, and everything in-between. 
You will be given a job description. 
You will evaluate the job description and determine the minimum level of education required. 
If it's a job that only needs a high school degree, you will make sure to say so. 
Your response must only contain the level of education required and must not contain any other text.
''', max_tokens=50):
    return use_groq(query, prompt, get_good_model())

def generate_resume(query, prompt='''
You are an expert resume builder.
You will take my existing resume and rework it so that it is tailored to a job description you will be given. 
You will keep entries in chronological order from most recent to least recent.
You will rephrase all relevant experience and skills, emphasizing those most relevant to the job description you will be given. 
Your response should increase my odds of getting the job. 
If it's not a technical job, omit specific technical details like specific programming languages. 
Your response must only contain the generated resume. 
Your response must not contain placeholder information or sections that have no content. 
Your response must not contain sections containing nothing, or containing only something like "(No information available)". 
Do not respond with anything other than the resume you generate. 
Do not begin your response with anything like 'Here is the reworked resume', and instead only respond with the resume itself. 
Your response must not contain links, like for example to an email. 
This is my current resume: Lee Bolgatz.  lee.bolgatz.jobs@gmail.com ❖ (603) 557-7022 ❖ Manchester, NH. WORK EXPERIENCE: DCS Corporation, June 2019 – Jan 2023. Full-Stack Software Engineer - Nashua, NH. * As a Software Engineer, I built mission-critical software for military applications.    * Developed a web application from scratch using React and Redux for military mission planning.    * Implemented back-end functionality using C# and SQL to support complex military operations. * Served as Scrum Master during transitional period of team reorganization following the award of additional contracted projects from the U.S. Department of Defense. Successfully led development team to release of new product in line with customer specifications. * Ensured precision execution of aeronautic specifications to integrate generated data directly with military hardware on multiple types of aircraft. * Coordinated with cross-functional teams, delivering software ahead of schedule, allowing time for additional features before release.   Centene Corporation, May 2023 - May 2024. Back-End Software Developer (Contract) - Remote, Manchester, NH. * Enhanced and maintained web applications using JavaScript and JSP. * Spearheaded software updates and system enhancements to improve operational efficiency. * Existing web applications had performance issues, leading to decreased user satisfaction. Optimized code and redesigned UI components using JavaScript and JSP.  Reduced page load times, increasing user engagement. * Frequent UI issues were causing user frustration. Led initiatives to identify and resolve interface problems, implementing best UI/UX practices. Improved customer satisfaction. Career Sabbatical, May 2018 - June 2019. * Focused on personal projects, honing my skills in both front-end and back-end development. Carbon Black, Jan 2017 - May 2018. Software Engineer - Waltham, MA. * Eliminated a backlog of UI bugs using jQuery and JavaScript. * Developed new UI features using PHP and SQL. * Over 50 UI bugs were affecting product usability. Systematically addressed and resolved all UI issues. Increased user satisfaction due to improved interface stability. * Lack of requested UI features was hindering client acquisition. Implemented new features to enhance product capabilities. Contributed to an increase in sales by attracting new clients. Professional Development, Mar 2016 - Jan 2017. * Acquired new skills in UI development, sharpening my skills in jQuery and JavaScript. MPAY, May 2015 - Mar 2016.  Software Engineer (Seasonal Contract) - Waltham, MA. * Improved C++ features for payroll software, ensuring compliance with tax law changes. * Updated tax calculation with VB Script and fixed various bugs, resulting in a smoother user experience. Lionbridge, May 2014 - May 2015. Software Engineer - Waltham, MA. * Enhanced translation software’s UI with C++ and MySQL for improved functionality and data management. * Developed features in Python and JavaScript, improving the efficiency of the software suite. EDUCATION:  University of New Hampshire, May 2014.  B.A. in Computer Science - Durham, NH. New Hampshire Technical Institute, May 2010. A.S. in Game Programming - Concord, NH. SKILLS: Languages & Frameworks: JavaScript (Native, Angular, React, Redux, jQuery), .NET (C#, ASP.NET), Python, PHP, XML, C/C++, Java, VBScript, SQL, JSP. Development Tools & Platforms: Jenkins (CI/CD), Selenium, Visual Studio, Eclipse, SQLServer, MySQL. Methodologies: Agile (Scrum Master), Test-Driven Development (TDD), CI/CD.
''', max_tokens=200):
    return use_groq(query, prompt, get_good_model())

def generate_cover_letter(job_description, resume, prompt='''
You are an expert cover letter builder. 
You will take my existing resume and generate a cover letter that is tailored to a job description you will be given. 
In the case of me being overqualified, you will downplay and summarize experience not relevant to the job posting. 
Your response must be exactly one full paragraph long. 
Your response must only contain the generated cover letter. 
Your response must not contain placeholder information, such as "[Your Name]" or "[Email Address]". 
The cover letter should have a greeting, like "Dear Hiring Manager". 
The cover letter should have a signoff which at least includes my name, which is Lee Bolgatz.
Do not respond with anything other than the cover letter you generate. 
Do not begin your response with anything like 'Here is the cover letter', and instead only respond with the cover letter itself. 
Your response must not contain postal addresses. 
Your response must not contain lists.
''', max_tokens=200):
    return use_groq(f"The job description is as follows: {job_description}", f"{prompt} My resume is as follows: {resume}", get_good_model())

def polish_resume(query, prompt='''
You are a copy editor. 
You will be given a resume. 
You will remove anything that isn't part of the resume, such as 'Here is the resume'. 
You will improve the visual appeal of the document by adding formatting. 
If it's not a technical job, omit specific technical details like specific programming languages. 
Your improvements will not add or remove information. 
The information in your response must match the information in the resume you are given. 
Your response must only contain the generated resume. 
Your response must not contain placeholder information or sections that have no content. 
Your response must not contain sections containing nothing, or containing only something like "(No information available)". 
Do not respond with anything other than the resume you generate. 
Your response must not contain links, like for example to an email. 
Do not begin your response with anything like 'Here is the reworked resume', and instead only respond with the resume itself. 
''', max_tokens=200):
    return use_groq(query, prompt, get_great_model())

def remove_resume_lies(query, prompt='''
You are a fact checker. 
You will be given an improved, more marketable version of resume. 
You will be given the original, generic version of my resume. 
You will compare the claims made by the improved resume to the facts listed on the original resume. 
You will remove anything stated in the improved resume that is not supported by the information in the original resume. 
The information in your response must be supported by the information in my resume. 
Your response must only contain the generated resume. 
Your response must not contain placeholder information. 
Do not respond with anything other than the resume you generate. 
Do not begin your response with anything like 'Here is the fact-checked resume', and instead only respond with the resume itself. 
You will retain the formatting in the resume. 
Your response must not contain links, like for example to an email. 
You will use my original, generic resume to find and remove false statements. 
My original, generic resume is as follows: Lee Bolgatz.  lee.bolgatz.jobs@gmail.com ❖ (603) 557-7022 ❖ Manchester, NH. WORK EXPERIENCE: DCS Corporation, June 2019 – Jan 2023. Full-Stack Software Engineer - Nashua, NH. * As a Software Engineer, I built mission-critical software for military applications.    * Developed a web application from scratch using React and Redux for military mission planning.    * Implemented back-end functionality using C# and SQL to support complex military operations. * Served as Scrum Master during transitional period of team reorganization following the award of additional contracted projects from the U.S. Department of Defense. Successfully led development team to release of new product in line with customer specifications. * Ensured precision execution of aeronautic specifications to integrate generated data directly with military hardware on multiple types of aircraft. * Coordinated with cross-functional teams, delivering software ahead of schedule, allowing time for additional features before release.   Centene Corporation, May 2023 - May 2024. Back-End Software Developer (Contract) - Remote, Manchester, NH. * Enhanced and maintained web applications using JavaScript and JSP. * Spearheaded software updates and system enhancements to improve operational efficiency. * Existing web applications had performance issues, leading to decreased user satisfaction. Optimized code and redesigned UI components using JavaScript and JSP.  Reduced page load times, increasing user engagement. * Frequent UI issues were causing user frustration. Led initiatives to identify and resolve interface problems, implementing best UI/UX practices. Improved customer satisfaction. Career Sabbatical, May 2018 - June 2019. * Focused on personal projects, honing my skills in both front-end and back-end development. Carbon Black, Jan 2017 - May 2018. Software Engineer - Waltham, MA. * Eliminated a backlog of UI bugs using jQuery and JavaScript. * Developed new UI features using PHP and SQL. * Over 50 UI bugs were affecting product usability. Systematically addressed and resolved all UI issues. Increased user satisfaction due to improved interface stability. * Lack of requested UI features was hindering client acquisition. Implemented new features to enhance product capabilities. Contributed to an increase in sales by attracting new clients. Professional Development, Mar 2016 - Jan 2017. * Acquired new skills in UI development, sharpening my skills in jQuery and JavaScript. MPAY, May 2015 - Mar 2016.  Software Engineer (Seasonal Contract) - Waltham, MA. * Improved C++ features for payroll software, ensuring compliance with tax law changes. * Updated tax calculation with VB Script and fixed various bugs, resulting in a smoother user experience. Lionbridge, May 2014 - May 2015. Software Engineer - Waltham, MA. * Enhanced translation software’s UI with C++ and MySQL for improved functionality and data management. * Developed features in Python and JavaScript, improving the efficiency of the software suite. EDUCATION:  University of New Hampshire, May 2014.  B.A. in Computer Science - Durham, NH. New Hampshire Technical Institute, May 2010. A.S. in Game Programming - Concord, NH. SKILLS: Languages & Frameworks: JavaScript (Native, Angular, React, Redux, jQuery), .NET (C#, ASP.NET), Python, PHP, XML, C/C++, Java, VBScript, SQL, JSP. Development Tools & Platforms: Jenkins (CI/CD), Selenium, Visual Studio, Eclipse, SQLServer, MySQL. Methodologies: Agile (Scrum Master), Test-Driven Development (TDD), CI/CD.
''', max_tokens=200):
    return use_groq(query, prompt, get_good_model())

def polish_cover_letter(query, prompt='''
You are a copy editor.
You will be given a cover letter for a job posting. 
You will remove anything that isn't part of the cover letter, such as 'Here is the cover letter'. 
The information in your response must match the information in the cover letter you are given. 
The cover letter should have a greeting, like "Dear Hiring Manager". 
The cover letter must have a signoff which includes my name, which is Lee Bolgatz. 
Your response must only contain the generated cover letter. 
Your response must be exactly one full paragraph long. 
Your response must not contain placeholder information, such as "[Your Name]" or "[Email Address]". 
Do not respond with anything other than the cover letter you generate. 
Your response must not contain postal addresses. 
Do not begin your response with anything like 'Here is the reworked cover letter', and instead only respond with the cover letter itself. 
Where possible, try to reduce the usage of the full company name and full job title - remove things like "Inc." and things like slashes between two options. 
''', max_tokens=200):
    return use_groq(query, prompt, get_great_model())

def extract_company_name(query, prompt='''
You are a machine that will be fed a job posting and will output the name of the company which posted the job. 
Your response will only contain the name of the company. 
''', max_tokens=50):
    return use_groq(query, prompt, get_okay_model())

def remove_cover_letter_lies(query, prompt='''
You are a fact checker. 
You will be given a cover letter describing my experience. 
You will be given my resume describing my experience. 
You will remove anything stated in the cover letter that is not mentioned in the resume. 
You will use my resume to find and remove false statements. 
Your response must only contain the generated cover letter. 
Your response must not contain placeholder information, such as "[Your Name]" or "[Email Address]". 
Do not remove my name, which is Lee Bolgatz. 
Your response must not contain postal addresses. 
Do not respond with anything other than the cover letter you generate. 
Do not begin your response with anything like 'Here is the reworked cover letter', and instead only respond with the cover letter itself. 
My resume is as follows: Lee Bolgatz.  lee.bolgatz.jobs@gmail.com ❖ (603) 557-7022 ❖ Manchester, NH. WORK EXPERIENCE: DCS Corporation, June 2019 – Jan 2023. Full-Stack Software Engineer - Nashua, NH. * As a Software Engineer, I built mission-critical software for military applications.    * Developed a web application from scratch using React and Redux for military mission planning.    * Implemented back-end functionality using C# and SQL to support complex military operations. * Served as Scrum Master during transitional period of team reorganization following the award of additional contracted projects from the U.S. Department of Defense. Successfully led development team to release of new product in line with customer specifications. * Ensured precision execution of aeronautic specifications to integrate generated data directly with military hardware on multiple types of aircraft. * Coordinated with cross-functional teams, delivering software ahead of schedule, allowing time for additional features before release.   Centene Corporation, May 2023 - May 2024. Back-End Software Developer (Contract) - Remote, Manchester, NH. * Enhanced and maintained web applications using JavaScript and JSP. * Spearheaded software updates and system enhancements to improve operational efficiency. * Existing web applications had performance issues, leading to decreased user satisfaction. Optimized code and redesigned UI components using JavaScript and JSP.  Reduced page load times, increasing user engagement. * Frequent UI issues were causing user frustration. Led initiatives to identify and resolve interface problems, implementing best UI/UX practices. Improved customer satisfaction. Career Sabbatical, May 2018 - June 2019. * Focused on personal projects, honing my skills in both front-end and back-end development. Carbon Black, Jan 2017 - May 2018. Software Engineer - Waltham, MA. * Eliminated a backlog of UI bugs using jQuery and JavaScript. * Developed new UI features using PHP and SQL. * Over 50 UI bugs were affecting product usability. Systematically addressed and resolved all UI issues. Increased user satisfaction due to improved interface stability. * Lack of requested UI features was hindering client acquisition. Implemented new features to enhance product capabilities. Contributed to an increase in sales by attracting new clients. Professional Development, Mar 2016 - Jan 2017. * Acquired new skills in UI development, sharpening my skills in jQuery and JavaScript. MPAY, May 2015 - Mar 2016.  Software Engineer (Seasonal Contract) - Waltham, MA. * Improved C++ features for payroll software, ensuring compliance with tax law changes. * Updated tax calculation with VB Script and fixed various bugs, resulting in a smoother user experience. Lionbridge, May 2014 - May 2015. Software Engineer - Waltham, MA. * Enhanced translation software’s UI with C++ and MySQL for improved functionality and data management. * Developed features in Python and JavaScript, improving the efficiency of the software suite. EDUCATION:  University of New Hampshire, May 2014.  B.A. in Computer Science - Durham, NH. New Hampshire Technical Institute, May 2010. A.S. in Game Programming - Concord, NH. SKILLS: Languages & Frameworks: JavaScript (Native, Angular, React, Redux, jQuery), .NET (C#, ASP.NET), Python, PHP, XML, C/C++, Java, VBScript, SQL, JSP. Development Tools & Platforms: Jenkins (CI/CD), Selenium, Visual Studio, Eclipse, SQLServer, MySQL. Methodologies: Agile (Scrum Master), Test-Driven Development (TDD), CI/CD.
''', max_tokens=200):
    return use_groq(query, prompt, get_great_model())

def rephrase_document(query, prompt='''
You are salt of the Earth. 
You've worked as a CEO at famous companies, and you've worked as a burger-flipper at burger places. 
You've been everywhere and done everything. 
You will be given a document and a level of education. 
You will ensure that all phrasing in the document matches the level of education. 
If you give someone with only a little education a document with big words and technical terms, it will offend them because it will make them feel stupid. 
If you give someone with a lot of education a document with small words, it will offend them because it will make them think you believe they are stupid. 
You will reword the document to make absolutely sure that someone at the specified education level will not be offended by the phrasing. 
Your response must only contain the revised document and nothing else. 
Your response must not contain things like "Here is the revized document:". 
Your response must exclusively contain the revised document. 
''', max_tokens=250):
    return use_groq(query, prompt, get_great_model())

def normalize_filename(filename):
    return filename.replace("&","") \
                   .replace(".","") \
                   .replace(",","") \
                   .replace("__","_") \
                   .replace("/","-") \
                   .lower()

while True:
  job_description = input("Job Description: ")
  
  log("Evaluating education needed...")
  job_education_level = evaluate_job(f"The job description is as follows: {job_description}")
  log(f"{job_education_level}")

  log("Getting company name...")
  company_name = extract_company_name(job_description[:round(len(job_description)/2)])
  log(f"{company_name}")
  '''
  log("Generating resume...")
  resume = generate_resume(f"The job description is as follows: {job_description}")
#  log(resume)
  
  log("Double-checking resume...")
  resume = remove_resume_lies("The improved resume is as follows: " + resume)
#  log(resume)

  log("Matching education level...")
  resume = rephrase_document(f"The education level is: {job_education_level}. The document is as follows: {resume}.")
#  log(resume)

  log("Polishing resume...")
  resume = polish_resume(f"The resume is as follows: {resume}")
#  log(resume)

  resume_docx_path = f"{_job_documents_dir}/resume_{company_name.replace(' ','_')}"
  generate_document(normalize_filename(resume_docx_path), resume)
  convert(normalize_filename(resume_docx_path))
  '''
  log("Generating cover letter...")
  resume = "Lee Bolgatz.  lee.bolgatz.jobs@gmail.com ❖ (603) 557-7022 ❖ Manchester, NH. WORK EXPERIENCE: DCS Corporation, June 2019 – Jan 2023. Full-Stack Software Engineer - Nashua, NH. * As a Software Engineer, I built mission-critical software for military applications.    * Developed a web application from scratch using React and Redux for military mission planning.    * Implemented back-end functionality using C# and SQL to support complex military operations. * Served as Scrum Master during transitional period of team reorganization following the award of additional contracted projects from the U.S. Department of Defense. Successfully led development team to release of new product in line with customer specifications. * Ensured precision execution of aeronautic specifications to integrate generated data directly with military hardware on multiple types of aircraft. * Coordinated with cross-functional teams, delivering software ahead of schedule, allowing time for additional features before release.   Centene Corporation, May 2023 - May 2024. Back-End Software Developer (Contract) - Remote, Manchester, NH. * Enhanced and maintained web applications using JavaScript and JSP. * Spearheaded software updates and system enhancements to improve operational efficiency. * Existing web applications had performance issues, leading to decreased user satisfaction. Optimized code and redesigned UI components using JavaScript and JSP.  Reduced page load times, increasing user engagement. * Frequent UI issues were causing user frustration. Led initiatives to identify and resolve interface problems, implementing best UI/UX practices. Improved customer satisfaction. Career Sabbatical, May 2018 - June 2019. * Focused on personal projects, honing my skills in both front-end and back-end development. Carbon Black, Jan 2017 - May 2018. Software Engineer - Waltham, MA. * Eliminated a backlog of UI bugs using jQuery and JavaScript. * Developed new UI features using PHP and SQL. * Over 50 UI bugs were affecting product usability. Systematically addressed and resolved all UI issues. Increased user satisfaction due to improved interface stability. * Lack of requested UI features was hindering client acquisition. Implemented new features to enhance product capabilities. Contributed to an increase in sales by attracting new clients. Professional Development, Mar 2016 - Jan 2017. * Acquired new skills in UI development, sharpening my skills in jQuery and JavaScript. MPAY, May 2015 - Mar 2016.  Software Engineer (Seasonal Contract) - Waltham, MA. * Improved C++ features for payroll software, ensuring compliance with tax law changes. * Updated tax calculation with VB Script and fixed various bugs, resulting in a smoother user experience. Lionbridge, May 2014 - May 2015. Software Engineer - Waltham, MA. * Enhanced translation software’s UI with C++ and MySQL for improved functionality and data management. * Developed features in Python and JavaScript, improving the efficiency of the software suite. EDUCATION:  University of New Hampshire, May 2014.  B.A. in Computer Science - Durham, NH. New Hampshire Technical Institute, May 2010. A.S. in Game Programming - Concord, NH. SKILLS: Languages & Frameworks: JavaScript (Native, Angular, React, Redux, jQuery), .NET (C#, ASP.NET), Python, PHP, XML, C/C++, Java, VBScript, SQL, JSP. Development Tools & Platforms: Jenkins (CI/CD), Selenium, Visual Studio, Eclipse, SQLServer, MySQL. Methodologies: Agile (Scrum Master), Test-Driven Development (TDD), CI/CD."
  cover_letter = generate_cover_letter(job_description, resume)
#  log(cover_letter)

  log("Double-checking cover letter...")
  cover_letter = remove_cover_letter_lies(f"The cover letter is as follows: {cover_letter}")
#  log(cover_letter)

  log("Triple-checking cover letter...")
  cover_letter = remove_cover_letter_lies(f"The cover letter is as follows: {cover_letter}")
#  log(cover_letter)
           
  log("Matching education level...")
  cover_letter = rephrase_document(f"The education level is: {job_education_level}. The document is as follows: {cover_letter}.")
#  log(cover_letter)

  log("Polishing cover letter...")
  cover_letter = polish_cover_letter(cover_letter)
#  log(cover_letter)

  cover_letter_docx_path = f"{_job_documents_dir}/cover_letter_{normalize_filename(company_name).replace(' ','_')}"
  generate_document(cover_letter_docx_path, cover_letter)
  convert(cover_letter_docx_path)
  

  # print(resume)
  # print(company_name)