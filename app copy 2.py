from flask import Flask, render_template, request, redirect, session, url_for
from authlib.integrations.flask_client import OAuth
import argparse
import uuid
from dateutil import parser
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for session to work
import time
import base64
import requests
from datetime import datetime
from flask_socketio import SocketIO
import shutil
from werkzeug.utils import secure_filename


import random








JENKINS_URL = "http://192.168.100.12:8080/"
JENKINS_USERNAME = "AzureTeam"
JENKINS_API_TOKEN = "11029516d336cd3e4659d68ed54c21cd98"

# JENKINS_URL = "http://localhost:8080/"
# JENKINS_USERNAME = "dhanasekhar"
# JENKINS_API_TOKEN = "1144b35766ffaa1419142ce13b2f6e1d70"

COLOR_SCHEMES = [
    {'primary': '#4e79a7', 'secondary': '#f28e2b', 'accent': '#e15759'},
    {'primary': '#59a14f', 'secondary': '#edc948', 'accent': '#76b7b2'},
    {'primary': '#b07aa1', 'secondary': '#ff9da7', 'accent': '#9c755f'}
]

CRON_SCHEDULES = {
    'Neural Daily Scan': 'H 0 * * *',
    'Cognitive Weekly Sync': 'H 0 * * 0',
    'Machine Monthly Digest': 'H 0 1 * *',
    'Custom AI Schedule': ''
}

AI_TIPS = [
    "Pro tip: Use descriptive index names for better searchability!",
    "Did you know? Consistent sourcetypes improve data analysis.",
    "Recommendation: Schedule scans during low-traffic periods.",
    "Optimization: Group similar logs together in your monitor path."
]

import xml.sax.saxutils as saxutils
from datetime import datetime

from datetime import datetime

def datetime_to_cron(dt_str):
    # Convert the string to a datetime object
    dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M")
    
    # Format the datetime object into the cron format
    cron_expression = f"{dt.minute} {dt.hour} {dt.day} {dt.month} *"
    
    return cron_expression

@app.route('/harness', methods=['GET'])
def harness_ui():
    return harness()

def harness():
    return render_template('harness.html')





@app.route('/splunk_create', methods=['GET'])
def splunk_create_ui():
    return splunk_create_app()

def splunk_create_app():
    return render_template('index_copy.html')































@app.route('/schedule-job', methods=['GET', 'POST'])
def schedule_job():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        repo_link = request.form.get('repoLink')
        schedule_time = request.form.get('scheduleTime')

        repo_name = repo_link.rstrip('/').split('/')[-1].replace('.git', '')

        # Create a unique job name
        job_name = f"{repo_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        print("Pipeline created:", job_name)

        cron_schedule = datetime_to_cron(schedule_time)
        print(f"Creating pipeline job: {job_name} at cron time: {cron_schedule}")

        # Create the Jenkins pipeline script with the cron trigger
        pipeline_script = f"""pipeline {{
    agent {{ label 'Azure Team' }}
    triggers {{
        cron('{cron_schedule}')
    }}
    environment {{
        SPLUNK_APPS_DIR = 'C:\\\\Program Files\\\\Splunk\\\\etc\\\\apps'
        REPO_URL = "{repo_link}"
        REPO_NAME = "{repo_name}"
        INDEX_NAME = 'devsync-index'
        SPLUNK_USERNAME = 'MTL1013'
        SPLUNK_PASSWORD = 'MTL@1013'
        EMAIL_RECIPIENT = "{email}"
        CRON_TIME = "{cron_schedule}"
    }}
    stages {{
        stage('Clone Repo to Splunk Apps Directory') {{
            steps {{
                bat \"\"\"
                cd "%SPLUNK_APPS_DIR%"
                if not exist "%REPO_NAME%" (
                    git clone {repo_link}
                    rmdir /s /q "%SPLUNK_APPS_DIR%\\%REPO_NAME%\\.git"
                    echo Repository cloned successfully.
                ) else (
                    echo Repository already exists. Skipping clone.
                )
                \"\"\"
            }}
        }}
        stage('Close Repo (Skip Clone)') {{
            steps {{
                script {{
                    echo "Repository '{repo_name}' is closed or skipped."
                }}
            }}
        }}
        stage('Send Completion Email') {{
            steps {{
                emailext(
                    subject: 'Splunk Deployment Completed Successfully',
                    to: "{email}",
                    mimeType: 'text/html',
                    body: \"\"\"<p>Deployment complete for {repo_name}.</p>\"\"\"
                )
            }}
        }}
    }}
    post {{
        success {{ echo "Success"; }}
        failure {{ echo "Failure"; }}
    }}
}}"""

        # Jenkins config.xml format
        job_config = f"""<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job">
  <description>Auto-created job for {repo_name}</description>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps">
    <script>{saxutils.escape(pipeline_script)}</script>
    <sandbox>true</sandbox>
  </definition>
  <disabled>false</disabled>
</flow-definition>
"""

        # Send request to Jenkins to create the job
        try:
            create_response = requests.post(
                f"{JENKINS_URL}/createItem?name={job_name}",
                data=job_config,
                headers={"Content-Type": "application/xml"},
                auth=HTTPBasicAuth(JENKINS_USERNAME, JENKINS_API_TOKEN)
            )

            # Debugging response
            print(f"Response Status: {create_response.status_code}")
            print(f"Response Content: {create_response.text}")

            if create_response.status_code == 200:
                return f"Job '{job_name}' scheduled successfully!"
            else:
                return f"Failed to create Jenkins job: {create_response.text}", 500
        except Exception as e:
            print(f"Error occurred: {e}")
            return f"An error occurred: {e}", 500

    # GET method
    return render_template('schedule-job.html')


# # Route for scheduling a job (using dynamic URL parts for owner and repo name)
# @app.route('/schedule-job', methods=['GET', 'POST'])
# def schedule_job():
#     if request.method == 'POST':
#         # Handle form submission
#         email = request.form.get('email')
#         name = request.form.get('name')
#         repo_link = request.form.get('repoLink')
#         schedule_time = request.form.get('scheduleTime')

#         # You can log the details or store them as necessary
#         print(f"Job Scheduled for {name} - {email} - {repo_link} at {schedule_time}")
        
#         # After processing the form, redirect to the main page
#         return redirect(url_for('main'))  # Redirect to the main page (home)
    
#     # Render the form for GET request
#     return render_template('schedule-job.html')  # Return the scheduling form



@app.route('/dashboard')
def main_form():
    if 'github_token' not in session:
        return render_template('Github_login.html')

    token = session['github_token']
    user = session['user_info']

    # Fetch GitHub repositories with pagination
    repos = []
    try:
        headers = {'Authorization': f"token {token['access_token']}"}
        page = 1
        while True:
            response = requests.get(
                'https://api.github.com/user/repos',
                headers=headers,
                params={'per_page': 100, 'page': page}
            )
            response.raise_for_status()
            page_repos = response.json()
            if not page_repos:
                break
            repos.extend(page_repos)
            page += 1
    except Exception as e:
        print(f"[ERROR] Failed to fetch repos: {e}")
        repos = []

    return render_template('dashboard.html',
                           user=user,
                           repos=repos,
                           cron_schedules=CRON_SCHEDULES,
                           colors=random.choice(COLOR_SCHEMES),
                           ai_tip=random.choice(AI_TIPS))










from flask import request, render_template
from datetime import datetime
from urllib.parse import urlparse
import os
import random

# @app.route('/submit', methods=['POST'])
# def submit():
#     data = request.form

#     # Get and validate inputs
#     business = data.get('business_name', '').strip()
#     email = data.get('email', '').strip()
#     agent_label = data.get('agent_label', '').strip()
#     monitor_path = data.get('monitor_path', '').strip()
#     source_type = data.get('source_type', '').strip()
#     repo_url = data.get('repo_url', '').strip()
#     cron = data.get('cron_schedule', '').strip()

#     if not all([business, email, agent_label, monitor_path, repo_url, cron]):
#         return "Missing required fields", 400

#     if cron == 'Custom AI Schedule':
#         cron = data.get('custom_cron', '').strip()

#     if len(cron.split()) != 5:
#         return "Invalid cron expression", 400

#     # Process names
#     index_base = business.lower().replace(" ", "-")
#     default_index = f"{index_base}-ai-logs-{datetime.now().year}"
#     index_name = data.get('index_name') or default_index
#     repo_name = os.path.basename(urlparse(repo_url).path).replace('.git', '')

#     # Hardcoded for simplicity
#     splunk_user = "admin"
#     splunk_pass = "changeme"
#     splunk_apps_dir = "C:\\Splunk\\etc\\apps"

#     # Jenkinsfile generation
#     jenkinsfile = f"""// AI-Optimized Splunk Monitoring Pipeline
# pipeline {{
#   agent {{
#     label '{agent_label}'
#   }}
#   environment {{
#     INDEX_NAME = '{index_name}'
#     MONITOR_PATH = '{monitor_path}'
#     SOURCE_TYPE = '{source_type}'
#     REPO_NAME = '{repo_name}'
#     REPO_URL = '{repo_url}'
#     SPLUNK_USERNAME = '{splunk_user}'
#     SPLUNK_PASSWORD = '{splunk_pass}'
#     SPLUNK_APPS_DIR = '{splunk_apps_dir}'
#     EMAIL_RECIPIENT = '{email}'
#   }}
#   triggers {{
#     cron('{cron}')
#   }}
#   stages {{
#     stage('AI Monitor Setup') {{
#       steps {{
#         echo "AI Assistant: Setting up intelligent monitoring"
#         echo "Index: ${{INDEX_NAME}}"
#         echo "Path: ${{MONITOR_PATH}}"
#         echo "Type: ${{SOURCE_TYPE}}"
#       }}
#     }}
#     stage('AI Validation') {{
#       steps {{
#         echo "Validating configuration..."
#         script {{
#           if (env.MONITOR_PATH.contains('*')) {{
#             echo "Wildcard path detected"
#           }}
#           if (env.SOURCE_TYPE == '') {{
#             echo "Warning: Specify a sourcetype"
#           }}
#         }}
#       }}
#     }}
#     stage('Clone Repo to Splunk Apps Directory') {{
#       steps {{
#         bat \"\"\"
# cd "${{SPLUNK_APPS_DIR}}"
# if not exist "${{REPO_NAME}}" (
#     git clone ${{REPO_URL}}
#     rmdir /s /q "${{SPLUNK_APPS_DIR}}\\${{REPO_NAME}}\\.git"
#     echo Repository cloned successfully.
# ) else (
#     echo Repository already exists. Skipping clone.
# )
# \"\"\"
#       }}
#     }}
#     stage('Create Splunk Index') {{
#       steps {{
#         bat \"\"\"
# cd "C:\\Program Files\\Splunk\\bin"
# splunk list index ${{INDEX_NAME}} -auth ${{SPLUNK_USERNAME}}:${{SPLUNK_PASSWORD}} > nul 2>&1
# if errorlevel 1 (
#     echo Index does not exist. Creating index: ${{INDEX_NAME}}
#     splunk add index ${{INDEX_NAME}} -auth ${{SPLUNK_USERNAME}}:${{SPLUNK_PASSWORD}}
# ) else (
#     echo Index '${{INDEX_NAME}}' already exists. Skipping creation.
# )
# \"\"\"
#       }}
#     }}
#     stage('Restart Splunk') {{
#       steps {{
#         bat '"C:\\Program Files\\Splunk\\bin\\splunk" restart'
#       }}
#     }}
#     stage('Send Completion Email') {{
#   steps {{
#     emailext(
#       subject: 'Splunk Deployment Completed Successfully',
#       to: "${{EMAIL_RECIPIENT}}",
#       mimeType: 'text/html',
#       body: \"\"\"<p>Hello,</p>
# <p>The Splunk deployment has been completed successfully. Here are the details:</p>
# <ul>
#   <li>Repository: ${{REPO_NAME}}</li>
#   <li>Index: ${{INDEX_NAME}}</li>
#   <li>Splunk was restarted successfully</li>
# </ul>
# <p>Thanks,<br>Jenkins Automation</p>\"\"\"
#     )
#   }}
# }}

#   }}
#   post {{
#     success {{
#       echo "Deployment completed successfully."
#     }}
#     failure {{
#       echo "Deployment failed."
#     }}
#     always {{
#       echo "Pipeline complete!"
#     }}
#   }}
# }}"""

#     # Save Jenkinsfile
#     os.makedirs('output', exist_ok=True)
#     filename = f"AI-Splunk-Jenkinsfile-{datetime.now().strftime('%Y%m%d-%H%M')}.groovy"
#     with open(f'output/{filename}', 'w', encoding='utf-8') as f:
#         f.write(jenkinsfile)

#     return render_template('result.html',
#                            jenkinsfile=jenkinsfile,
#                            filename=filename,
#                            colors=random.choice(COLOR_SCHEMES),
#                            ai_tip=random.choice(AI_TIPS))

from flask import Flask, request, jsonify
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth

# app = Flask(__name__)

# JENKINS_URL = "http://localhost:8080"
# JENKINS_USER = "admin"
# JENKINS_TOKEN = "your-token-here"
# JENKINS_URL = "http://47.247.224.149:8080/"
# JENKINS_USER = "yaswanth"
# JENKINS_API_TOKEN = "1183a581fe0a195dd792c7f88df81b74c9"

# JENKINS_URL = "http://192.168.100.12:8080/"
# JENKINS_USER = "AzureTeam"
# JENKINS_API_TOKEN = "1183a581fe0a195dd792c7f88df81b74c9"

# @app.route('/create-jenkins-job', methods=['POST'])
# def create_jenkins_job_1():
#     data = request.json
#     if not data:
#         return jsonify(success=False, message="No data received."), 400

#     project = data['project_name'].strip().lower().replace(' ', '-')
#     date_str = datetime.now().strftime('%Y-%m-%d')
#     job_name = f"{project}-{date_str}"

#     jenkinsfile = f"""
#     pipeline {{
#         agent {{
#             label '{data['agent_label']}'
#         }}
#         triggers {{
#             cron('{data['cron_expression']}')
#         }}
#         stages {{
#             stage('Monitor') {{
#                 steps {{
#                     echo 'Monitoring {data['monitor_path']} for {project}'
#                 }}
#             }}
#         }}
#     }}
#     """.strip()

#     job_config = f"""<?xml version='1.1' encoding='UTF-8'?>
#     <flow-definition plugin="workflow-job">
#       <description>AI-created pipeline job</description>
#       <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps">
#         <script>{jenkinsfile}</script>
#         <sandbox>true</sandbox>
#       </definition>
#       <disabled>false</disabled>
#     </flow-definition>
#     """

#     res = requests.post(
#         f"{JENKINS_URL}/createItem?name={job_name}",
#         data=job_config,
#         headers={"Content-Type": "application/xml"},
#         auth=HTTPBasicAuth(JENKINS_USER, JENKINS_API_TOKEN)
#     )

#     if res.status_code == 200:
#         return jsonify(success=True, job_name=job_name)
#     else:
#         return jsonify(success=False, message=res.text), 500







from flask import request, render_template
from datetime import datetime
from urllib.parse import urlparse
import os
import random

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form

    # Get and validate inputs
    business = data.get('business_name', '').strip()
    email = data.get('email', '').strip()
    # agent_label = data.get('agent_label', '').strip()
    # monitor_path = data.get('monitor_path', '').strip()
    # source_type = data.get('source_type', '').strip()
    repo_url = data.get('repo_url', '').strip()
    cron = data.get('cron_schedule', '').strip()

    if not all([business, email, repo_url, cron]):
        return "Missing required fields", 400

    if cron == 'Custom AI Schedule':
        cron = data.get('custom_cron', '').strip()

    if len(cron.split()) != 5:
        return "Invalid cron expression", 400

    # Smart AI-style index name suggestions
    index_base = business.lower().replace(" ", "-")
    year = datetime.now().year

    all_suggestions = [
        f"{index_base}-ai-logs-{year}",
        f"ml-{index_base}-metrics",
        f"ai-{index_base}-analytics",
        f"{index_base}-neural-data",
        f"deep-{index_base}-logs",
        f"{index_base}-model-traces",
        f"smart-{index_base}-insights",
        f"{index_base}-inference-records",
        f"autogen-{index_base}-activity",
        f"{index_base}-intel-metrics"
    ]

    suggestion_count = random.randint(3, 7)
    random.shuffle(all_suggestions)
    index_suggestions = all_suggestions[:suggestion_count]

    # Choose user input or first smart suggestion
    index_name = data.get('index_name') or index_suggestions[0]

    # Extract repo name
    repo_name = os.path.basename(urlparse(repo_url).path).replace('.git', '')

    # Hardcoded for simplicity
   
    splunk_apps_dir = "C:\\program files\\Splunk\\etc\\apps"

    # Jenkinsfile generation
   # // AI-Optimized Splunk Monitoring Pipeline
    jenkinsfile = f"""
pipeline {{
  agent {{
    label 'Azure Team'
  }}
  environment {{
    
  
    REPO_NAME = '{repo_name}'
    REPO_URL = '{repo_url}'
    SPLUNK_USERNAME = 'MTL1013'
    SPLUNK_PASSWORD = 'MTL@1013'
    SPLUNK_APPS_DIR = '{splunk_apps_dir}'
    EMAIL_RECIPIENT = '{email}'
  }}
  triggers {{
    cron('{cron}')
  }}
  stages {{
   

    stage('Clone Repo to Splunk Apps Directory') {{
      steps {{
        bat \"\"\"cd "${{SPLUNK_APPS_DIR}}"
if not exist "${{REPO_NAME}}" (
    git clone ${{REPO_URL}}
    rmdir /s /q "${{SPLUNK_APPS_DIR}}\\${{REPO_NAME}}\\.git"
    echo Repository cloned successfully.
) else (
    echo Repository already exists. Skipping clone.
)\"\"\"
      }}
    }}
    
    stage('Restart Splunk') {{
      steps {{
        bat '"C:\\Program Files\\Splunk\\bin\\splunk" restart'
      }}
    }}
    stage('Send Completion Email') {{
      steps {{
        emailext(
          subject: 'Splunk Deployment Completed Successfully',
          to: "${{EMAIL_RECIPIENT}}",
          mimeType: 'text/html',
          body: \"\"\"<p>Hello,</p>
<p>The Splunk deployment has been completed successfully. Here are the details:</p>
<ul>
  <li>Repository: ${{REPO_NAME}}</li>
  
  <li>Splunk was restarted successfully</li>
</ul>
<p>Thanks,<br>Jenkins Automation</p>\"\"\"
        )
      }}
    }}
  }}
  post {{
    success {{
      echo "Deployment completed successfully."
    }}
    failure {{
      echo "Deployment failed."
    }}
    always {{
      echo "Pipeline complete!"
    }}
  }}
}}"""

    # Save Jenkinsfile
    os.makedirs('output', exist_ok=True)
    filename = f"AI-Splunk-Jenkinsfile-{datetime.now().strftime('%Y%m%d-%H%M')}.groovy"
    with open(f'output/{filename}', 'w', encoding='utf-8') as f:
        f.write(jenkinsfile)

    # Render result
    return render_template(
        'result.html',
        jenkinsfile=jenkinsfile,
        filename=filename,
        colors=random.choice(COLOR_SCHEMES),
        ai_tip=random.choice(AI_TIPS),
        index_suggestions=index_suggestions  # Optional: for display in UI
    )

from flask import request, jsonify
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth

# JENKINS_URL = "http://47.247.224.149:8080/"
# JENKINS_USER = "yaswanth"
# JENKINS_API_TOKEN = "1183a581fe0a195dd792c7f88df81b74c9"


@app.route('/create-jenkins-job', methods=['POST'])
def create_jenkins_job_1():
    data = request.json
    
    print("**********************************************************")

    print(request.json)
    print("*************************************************")
    if not data:
        return jsonify(success=False, message="No data received."), 400

    project = data['project_name'].strip().lower().replace(' ', '-')
    date_str = datetime.now().strftime('%Y-%m-%d')
    job_name = f"{project}-{date_str}"

 
    cron_expression = data['cron_expression']
   
    repo_url = data.get('repo_url', 'https://github.com/yaswanthkumar12-cmyk/Server_Logs.git')
    repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
    email_recipient = data.get('email', 'Yaswanth@middlewaretalents.com')

    jenkinsfile = f"""pipeline {{
    agent {{
        label 'Azure Team'
    }}
    environment {{
       
        REPO_URL = '{repo_url}'
        REPO_NAME = '{repo_name}'
        
        SPLUNK_USERNAME = 'MTL1013'
        SPLUNK_PASSWORD = 'MTL@1013'
        EMAIL_RECIPIENT = '{email_recipient}'
    }}
    triggers {{
        cron('{cron_expression}')
    }}
    stages {{
        stage('Clone Repo to Splunk Apps Directory') {{
            
            steps {{
        bat \"\"\"cd "${{SPLUNK_APPS_DIR}}"
if not exist "${{REPO_NAME}}" (
    git clone ${{REPO_URL}}
    rmdir /s /q "${{SPLUNK_APPS_DIR}}\\${{REPO_NAME}}\\.git"
    echo Repository cloned successfully.
) else (
    echo Repository already exists. Skipping clone.
)\"\"\"
      }}

        }}
    }}
    post {{
        success {{
            echo "Success"
        }}
        failure {{
            echo "Failure"
        }}
    }}
}}"""

    job_config = f"""<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job">
  <description>Auto-created job</description>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps">
    <script>{jenkinsfile}</script>
    <sandbox>true</sandbox>
  </definition>
  <disabled>false</disabled>
</flow-definition>
"""

    response = requests.post(
    f"{JENKINS_URL}/createItem?name={job_name}",
    data=job_config,
    headers={"Content-Type": "application/xml"},
    auth=HTTPBasicAuth(JENKINS_USERNAME, JENKINS_API_TOKEN)
)


    if response.status_code == 200:
        return jsonify(success=True, job_name=job_name)
    else:
        return jsonify(success=False, message=response.text), 500


# @app.route('/create-jenkins-job', methods=['POST'])
# def create_jenkins_job_1():
#     data = request.json
#     project = data['project_name'].strip().lower().replace(' ', '-')
#     date_str = datetime.now().strftime('%Y-%m-%d')
#     job_name = f"{project}-{date_str}"

#     jenkinsfile = f"""
# pipeline {{
#     agent {{
#         label '{data['agent_label']}'
#     }}
#     triggers {{
#         cron('{data['cron_expression']}')
#     }}
#     stages {{
#         stage('Monitor') {{
#             steps {{
#                 echo 'Monitoring {data['monitor_path']} for {project}'
#             }}
#         }}
#     }}
# }}
#     """.strip()

#     job_config = f"""<?xml version='1.1' encoding='UTF-8'?>
# <flow-definition plugin="workflow-job">
#   <description>AI-created pipeline job</description>
#   <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps">
#     <script>{jenkinsfile}</script>
#     <sandbox>true</sandbox>
#   </definition>
#   <disabled>false</disabled>
# </flow-definition>
# """

#     res = requests.post(
#         f"{JENKINS_URL}/createItem?name={job_name}",
#         data=job_config,
#         headers={"Content-Type": "application/xml"},
#         auth=HTTPBasicAuth(JENKINS_USER, JENKINS_TOKEN)
#     )

#     if res.status_code == 200:
#         return jsonify(success=True, job_name=job_name)
#     else:
#         return jsonify(success=False, message=res.text), 500



# @app.route('/submit', methods=['POST'])
# def submit():
#     data = request.form
#     business = data['business_name']
#     index_base = business.lower().replace(" ", "-")

    # suggestions = [
    #     f"{index_base}-ai-logs-{datetime.now().year}",
    #     f"ml-{index_base}-metrics",
    #     f"ai-{index_base}-analytics",
    #     f"{index_base}-neural-data",
    #     f"deep-{index_base}-logs"
    # ]

    # index_name = data.get('index_name') or suggestions[0]
#     cron = data['cron_schedule']
#     if cron == 'Custom AI Schedule':
#         cron = data['custom_cron']

#     jenkinsfile = f"""// AI-Optimized Splunk Monitoring Pipeline
# pipeline {{
#   agent {{
#     label '{data['agent_label']}'
#   }}
#   environment {{
#     INDEX_NAME = '{index_name}'
#     MONITOR_PATH = '{data['monitor_path']}'
#     SOURCE_TYPE = '{data['source_type']}'
#   }}
#   triggers {{
#     cron('{cron}')
#   }}
#   stages {{
#     stage('AI Monitor Setup') {{
#       steps {{
#         echo "AI Assistant: Setting up intelligent monitoring"
#         echo "Index: ${{INDEX_NAME}}"
#         echo "Path: ${{MONITOR_PATH}}"
#         echo "Type: ${{SOURCE_TYPE}}"
#       }}
#     }}
#     stage('AI Validation') {{
#       steps {{
#         echo "Validating configuration..."
#         script {{
#           if (env.MONITOR_PATH.contains('*')) {{
#             echo "Wildcard path detected"
#           }}
#           if (env.SOURCE_TYPE == '') {{
#             echo "Warning: Specify a sourcetype"
#           }}
#         }}
#       }}
#     }}
#   }}
#   post {{
#     always {{
#       echo "Pipeline complete!"
#     }}
#   }}
# }}"""

#     os.makedirs('output', exist_ok=True)
#     filename = f"AI-Splunk-Jenkinsfile-{datetime.now().strftime('%Y%m%d-%H%M')}.groovy"
    
#     # Save with UTF-8 encoding to handle special characters
#     with open(f'output/{filename}', 'w', encoding='utf-8') as f:
#         f.write(jenkinsfile)

#     # Render template without emoji unicode characters
#     return render_template('result.html',
#                          jenkinsfile=jenkinsfile,
#                          filename=filename,
#                          colors=random.choice(COLOR_SCHEMES),
#                          ai_tip=random.choice(AI_TIPS))






# @app.route('/submit', methods=['POST'])
# def submit():
#     data = request.form

#     # Safely get required values
#     business = data.get('business_name', '').strip()
#     email = data.get('email', '').strip()
#     agent_label = data.get('agent_label', '').strip()
#     monitor_path = data.get('monitor_path', '').strip()

#     if not all([business, email, agent_label, monitor_path]):
#         return "Missing required fields", 400

#     index_base = business.lower().replace(" ", "-")
#     suggestions = [
#         f"{index_base}-ai-logs-{datetime.now().year}",
#         f"ml-{index_base}-metrics",
#         f"ai-{index_base}-analytics",
#         f"{index_base}-neural-data",
#         f"deep-{index_base}-logs"
#     ]

#     index_name = data.get('index_name') or suggestions[0]
#     source_type = data.get('source_type', '')

#     # Cron handling
#     cron = data.get('cron_schedule', '').strip()
#     if cron == 'Custom AI Schedule':
#         cron = data.get('custom_cron', '').strip()

#     # Validate cron format (basic check: 5 parts)
#     if len(cron.split()) != 5:
#         return "Invalid cron expression", 400

#     # Create Jenkinsfile content
#     jenkinsfile = f"""// AI-Optimized Splunk Monitoring Pipeline
# pipeline {{
#   agent {{
#     label '{agent_label}'
#   }}
#   environment {{
#     INDEX_NAME = '{index_name}'
#     MONITOR_PATH = '{monitor_path}'
#     SOURCE_TYPE = '{source_type}'
#   }}
#   triggers {{
#     cron('{cron}')
#   }}
#   stages {{
#     stage('AI Monitor Setup') {{
#       steps {{
#         echo "AI Assistant: Setting up intelligent monitoring"
#         echo "Index: ${{INDEX_NAME}}"
#         echo "Path: ${{MONITOR_PATH}}"
#         echo "Type: ${{SOURCE_TYPE}}"
#       }}
#     }}
#     stage('AI Validation') {{
#       steps {{
#         echo "Validating configuration..."
#         script {{
#           if (env.MONITOR_PATH.contains('*')) {{
#             echo "Wildcard path detected"
#           }}
#           if (env.SOURCE_TYPE == '') {{
#             echo "Warning: Specify a sourcetype"
#           }}
#         }}
#       }}
#     }}
#   }}
#   post {{
#     always {{
#       echo "Pipeline complete!"
#     }}
#   }}
# }}"""

#     # Save file
#     os.makedirs('output', exist_ok=True)
#     filename = f"AI-Splunk-Jenkinsfile-{datetime.now().strftime('%Y%m%d-%H%M')}.groovy"
#     with open(f'output/{filename}', 'w', encoding='utf-8') as f:
#         f.write(jenkinsfile)

#     # Render the result page
#     return render_template('result.html',
#                            jenkinsfile=jenkinsfile,
#                            filename=filename,
#                            colors=random.choice(COLOR_SCHEMES),
#                            ai_tip=random.choice(AI_TIPS))




# Temporary user storage (in-memory dictionary)
users = {}

@app.route('/')
def main():
    if 'username' in session:
        jobs = get_jenkins_jobs_home()
        job_counts = {
        "total": len(jobs),
        "success": sum(1 for job in jobs if job["status"] == "SUCCESS"),
        "pending": sum(1 for job in jobs if job["status"] == "RUNNING"),
        "failed": sum(1 for job in jobs if job["status"] == "FAILURE")
    }
        return render_template("main.html", jobs=jobs, job_counts=job_counts, username=session['username'])  # Admin panel
    return render_template('login.html')  # If not logged in, go to login







def get_jenkins_jobs_home():
    """Fetch Jenkins jobs."""
    api_url = f"{JENKINS_URL}/api/json?tree=jobs[name,url,color]"
    try:
        response = requests.get(api_url, auth=HTTPBasicAuth(JENKINS_USERNAME, JENKINS_API_TOKEN))
        response.raise_for_status()  # Ensure we get a successful response
        jobs_raw = response.json().get("jobs", [])

        job_list = []
        for job in jobs_raw:
            color = job.get("color", "")
            status = (
                "RUNNING" if "anime" in color else
                "SUCCESS" if "blue" in color else
                "FAILURE" if "red" in color else
                "UNKNOWN"
            )
            job_list.append({
                "name": job["name"],
                "url": job["url"],
                "status": status
            })

        return job_list
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Jenkins jobs: {e}")
        return []  # Return an empty list if an error occurs








@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('main'))  # Successful login
        # Invalid credentials - show login page with error message
        return render_template('login.html', error="Invalid username or password.")
    
    return render_template('login.html')  # GET request: just show login
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users:
            return render_template('register.html', error="User already exists.")
        users[username] = password
        print("******************************")
        print(username)
        print(password)
        print("*******************************")
        return render_template('register.html', success="User created successfully.")
    return render_template('register.html')
# @app.route("/dashboard")
# def dashboard():
#     return render_template('dashboard.html')

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')

# @app.route("/jenkins")
# def jenkins():
#     return render_template('jenkins.html')
@app.route("/jenkins")
def jenkins():
    return get_jenkins_jobs()

# JENKINS_URL = "http://47.247.224.149:8080/"
# JENKINS_USERNAME = "yaswanth"
# JENKINS_API_TOKEN = "1183a581fe0a195dd792c7f88df81b74c9"
# Jenkins configuration
# JENKINS_URL = "http://192.168.100.12:8080/"
# JENKINS_USERNAME = "AzureTeam"
# JENKINS_API_TOKEN = "11029516d336cd3e4659d68ed54c21cd98"
# JENKINS_URL = "https://504d-136-232-205-158.ngrok-free.app"
# JENKINS_USERNAME = "EshwarBashaBathini"
# JENKINS_API_TOKEN = "113ec86ef3be1f0475adf8890a34010929"

# @app.route('/')
# def index():
#     return get_jenkins_jobs()


@app.route('/get_jenkins_jobs', methods=['GET'])
def get_jenkins_jobs():
    url = f"{JENKINS_URL}/api/json"
    auth = HTTPBasicAuth(JENKINS_USERNAME, JENKINS_API_TOKEN)
    
    try:
        response = requests.get(url, auth=auth)
        if response.status_code == 200:
            jobs_data = response.json()
            jobs = []
            for job in jobs_data.get('jobs', []):
                # Get pipeline script for each job
                job_url = f"{JENKINS_URL}/job/{job['name']}/config.xml"
                job_response = requests.get(job_url, auth=auth)
                if job_response.status_code == 200:
                    job['config_xml'] = job_response.text
                else:
                    job['config_xml'] = "Unable to fetch pipeline configuration"
                
                # Get the build history for each job
                build_history_url = f"{JENKINS_URL}/job/{job['name']}/api/json?tree=builds[number,status,timestamp,result]"
                build_history_response = requests.get(build_history_url, auth=auth)
                if build_history_response.status_code == 200:
                    build_history = build_history_response.json().get('builds', [])
                    if build_history:
                        # Add the latest build status to the job
                        job['latest_build'] = {
                            'number': build_history[0]['number'],
                            'status': build_history[0]['result'] if 'result' in build_history[0] else 'RUNNING',
                            'timestamp': build_history[0]['timestamp']
                        }
                    else:
                        job['latest_build'] = None
                else:
                    job['latest_build'] = None

                jobs.append(job)
            return render_template('jenkins_jobs.html', jobs=jobs)
        else:
            return render_template('jenkins_jobs.html', jobs=[], error="Failed to fetch Jenkins jobs")
    except Exception as e:
        return render_template('jenkins_jobs.html', jobs=[], error=str(e))

@app.route('/trigger_jenkins_build/<job_name>', methods=['POST'])
def trigger_jenkins_build(job_name):
    try:
        url = f"{JENKINS_URL}/job/{job_name}/build"
        response = requests.post(url, auth=HTTPBasicAuth(JENKINS_USERNAME, JENKINS_API_TOKEN))
        
        if response.status_code == 201:
            return jsonify({"status": "success", "message": f"Build for {job_name} triggered successfully!"})
        else:
            return jsonify({"status": "error", "message": f"Failed to trigger build. Status: {response.status_code}"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_build_logs/<job_name>', methods=['GET'])
def get_jenkins_build_logs(job_name):
    try:
        url = f"{JENKINS_URL}/job/{job_name}/lastBuild/consoleText"
        response = requests.get(url, auth=HTTPBasicAuth(JENKINS_USERNAME, JENKINS_API_TOKEN))
        
        if response.status_code == 200:
            return jsonify({"status": "success", "logs": response.text})
        else:
            return jsonify({"status": "error", "message": "Failed to fetch build logs."}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/create_jenkins_job', methods=['POST'])
def create_jenkins_job():
    try:
        data = request.get_json()
        job_name = data['jobName']
        jenkinsfile_url = data['jenkinsfileUrl']
        job_description = data.get('jobDescription', '')
        job_type = data.get('jobType', 'pipeline')
        branch_specifier = data.get('branchSpecifier', '*/main')
        webhook_enabled = data.get('webhookEnabled', False)
        cron_trigger_enabled = data.get('cronTriggerEnabled', False)
        cron_schedule = data.get('cronSchedule', 'H/15 * * * *')

        # Basic pipeline configuration
        job_config_xml = f"""<?xml version='1.1' encoding='UTF-8'?>
        <flow-definition plugin="workflow-job@2.40">
            <actions/>
            <description>{job_description}</description>
            <keepDependencies>false</keepDependencies>
            <properties/>
            <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps@2.80">
                <scm class="hudson.plugins.git.GitSCM" plugin="git@4.7.1">
                    <configVersion>2</configVersion>
                    <userRemoteConfigs>
                        <hudson.plugins.git.UserRemoteConfig>
                            <url>{jenkinsfile_url}</url>
                        </hudson.plugins.git.UserRemoteConfig>
                    </userRemoteConfigs>
                    <branches>
                        <hudson.plugins.git.BranchSpec>
                            <name>{branch_specifier}</name>
                        </hudson.plugins.git.BranchSpec>
                    </branches>
                    <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
                    <submoduleCfg class="list"/>
                    <extensions/>
                </scm>
                <scriptPath>Jenkinsfile</scriptPath>
                <lightweight>true</lightweight>
            </definition>
            <triggers>"""

        # Add triggers if enabled
        if webhook_enabled:
            job_config_xml += """
                <jenkins.triggers.ReverseBuildTrigger>
                    <spec/>
                    <upstreamProjects/>
                    <threshold>
                        <name>SUCCESS</name>
                        <ordinal>0</ordinal>
                        <color>BLUE</color>
                        <completeBuild>true</completeBuild>
                    </threshold>
                </jenkins.triggers.ReverseBuildTrigger>"""

        if cron_trigger_enabled:
            job_config_xml += f"""
                <hudson.triggers.TimerTrigger>
                    <spec>{cron_schedule}</spec>
                </hudson.triggers.TimerTrigger>"""

        job_config_xml += """
            </triggers>
            <disabled>false</disabled>
        </flow-definition>"""

        create_job_url = f"{JENKINS_URL}/createItem?name={job_name}"
        headers = {'Content-Type': 'application/xml'}

        response = requests.post(
            create_job_url,
            data=job_config_xml,
            headers=headers,
            auth=HTTPBasicAuth(JENKINS_USERNAME, JENKINS_API_TOKEN)
        )

        if response.status_code in [200, 201]:
            return jsonify({
                "status": "success", 
                "message": f"Jenkins job {job_name} created successfully!",
                "job_url": f"{JENKINS_URL}/job/{job_name}"
            })
        else:
            return jsonify({
                "status": "error", 
                "message": f"Failed to create job. Status: {response.status_code}, Response: {response.text}"
            }), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500




# @app.route('/update_pipeline_script/<job_name>', methods=['POST'])
# def update_pipeline_script(job_name):
#     try:
#         data = request.get_json()
#         new_script = data['script']  # Extract the new script from the request body
#         # Fetch the current job's config XML first
#         job_url = f"{JENKINS_URL}/job/{job_name}/config.xml"
#         response = requests.get(job_url, auth=HTTPBasicAuth(JENKINS_USERNAME, JENKINS_API_TOKEN))
        
#         if response.status_code != 200:
#             return jsonify({"status": "error", "message": "Failed to fetch the pipeline config"}), 400

#         # Modify the <script> section in the XML (you may need to parse and update the XML here)
#         config_xml = response.text
#         # Assuming the <script> section is in the config and replacing it
#         config_xml = config_xml.replace('<script>.*</script>', f'<script>{new_script}</script>')

#         # Now, update the pipeline with the new config
#         headers = {'Content-Type': 'application/xml'}
#         update_response = requests.post(
#             job_url,
#             data=config_xml,  # Send the modified config XML back
#             headers=headers,
#             auth=HTTPBasicAuth(JENKINS_USERNAME, JENKINS_API_TOKEN)
#         )

#         if update_response.status_code == 200:
#             return jsonify({"status": "success", "message": "Pipeline script updated successfully!"})
#         else:
#             return jsonify({
#                 "status": "error",
#                 "message": f"Failed to update pipeline script. Status: {update_response.status_code}, Response: {update_response.text}"
#             }), 400

#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500

from flask import request, jsonify
import requests
from requests.auth import HTTPBasicAuth
import re
import xml.sax.saxutils as saxutils













@app.route('/delete_jenkins_job/<job_name>', methods=['POST'])
def delete_jenkins_job(job_name):
    try:
        url = f"{JENKINS_URL}/job/{job_name}/doDelete"
        response = requests.post(url, auth=HTTPBasicAuth(JENKINS_USERNAME, JENKINS_API_TOKEN))
        
        if response.status_code == 200:
            return jsonify({"status": "success", "message": f"Job {job_name} deleted successfully!"})
        else:
            return jsonify({"status": "error", "message": f"Failed to delete job. Status: {response.status_code}"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_pipeline_config/<job_name>', methods=['GET'])
def get_pipeline_config(job_name):
    try:
        url = f"{JENKINS_URL}/job/{job_name}/config.xml"
        response = requests.get(url, auth=HTTPBasicAuth(JENKINS_USERNAME, JENKINS_API_TOKEN))
        
        if response.status_code == 200:
            return jsonify({"status": "success", "config": response.text})
        else:
            return jsonify({"status": "error", "message": "Failed to fetch pipeline config"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500




import re
import requests
from flask import Flask, request, jsonify
from requests.auth import HTTPBasicAuth
from xml.sax import saxutils
from urllib.parse import quote  # <-- Import this


@app.route('/update_pipeline_script/<path:job_name>', methods=['POST'])
def update_pipeline_script(job_name):
    try:
        # Get the new pipeline script from the request body
        data = request.get_json()
        new_script = data['script']

        # Construct the job URL to fetch the current config.xml
        encoded_job_path = '/'.join(f'job/{quote(part)}' for part in job_name.split('/'))
        job_url = f"{JENKINS_URL}/{encoded_job_path}/config.xml"
        
        # Fetch the current job config (XML)
        response = requests.get(job_url, auth=HTTPBasicAuth(JENKINS_USERNAME, JENKINS_API_TOKEN))

        if response.status_code != 200:
            return jsonify({"status": "error", "message": "Failed to fetch pipeline config"}), 400

        config_xml = response.text

        # Escape the new script to make it XML-safe
        escaped_script = saxutils.escape(new_script)

        # Replace the <script>...</script> section using regex
        updated_config = re.sub(
            r'<script>.*?</script>',
            f'<script>{escaped_script}</script>',
            config_xml,
            flags=re.DOTALL
        )

        # Post the updated config back to Jenkins
        headers = {'Content-Type': 'application/xml'}
        update_response = requests.post(
            job_url,
            data=updated_config,
            headers=headers,
            auth=HTTPBasicAuth(JENKINS_USERNAME, JENKINS_API_TOKEN)
        )

        if update_response.status_code == 200:
            return jsonify({"status": "success", "message": "Pipeline script updated successfully!"})
        else:
            return jsonify({
                "status": "error",
                "message": f"Failed to update pipeline. Status: {update_response.status_code}, Response: {update_response.text}"
            }), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500





# @app.route('/update_pipeline_config/<job_name>', methods=['POST'])
# def update_pipeline_config(job_name):
#     try:
#         data = request.get_json()
#         new_config = data['config']
#         url = f"{JENKINS_URL}/job/{job_name}/config.xml"
#         headers = {'Content-Type': 'application/xml'}

#         response = requests.post(
#             url, 
#             data=new_config, 
#             headers=headers, 
#             auth=HTTPBasicAuth(JENKINS_USERNAME, JENKINS_API_TOKEN)
#         )

#         if response.status_code == 200:
#             return jsonify({"status": "success", "message": "Pipeline updated successfully!"})
#         else:
#             return jsonify({
#                 "status": "error", 
#                 "message": f"Failed to update pipeline. Status: {response.status_code}, Response: {response.text}"
#             }), 400
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/get_build_history/<job_name>', methods=['GET'])
def get_build_history(job_name):
    try:
        url = f"{JENKINS_URL}/job/{job_name}/api/json?tree=builds[number,result,timestamp,duration,url]"
        response = requests.get(url, auth=HTTPBasicAuth(JENKINS_USERNAME, JENKINS_API_TOKEN))
        
        if response.status_code == 200:
            builds = response.json().get('builds', [])
            # Process builds to include status (result) and formatted timestamp
            processed_builds = []
            for build in builds:
                processed_builds.append({
                    'number': build['number'],
                    'status': build.get('result', 'RUNNING'),
                    'timestamp': build['timestamp'],
                    'duration': build['duration'],
                    'url': build['url']
                })
            return jsonify({"status": "success", "builds": processed_builds})
        else:
            return jsonify({"status": "error", "message": "Failed to fetch build history."}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500





import requests
import splunklib.client as splunk_client
from flask import Flask, render_template, request, jsonify

import splunklib.client as splunk_client
from flask import Flask, render_template, request



# @app.route('/test_connection', methods=['GET', 'POST'])
# def test_connection():
#     if request.method == 'POST':
#         # Get form data (Splunk credentials from user)
#         splunk_host = request.form['splunk_host']
#         splunk_port = request.form['splunk_port']
#         splunk_user = request.form['splunk_user']
#         splunk_pass = request.form['splunk_pass']

#         # Test Splunk connection
#         try:
#             splunk_service = splunk_client.connect(
#                 host=splunk_host,
#                 port=int(splunk_port),
#                 username=splunk_user,
#                 password=splunk_pass
#             )
#             result_message = "✅ Splunk connected successfully!"  # Success message
#             result_style = "success"  # Style for success (green)
#         except Exception as e:
#             result_message = f"❌ Splunk Connection Failed: {e}"  # Error message
#             result_style = "error"  # Style for error (red)

#         # Render the result page
#         return render_template('test_connection.html', result_message=result_message, result_style=result_style)

#     # GET request to show the empty form
#     return render_template('test_connection.html')



@app.route('/test_connection', methods=['GET', 'POST'])
def test_connection():
    result_message = ""
    result_style = ""
    jenkins_result_message = ""
    jenkins_result_style = ""

    if request.method == 'POST':
        # Splunk Settings
        splunk_host = request.form.get('splunk_host')
        splunk_port = request.form.get('splunk_port')
        splunk_user = request.form.get('splunk_user')
        splunk_pass = request.form.get('splunk_pass')

        try:
            # Simulate Splunk connection here (example)
            splunk_service = splunk_client.connect(
                host=splunk_host,
                port=int(splunk_port),
                username=splunk_user,
                password=splunk_pass
            )
            result_message = "✅ Splunk connected successfully!"
            result_style = "success"
        except Exception as e:
            result_message = f"❌ Splunk Connection Failed: {e}"
            result_style = "error"

        # Jenkins Settings
        jenkins_url = request.form.get('jenkins_url')
        jenkins_username = request.form.get('jenkins_username')
        jenkins_api_token = request.form.get('jenkins_api_token')

        try:
            # Simulate Jenkins connection here (example)
            jenkins_response = requests.get(
                f"{jenkins_url}/api/json",
                auth=(jenkins_username, jenkins_api_token)
            )
            if jenkins_response.status_code == 200:
                jenkins_result_message = "✅ Jenkins connected successfully!"
                jenkins_result_style = "success"
            else:
                jenkins_result_message = f"❌ Jenkins Connection Failed: {jenkins_response.status_code}"
                jenkins_result_style = "error"
        except Exception as e:
            jenkins_result_message = f"❌ Jenkins Connection Failed: {e}"
            jenkins_result_style = "error"

        return render_template(
            'test_connection.html', 
            result_message=result_message,
            result_style=result_style,
            jenkins_result_message=jenkins_result_message,
            jenkins_result_style=jenkins_result_style
        )

    return render_template('test_connection.html')




# @app.route("/splunk")
# def splunk():
#     return render_template('splunk.html')






import os
import requests
from flask import Flask, render_template, jsonify, request
from requests.auth import HTTPBasicAuth

# Splunk connection settings
SPLUNK_HOST = '127.0.0.1'
SPLUNK_PORT = '8089'  # Splunk management port
SPLUNK_WEB_PORT = '8000'  # Splunk web UI port
SPLUNK_USER = 'MTL1013'
SPLUNK_PASSWORD = 'MTL@1013'
@app.route("/splunk")
def splunk():
    return render_template('splunk.html')

def splunk_session():
    session = requests.Session()
    session.auth = HTTPBasicAuth(SPLUNK_USER, SPLUNK_PASSWORD)
    session.verify = False  # Only for local/dev
    return session

# @app.route('/')
# def home():
#     return render_template('splunk.html')

# @app.route('/splunk')
# def splunk_page():
#     return render_template('splunk_enhanced.html')

@app.route('/splunk_status')
def splunk_status():
    try:
        # Check if Splunk web interface is accessible
        response = requests.get(f'http://{SPLUNK_HOST}:{SPLUNK_WEB_PORT}', timeout=5)
        response.raise_for_status()
        return jsonify({'status': 'success', 'message': 'Splunk is running and accessible.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/splunk_dashboards')
def splunk_dashboards():
    try:
        session = splunk_session()
        url = f'https://{SPLUNK_HOST}:{SPLUNK_PORT}/servicesNS/admin/search/data/ui/views?output_mode=json'
        response = session.get(url)
        response.raise_for_status()

        entries = response.json().get('entry', [])
        dashboards = [{
            'name': entry['name'],
            'label': entry['content'].get('label', entry['name']),
            'description': entry['content'].get('description', '')
        } for entry in entries]

        return jsonify(dashboards)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/splunk_search/<dashboard_name>')
def splunk_search_dashboard(dashboard_name):
    try:
        session = splunk_session()
        url = f'https://{SPLUNK_HOST}:{SPLUNK_PORT}/servicesNS/admin/search/data/ui/views/{dashboard_name}?output_mode=json'
        response = session.get(url)
        response.raise_for_status()

        dashboard = response.json()['entry'][0]
        return jsonify({
            'name': dashboard['name'],
            'label': dashboard['content'].get('label', dashboard['name']),
            'description': dashboard['content'].get('description', ''),
            'content': {
                'xml': dashboard['content'].get('eai:data', 'No definition available.')
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/splunk_indexes')
def splunk_indexes():
    try:
        session = splunk_session()
        url = f'https://{SPLUNK_HOST}:{SPLUNK_PORT}/services/data/indexes?output_mode=json'
        response = session.get(url)
        response.raise_for_status()

        indexes = []
        for entry in response.json().get('entry', []):
            indexes.append({
                'name': entry['name'],
                'totalEventCount': entry['content'].get('totalEventCount', 'N/A'),
                'currentDBSizeMB': entry['content'].get('currentDBSizeMB', 'N/A'),
                'disabled': entry['content'].get('disabled', False)
            })
        return jsonify(indexes)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/splunk_recent_logs')
def splunk_recent_logs():
    try:
        index = request.args.get('index', '*')
        count = request.args.get('count', '10')
        
        session = splunk_session()
        search_query = f'search index="{index}" | head {count}'
        url = f'https://{SPLUNK_HOST}:{SPLUNK_PORT}/services/search/jobs'
        
        # Start the search job
        response = session.post(url, data={
            'search': search_query,
            'output_mode': 'json'
        })
        response.raise_for_status()
        
        sid = response.json()['sid']
        
        # Wait for results
        results_url = f'https://{SPLUNK_HOST}:{SPLUNK_PORT}/services/search/jobs/{sid}/results'
        params = {
            'output_mode': 'json',
            'count': count
        }
        
        import time
        for _ in range(10):  # Try 10 times with 1 second delay
            time.sleep(1)
            response = session.get(results_url, params=params)
            if response.status_code == 200:
                break
        
        response.raise_for_status()
        results = response.json().get('results', [])
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/splunk_search')
def splunk_search():
    try:
        query = request.args.get('query')
        index = request.args.get('index', '*')
        realtime = request.args.get('realtime', 'false').lower() == 'true'
        
        if not query:
            return jsonify({'status': 'error', 'message': 'Search query is required'}), 400
            
        session = splunk_session()
        search_query = f'search index="{index}" {query}'
        if not realtime:
            search_query += ' | head 100'
            
        url = f'https://{SPLUNK_HOST}:{SPLUNK_PORT}/services/search/jobs'
        
        # Start the search job
        response = session.post(url, data={
            'search': search_query,
            'output_mode': 'json',
            'exec_mode': 'normal' if not realtime else 'realtime'
        })
        response.raise_for_status()
        
        sid = response.json()['sid']
        
        # Get results
        results_url = f'https://{SPLUNK_HOST}:{SPLUNK_PORT}/services/search/jobs/{sid}/results'
        params = {
            'output_mode': 'json',
            'count': 0 if realtime else 100
        }
        
        response = session.get(results_url, params=params)
        response.raise_for_status()
        results = response.json().get('results', [])
        
        return jsonify({
            'status': 'success',
            'results': results
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/splunk_apps')
def splunk_apps():
    try:
        session = splunk_session()
        url = f'https://{SPLUNK_HOST}:{SPLUNK_PORT}/services/apps/local?output_mode=json'
        response = session.get(url)
        response.raise_for_status()

        apps = []
        for entry in response.json().get('entry', []):
            apps.append({
                'name': entry['name'],
                'version': entry['content'].get('version', 'N/A'),
                'author': entry['content'].get('author', 'N/A'),
                'disabled': entry['content'].get('disabled', False)
            })
        return jsonify(apps)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/splunk_users')
def splunk_users():
    try:
        session = splunk_session()
        url = f'https://{SPLUNK_HOST}:{SPLUNK_PORT}/services/authentication/users?output_mode=json'
        response = session.get(url)
        response.raise_for_status()

        users = []
        for entry in response.json().get('entry', []):
            users.append({
                'name': entry['name'],
                'realName': entry['content'].get('realname', 'N/A'),
                'email': entry['content'].get('email', 'N/A'),
                'roles': entry['content'].get('roles', [])
            })
        return jsonify(users)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

















@app.route("/Github")
def github_Home():
    return render_template('Github_login.html')
oauth = OAuth(app)
github = oauth.register(
    name='github',
       client_id="Ov23lif5RfEOfW3POIuE",
    client_secret="db4a1b83b2c99d7a3157dd1372b67dac6dbd5fb1",
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'repo'},
    redirect_uri='http://127.0.0.1:5000/auth/github/callback'
)



@app.route('/Github/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    scopes = [
        'repo', 'delete_repo', 'user', 'notifications', 'gist', 'read:org', 'write:org',
        'admin:org', 'read:repo_hook', 'write:repo_hook', 'admin:repo_hook', 'read:discussion',
        'write:discussion', 'admin:discussion', 'public_repo', 'repo:status', 'repo_deployment',
        'workflow', 'security_events'
    ]
    return github.authorize_redirect(redirect_uri, scope=scopes)
@app.route('/auth/github/callback')
def auth():
    # Get the GitHub OAuth token after successful authorization
    token = github.authorize_access_token()

    # Get the user's GitHub profile
    user_response = github.get('user')
    user = user_response.json()  # Convert the response to JSON
    
    # Print user details for debugging
    print(user)
    
    # Extract and parse 'created_at' date
    created_at_str = user.get('created_at', '')
    repos_response = github.get('user/repos', params={'type': 'all'})
    repos = repos_response.json()  # Convert repos response to JSON
    
    # # Print repos for debugging
    # print(repos)

    # Parse the 'created_at' timestamp if available
    if created_at_str:
        created_at = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%SZ")
        created_at_date = created_at.date().strftime("%Y-%m-%d")
        print(created_at_date)
    else:
        created_at_date = ''

    # Store the token and user info in session
    session['github_token'] = token
    session['github_user'] = user['login']
    
    # Store detailed user info in session
    session['user_info'] = {
        'name': user.get('name', ''),
        'username': user.get('login', ''),
        'email': user.get('email', ''),
        'bio': user.get('bio', ''),
        'avatar_url': user.get('avatar_url', ''),
        'public_repos': user.get('public_repos', 0),
        'followers': user.get('followers', 0),
        'following': user.get('following', 0),
        'html_url': user.get('html_url', ''),
        'created_at': created_at_date
    }

    # Redirect the user to the home page
    return redirect(url_for('home'))
# @app.route('/home')
# def home():
#     return 'Welcome to the home page!'


@app.route('/home')
def home():
    if 'github_token' in session:
        username = session['github_user']
        token = session['github_token']['access_token']
        headers = {'Authorization': f'token {token}'}
       
        repos = []
        page = 1
        per_page = 100  # Maximum allowed by GitHub API
        
        while True:
            repos_resp = requests.get(
                f'https://api.github.com/users/{username}/repos?per_page={per_page}&page={page}',
                headers=headers
            )
            if repos_resp.ok:
                repos_page = repos_resp.json()
                if not repos_page:
                    break
                repos.extend(repos_page)
                page += 1
            else:
                break
        for repo in repos:
            print(f"Repo: {repo['name']}, Private: {repo.get('private')}")

       

        private_repos = sum(1 for repo in repos if repo.get('private', False))
        public_repos = len(repos) - private_repos  # The rest are 
        return render_template("Github_dashboard.html", username=username, repos=repos,private_repos=private_repos, public_repos=public_repos)

    return render_template("login.html")

@app.route('/repos/<owner>/<repo_name>/contents/', defaults={'path': ''})
@app.route('/repos/<owner>/<repo_name>/contents/<path:path>')
def show_contents(owner, repo_name, path):
    if 'github_token' not in session:
        return redirect(url_for('login'))

    token = session['github_token']['access_token']
    headers = {'Authorization': f'token {token}'}

    repo_info_url = f"https://api.github.com/repos/{owner}/{repo_name}"
    repo_info = requests.get(repo_info_url, headers=headers).json()
    repo_private = repo_info.get("private", False)

    branches_url = f"https://api.github.com/repos/{owner}/{repo_name}/branches"
    branches_resp = requests.get(branches_url, headers=headers)
    branches = branches_resp.json() if branches_resp.ok else []

    api_url = f'https://api.github.com/repos/{owner}/{repo_name}/contents/{path}'
    response = requests.get(api_url, headers=headers)
    
    if not response.ok:
        return jsonify({'error': 'Failed to fetch repository contents', 'details': response.json()}), 400

    contents = response.json()
    query = request.args.get('q', '').lower()
    if query:
        contents = [item for item in contents if query in item.get('name', '').lower()]

    enriched_contents = []
    for item in contents:
        latest_commit_message = None
        last_updated_time = None

        commits_url = f'https://api.github.com/repos/{owner}/{repo_name}/commits'
        params = {'path': item['path'], 'per_page': 1}
        commits_response = requests.get(commits_url, headers=headers, params=params)

        if commits_response.status_code == 200 and commits_response.json():
            commit_data = commits_response.json()[0]
            latest_commit_message = commit_data['commit']['message']
            commit_date = commit_data['commit']['committer']['date']

            commit_datetime = parser.isoparse(commit_date)
            now = datetime.now(timezone.utc)
            diff = relativedelta(now, commit_datetime)

            if diff.years > 0:
                last_updated_time = f"{diff.years} year{'s' if diff.years > 1 else ''} ago"
            elif diff.months > 0:
                last_updated_time = f"{diff.months} month{'s' if diff.months > 1 else ''} ago"
            elif diff.days > 0:
                last_updated_time = f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
            elif diff.hours > 0:
                last_updated_time = f"{diff.hours} hour{'s' if diff.hours > 1 else ''} ago"
            elif diff.minutes > 0:
                last_updated_time = f"{diff.minutes} minute{'s' if diff.minutes > 1 else ''} ago"
            else:
                last_updated_time = "just now"

        enriched_contents.append({
            'name': item['name'],
            'path': item['path'],
            'type': item['type'],
            'latest_commit': latest_commit_message,
            'last_updated': last_updated_time
        })

    parent_path = "/".join(path.strip("/").split("/")[:-1]) if path else ""
    user_info = session.get('user_info', {})
    return render_template(
        'Github_contents.html',
        repo_name=repo_name,
        contents=enriched_contents,
        owner=owner,
        path=path,
        parent_path=parent_path,
        repo_private=repo_private,
        query=query,
        branches=branches,
        **user_info
    )


@app.route('/download_repo/<owner>/<repo_name>/<branch>')
def download_repo(owner, repo_name, branch):
    if 'github_token' not in session:
        return redirect(url_for('login'))
    
    token = session['github_token']['access_token']
    headers = {'Authorization': f'token {token}'}
    
    api_url = f'https://api.github.com/repos/{owner}/{repo_name}/zipball/{branch}'
    response = requests.get(api_url, headers=headers, allow_redirects=False)
    
    if response.status_code == 302:
        return redirect(response.headers['Location'])
    else:
        flash('Failed to generate download link', 'danger')
        return redirect(url_for('show_contents', 
                            owner=owner, 
                            repo_name=repo_name, 
                            path=request.args.get('path', ''), 
                            branch=branch))




@app.route('/add-repo', methods=['POST'])
def create_and_upload():
    try:
        if 'github_token' not in session:
            return jsonify({'error': 'Authentication required'}), 401

        token = session['github_token']['access_token']
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        repo_name = request.form['repoName']
        repo_description = request.form['repoDescription']
        repo_visibility = request.form['repoVisibility']
        commit_message = request.form['commitMessage']
        github_username = session['github_user']

        print(f"Received data - Repo: {repo_name}, Description: {repo_description}, Visibility: {repo_visibility}, Commit Message: {commit_message}")
        
        # 1. Create GitHub Repository
        repo_data = {
            "name": repo_name,
            "description": repo_description,
            "private": repo_visibility == 'private',
            "auto_init": False  # Do not initialize with a README file
        }
        
        repo_res = requests.post(
            'https://api.github.com/user/repos',
            json=repo_data,
            headers=headers
        )
        
        if repo_res.status_code != 201:
            return jsonify({'error': f'Repo creation failed: {repo_res.json().get("message", "Unknown error")}' }), 400

        # 2. Upload Files
        uploaded_files = request.files.getlist('repoFolder[]')
        
        for file in uploaded_files:
            if not file.filename:
                continue

            filename = secure_filename(file.filename)
            file_path = os.path.join(*filename.split('\\'))

            file_content = file.read()
            encoded_content = base64.b64encode(file_content).decode('utf-8')

            upload_url = f'https://api.github.com/repos/{github_username}/{repo_name}/contents/{file_path}'
            payload = {
                "message": commit_message,
                "content": encoded_content,
                "branch": "main"
            }

            upload_res = requests.put(upload_url, headers=headers, json=payload)
            
            if upload_res.status_code not in [200, 201]:
                return jsonify({'error': f'Failed to upload {file_path}: {upload_res.json().get("message", "Unknown error")}' }), 400

        return jsonify({
            'success': True,
            'url': f'https://github.com/{github_username}/{repo_name}'
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500



# Git commit and push function
def git_commit_and_push():
    try:
        # Ensure the current directory is a Git repository
        if not os.path.isdir('.git'):
            raise Exception("This is not a valid Git repository.")

        # Stage all changes
        subprocess.run(['git', 'add', '.'], check=True)

        # Commit the changes
        subprocess.run(['git', 'commit', '-m', 'Updated file content via Flask'], check=True)

        # Push changes to the remote repository
        subprocess.run(['git', 'push'], check=True)

        print("Git commit and push successful.")

    except subprocess.CalledProcessError as e:
        print(f"Error during Git operation: {e}")
        raise Exception("Git operation failed.")
    except Exception as e:
        print(f"Error: {e}")
        raise Exception(f"Error: {e}")




@app.route('/add-webhook', methods=['POST'])
def add_webhook():
    if 'github_token' not in session:
        return jsonify({'error': 'Authentication required'}), 401

    token = session['github_token']['access_token']
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    data = request.get_json()
    logging.debug(f"Incoming data: {data}")

    repo_owner = data.get('repo_owner')
    repo_name = data.get('repo_name')

    if not repo_owner or not repo_name:
        return jsonify({'error': 'Repository owner and name are required'}), 400

    # ✅ Check for existing webhook with same URL
    get_hooks_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/hooks"
    existing_hooks_res = requests.get(get_hooks_url, headers=headers)
    
    if existing_hooks_res.status_code == 200:
        existing_hooks = existing_hooks_res.json()
        for hook in existing_hooks:
            if hook['config'].get('url') == data.get("url"):
                return jsonify({'error': 'Webhook with this URL already exists'}), 400
    else:
        logging.warning("Could not fetch existing webhooks")

    # Determine events
    if data.get('event') == 'select':
        events = data.get('selected_events', [])
        if not events:
            return jsonify({'error': 'Please select at least one event'}), 400
    elif data.get('event') == 'all':
        events = ['*']
    else:
        events = ['push']

    payload = {
        "name": "web",
        "active": data.get("active", True),
        "events": events,
        "config": {
            "url": data.get("url"),
            "content_type": data.get("content_type", "json"),
            "secret": data.get("secret", ""),
            "insecure_ssl": "0" if data.get("ssl") == "enable" else "1"
        }
    }

    logging.debug(f"Prepared payload: {payload}")
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/hooks"
    res = requests.post(api_url, headers=headers, json=payload)

    if res.status_code == 201:
        return jsonify({'success': True, 'webhook': res.json()})
    else:
        logging.debug(f"GitHub error: {res.status_code} - {res.text}")
        return jsonify({'error': 'Failed to create webhook', 'details': res.json()}), res.status_code

@app.route('/webhooks/<owner>/<repo>')
def show_webhooks(owner, repo):
    return render_template('contentsform_.html', owner=owner, repo=repo)



@app.route('/list-webhooks/<owner>/<repo>')
def list_webhooks(owner, repo):
    if 'github_token' not in session:
        return jsonify({'error': 'Authentication required'}), 401

    token = session['github_token']['access_token']
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    api_url = f'https://api.github.com/repos/{owner}/{repo}/hooks'
    webhooks = []
    while api_url:
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            hooks = response.json()
            webhooks.extend(hooks)

            # Check if pagination exists and get the next page URL
            api_url = response.links.get('next', {}).get('url')
        else:
            return jsonify({'error': 'Failed to fetch webhooks', 'details': response.json()}), 400

    return jsonify({'success': True, 'hooks': webhooks})


# DELETE route to handle repo deletion
@app.route('/delete-repo', methods=['DELETE'])
def delete_repo():
    print(f"[DEBUG] Session data: {dict(session)}")

    if 'github_token' not in session or 'user_info' not in session:
        return jsonify({
            "success": False,
            "message": "Authentication required",
            "login_url": url_for('login')
        }), 401

    username = session.get('user_info', {}).get('username')  # FIXED this line
    if not username:
        return jsonify({
            "success": False,
            "message": "User information incomplete. Please re-login."
        }), 401

    data = request.get_json()
    if not data or 'repo_name' not in data:
        return jsonify({
            "success": False,
            "message": "Repository name required"
        }), 400

    repo_name = data['repo_name']

    print(f"[DEBUG] Deleting repo: {username}/{repo_name}")

    headers = {
        'Authorization': f'token {session["github_token"]["access_token"]}',  # FIXED this line too
        'Accept': 'application/vnd.github.v3+json'
    }
    api_url = f'https://api.github.com/repos/{username}/{repo_name}'

    try:
        # Step 1: Verify repository exists
        verify_res = requests.get(api_url, headers=headers)
        if verify_res.status_code == 404:
            return jsonify({
                "success": False,
                "message": f"Repository '{repo_name}' not found",
                "not_found": True
            }), 404

        # Step 2: Delete repository
        delete_res = requests.delete(api_url, headers=headers)
        
        if delete_res.status_code == 204:
            print(f"[SUCCESS] Successfully deleted {username}/{repo_name}")
            return jsonify({
                "success": True,
                "message": f"Repository '{repo_name}' deleted",
                "repo_name": repo_name
            })
        else:
            print(f"[ERROR] GitHub API error: {delete_res.status_code} {delete_res.text}")
            return jsonify({
                "success": False,
                "message": f"GitHub API error: {delete_res.status_code}",
                "details": delete_res.text
            }), 400

    except Exception as e:
        print(f"[ERROR] Exception while deleting repository: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Server error during deletion",
            "error": str(e)
        }), 500

# View a file content
@app.route('/view_file/<owner>/<repo>/<path:file_path>')
def view_file(owner, repo, file_path):
    if 'github_token' not in session:
        return redirect(url_for('login'))

    token = session['github_token']['access_token']
    headers = {'Authorization': f'token {token}'}
    api_url = f'https://api.github.com/repos/{owner}/{repo}/contents/{file_path}'
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        content = response.json()
        file_content = base64.b64decode(content['content']).decode('utf-8')
        return file_content
    else:
        abort(404)


import smtplib
from email.message import EmailMessage



socketio = SocketIO(app, cors_allowed_origins="*")

pending_updates = {}

@app.route('/update_file/<owner>/<repo>', methods=['POST'])
def update_file(owner, repo):
    if 'github_token' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    file_path = data.get('file_path')
    new_content = data.get('new_content')
    commit_message = data.get('commit_message')

    if not file_path or not new_content or not commit_message:
        return jsonify({'error': 'Missing required fields'}), 400

    update_id = str(uuid.uuid4())

    pending_updates[update_id] = {
        'owner': owner,
        'repo': repo,
        'file_path': file_path,
        'new_content': new_content,
        'commit_message': commit_message,
        'token': session['github_token']['access_token'],
        'status': 'pending',
        'update_id': update_id
    }

    approve_url = f"http://127.0.0.1:5000/approve_update/{update_id}"
    reject_url = f"http://127.0.0.1:5000/reject_update/{update_id}"
    msg = EmailMessage()
    msg['Subject'] = f'Approval Required: Update to {file_path} in {owner}/{repo}'
    msg['From'] = "eshwar.bashabathini88@gmail.com"
    msg['To'] = "dhanasekhar@middlewaretalents.com"
    msg['X-Priority'] = "1"
    msg['X-MSMail-Priority'] = "High"
    msg['Importance'] = "High"

    # Plain text fallback
    msg.set_content(f"""
    A file update requires your approval.

    Repository: {owner}/{repo}
    File: {file_path}
    Commit message: {commit_message}
    This is the content add to that file :
    new_content:{new_content}
    Approve: {approve_url}
    Reject: {reject_url}

    """)

    # HTML version with buttons
    msg.add_alternative(f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <p>Dear Team,</p>
        <p>A file update in the repository requires your review and approval:</p>

        <table style="margin-left: 20px;">
        <tr><td><strong>📁 Repository:</strong></td><td>{owner}/{repo}</td></tr>
        <tr><td><strong>📄 File:</strong></td><td>{file_path}</td></tr>
        <tr><td><strong>📝 Commit Message:</strong></td><td>{commit_message}</td></tr>
        </table>

        <p style="margin-top: 20px;">Please take action:</p>

        <a href="{approve_url}" style="
        background-color: #28a745;
        color: white;
        padding: 10px 20px;
        text-decoration: none;
        border-radius: 5px;
        font-weight: bold;
        margin-right: 10px;
        display: inline-block;"> Approve</a>

        <a href="{reject_url}" style="
        background-color: #dc3545;
        color: white;
        padding: 10px 20px;
        text-decoration: none;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;"> Reject</a>
         <table style="margin-left: 20px;">

        <tr><td><strong> Content  IN File :</strong></td><td>{new_content}</td></tr>
        </table>
        <p style="margin-top: 30px;">Thank you,<br>DevOps Approval System</p>
    </body>
    </html>
    """, subtype='html')
    try:
        print("Connecting to SMTP server...")
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        
        # Enable debug output
        smtp.set_debuglevel(1)

        print("Starting TLS...")
        smtp.starttls()
        
        print("Logging into Gmail...")
        smtp.login("eshwar.bashabathini88@gmail.com", "rqob tobv xdeq pscr")
        
        print("Sending the message...")
        response = smtp.send_message(msg)
        print("SMTP send response:", response)  # This is usually an empty dict if successful

        smtp.quit()
        print("SMTP connection closed.")

        return jsonify({'message': 'Approval email sent', 'update_id': update_id}), 200

    except Exception as e:
        print("SMTP error occurred:", str(e))
        return jsonify({'error': 'Email failed', 'details': str(e)}), 500


@app.route('/approve_update/<update_id>', methods=['GET'])
def approve_update(update_id):
    update = pending_updates.get(update_id)
    if not update:
        return "Invalid or expired approval link.", 404

    update['status'] = 'approved'
    try:
        commit_to_github(update)
        socketio.emit('commit_status', {'update_id': update_id, 'status': 'approved'})
    except Exception as e:
        return f"Error committing to GitHub: {str(e)}", 500

    del pending_updates[update_id]
    return "✅ Update approved and committed."



@app.route('/reject_update/<update_id>', methods=['GET', 'POST'])
def reject_update(update_id):
    update = pending_updates.get(update_id)
    if not update:
        return "Invalid or expired rejection link.", 404

    if request.method == 'GET':
        # Show the form to enter rejection reason
        return f"""
        <form method="post">
            <label for="reason">Reason for rejection:</label><br>
            <textarea name="reason" rows="4" cols="50" required></textarea><br><br>
            <input type="submit" value="Submit Rejection">
        </form>
        """

    elif request.method == 'POST':
        reason = request.form.get('reason')
        update['status'] = 'rejected'
        update['rejection_reason'] = reason

        # Emit the reason to frontend
        socketio.emit('commit_status', {
            'update_id': update_id,
            'status': 'rejected',
            'reason': reason
        })

        del pending_updates[update_id]
        return "❌ Update has been rejected with reason: " + reason

# @app.route('/reject_update/<update_id>', methods=['GET'])
# def reject_update(update_id):
#     update = pending_updates.get(update_id)
#     if not update:
#         return "Invalid or expired rejection link.", 404

#     update['status'] = 'rejected'
#     socketio.emit('commit_status', {'update_id': update_id, 'status': 'rejected'})
#     del pending_updates[update_id]
#     return "❌ Update has been rejected."

def commit_to_github(update):
    headers = {
        'Authorization': f'token {update["token"]}',
        'Accept': 'application/vnd.github.v3+json'
    }
    get_url = f'https://api.github.com/repos/{update["owner"]}/{update["repo"]}/contents/{update["file_path"]}'
    res = requests.get(get_url, headers=headers)
    if res.status_code != 200:
        raise Exception('Failed to fetch file details from GitHub')

    file_sha = res.json()['sha']
    content_b64 = base64.b64encode(update['new_content'].encode()).decode()
    payload = {
        "message": update["commit_message"],
        "content": content_b64,
        "sha": file_sha
    }
    commit_res = requests.put(get_url, headers=headers, json=payload)
    if commit_res.status_code not in [200, 201]:
        raise Exception('Failed to update file on GitHub')





@app.route('/logout')
def logout():
    session.pop('username', None)
    return render_template('login.html')  # Go back to login after logout

if __name__ == '__main__':
    app.run(debug=True)




































































# from flask import Flask, redirect, url_for, session, render_template, request, jsonify, abort, send_from_directory, flash
# from authlib.integrations.flask_client import OAuth
# from datetime import datetime, timezone
# from dateutil import parser
# import logging
# from dateutil.relativedelta import relativedelta
# import os
# import requests
# import base64
# import subprocess
# import shutil
# from werkzeug.utils import secure_filename

# app = Flask(__name__)
# app.secret_key = 'your_secret_key_here'

# UPLOAD_FOLDER = 'uploads'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# # GitHub OAuth Configuration
# oauth = OAuth(app)
# github = oauth.register(
#     name='github',
#     client_id="Ov23livvf9u6T8LPxmPY",
#     client_secret="04372c22e7cd454d2cb4c0a055a09b76d3c62dd3",
#     access_token_url='https://github.com/login/oauth/access_token',
#     authorize_url='https://github.com/login/oauth/authorize',
#     api_base_url='https://api.github.com/',
#     client_kwargs={'scope': 'repo'},
#     redirect_uri='http://127.0.0.1:5000/auth/github/callback'
# )


# from flask import Flask, request, jsonify, render_template
# import requests
# from requests.auth import HTTPBasicAuth
# import re
# import xml.sax.saxutils as saxutils
# from urllib.parse import quote

# app = Flask(__name__)

# # Jenkins configuration
# JENKINS_URL = "http://192.168.100.12:8080/"
# JENKINS_USERNAME = "yaswanth"
# JENKINS_API_TOKEN = "1183a581fe0a195dd792c7f88df81b74c9"

# # Enhanced Jenkins job fetcher with caching
# def fetch_jenkins_jobs():
#     url = f"{JENKINS_URL}/api/json"
#     auth = HTTPBasicAuth(JENKINS_USERNAME, JENKINS_API_TOKEN)
    
#     try:
#         response = requests.get(url, auth=auth, timeout=10)
#         if response.status_code == 200:
#             jobs_data = response.json()
#             jobs = []
            
#             for job in jobs_data.get('jobs', []):
#                 # Parallelize these requests in production
#                 build_history = get_build_history(job['name'])
#                 config = get_job_config(job['name'])
                
#                 jobs.append({
#                     'name': job['name'],
#                     'url': job['url'],
#                     'color': job.get('color', 'disabled'),
#                     'latest_build': build_history[0] if build_history else None,
#                     'build_count': len(build_history),
#                     'success_count': len([b for b in build_history if b.get('result') == 'SUCCESS']),
#                     'config': config
#                 })
            
#             # Calculate statistics
#             stats = {
#                 'total_jobs': len(jobs),
#                 'success_builds': sum(job['success_count'] for job in jobs),
#                 'failed_builds': sum(1 for job in jobs if job['latest_build'] and job['latest_build'].get('result') == 'FAILURE'),
#                 'pending_builds': sum(1 for job in jobs if job['latest_build'] and not job['latest_build'].get('result'))
#             }
            
#             return {'jobs': jobs, 'stats': stats}, None
        
#         return None, "Failed to fetch Jenkins jobs"
#     except Exception as e:
#         return None, str(e)

# def get_build_history(job_name):
#     url = f"{JENKINS_URL}/job/{quote(job_name)}/api/json?tree=builds[number,result,timestamp,duration,url]"
#     response = requests.get(url, auth=HTTPBasicAuth(JENKINS_USERNAME, JENKINS_API_TOKEN))
#     return response.json().get('builds', []) if response.status_code == 200 else []

# def get_job_config(job_name):
#     url = f"{JENKINS_URL}/job/{quote(job_name)}/config.xml"
#     response = requests.get(url, auth=HTTPBasicAuth(JENKINS_USERNAME, JENKINS_API_TOKEN))
#     return response.text if response.status_code == 200 else None

# # @app.route('/')
# # def index():
# #     return render_template('dashboard.html')

# @app.route('/api/jobs')
# def get_jobs_api():
#     jobs_data, error = fetch_jenkins_jobs()
#     if error:
#         return jsonify({'status': 'error', 'message': error}), 500
#     return jsonify({'status': 'success', **jobs_data})

# # Keep your existing routes for trigger_build, create_job, delete_job, etc.
# # [Keep all your other routes from the original code here]


# import os
# import requests
# from flask import Flask, render_template, jsonify, request
# from requests.auth import HTTPBasicAuth



# # Splunk connection settings
# SPLUNK_HOST = '127.0.0.1'
# SPLUNK_PORT = '8089'  # Splunk management port
# SPLUNK_WEB_PORT = '8000'  # Splunk web UI port
# SPLUNK_USER = 'MTL1013'
# SPLUNK_PASSWORD = 'MTL@1013'

# def splunk_session():
#     session = requests.Session()
#     session.auth = HTTPBasicAuth(SPLUNK_USER, SPLUNK_PASSWORD)
#     session.verify = False  # Only for local/dev
#     return session

# # @app.route('/')
# # def home():
# #     return render_template('splunk1.html')

# @app.route('/splunk')
# def splunk_page():
#     return render_template('splunk1.html')

# @app.route('/api/logs')
# def fetch_logs():
#     logs = get_internal_logs()
#     return jsonify(logs)


# import splunklib.client as client
# import splunklib.results as results

# def get_internal_logs():
#     service = client.connect(
#         host='127.0.0.1',
#         port=8089,
#         username='MTL1013',
#         password='MTL@1013'
#     )

#     # search_query = 'search index=_internal | sort -_time | head 10'
#     search_query = 'search index=_internal | sort -_time | head 10'

#     job = service.jobs.create(search_query, exec_mode='blocking')
#     for result in results.ResultsReader(job.results()):
#         print(result)

#     job = service.jobs.create(search_query)
#     while not job.is_done():
#         pass  # Wait for the job to finish

#     log_results = []
#     for result in results.ResultsReader(job.results()):
#         if isinstance(result, dict):
#             log_results.append({
#                 'time': result.get('_time', ''),
#                 'source': result.get('source', ''),
#                 'level': result.get('log_level', 'INFO'),
#                 'message': result.get('log_message', result.get('_raw', ''))
#             })

#     return log_results





# @app.route('/splunk_status')
# def splunk_status():
#     try:
#         # Check if Splunk web interface is accessible
#         response = requests.get(f'http://{SPLUNK_HOST}:{SPLUNK_WEB_PORT}', timeout=5)
#         response.raise_for_status()
#         return jsonify({'status': 'success', 'message': 'Splunk is running and accessible.'})
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)}), 500

# @app.route('/splunk_dashboards')
# def splunk_dashboards():
#     try:
#         session = splunk_session()
#         url = f'https://{SPLUNK_HOST}:{SPLUNK_PORT}/servicesNS/admin/search/data/ui/views?output_mode=json'
#         response = session.get(url)
#         response.raise_for_status()

#         entries = response.json().get('entry', [])
#         dashboards = [{
#             'name': entry['name'],
#             'label': entry['content'].get('label', entry['name']),
#             'description': entry['content'].get('description', '')
#         } for entry in entries]

#         return jsonify(dashboards)
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)}), 500

# @app.route('/splunk_search/<dashboard_name>')
# def splunk_search_dashboard(dashboard_name):
#     try:
#         session = splunk_session()
#         url = f'https://{SPLUNK_HOST}:{SPLUNK_PORT}/servicesNS/admin/search/data/ui/views/{dashboard_name}?output_mode=json'
#         response = session.get(url)
#         response.raise_for_status()

#         dashboard = response.json()['entry'][0]
#         return jsonify({
#             'name': dashboard['name'],
#             'label': dashboard['content'].get('label', dashboard['name']),
#             'description': dashboard['content'].get('description', ''),
#             'content': {
#                 'xml': dashboard['content'].get('eai:data', 'No definition available.')
#             }
#         })
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)}), 500

# @app.route('/splunk_indexes')
# def splunk_indexes():
#     try:
#         session = splunk_session()
#         url = f'https://{SPLUNK_HOST}:{SPLUNK_PORT}/services/data/indexes?output_mode=json'
#         response = session.get(url)
#         response.raise_for_status()

#         indexes = []
#         for entry in response.json().get('entry', []):
#             indexes.append({
#                 'name': entry['name'],
#                 'totalEventCount': entry['content'].get('totalEventCount', 'N/A'),
#                 'currentDBSizeMB': entry['content'].get('currentDBSizeMB', 'N/A'),
#                 'disabled': entry['content'].get('disabled', False)
#             })
#         return jsonify(indexes)
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)}), 500

# @app.route('/splunk_recent_logs')
# def splunk_recent_logs():
#     try:
#         index = request.args.get('index', '*')
#         count = request.args.get('count', '10')
        
#         session = splunk_session()
#         search_query = f'search index="{index}" | head {count}'
#         url = f'https://{SPLUNK_HOST}:{SPLUNK_PORT}/services/search/jobs'
        
#         # Start the search job
#         response = session.post(url, data={
#             'search': search_query,
#             'output_mode': 'json'
#         })
#         response.raise_for_status()
        
#         sid = response.json()['sid']
        
#         # Wait for results
#         results_url = f'https://{SPLUNK_HOST}:{SPLUNK_PORT}/services/search/jobs/{sid}/results'
#         params = {
#             'output_mode': 'json',
#             'count': count
#         }
        
#         import time
#         for _ in range(10):  # Try 10 times with 1 second delay
#             time.sleep(1)
#             response = session.get(results_url, params=params)
#             if response.status_code == 200:
#                 break
        
#         response.raise_for_status()
#         results = response.json().get('results', [])
#         return jsonify(results)
        
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)}), 500

# @app.route('/splunk_search')
# def splunk_search():
#     try:
#         query = request.args.get('query')
#         index = request.args.get('index', '*')
#         realtime = request.args.get('realtime', 'false').lower() == 'true'
        
#         if not query:
#             return jsonify({'status': 'error', 'message': 'Search query is required'}), 400
            
#         session = splunk_session()
#         search_query = f'search index="{index}" {query}'
#         if not realtime:
#             search_query += ' | head 100'
            
#         url = f'https://{SPLUNK_HOST}:{SPLUNK_PORT}/services/search/jobs'
        
#         # Start the search job
#         response = session.post(url, data={
#             'search': search_query,
#             'output_mode': 'json',
#             'exec_mode': 'normal' if not realtime else 'realtime'
#         })
#         response.raise_for_status()
        
#         sid = response.json()['sid']
        
#         # Get results
#         results_url = f'https://{SPLUNK_HOST}:{SPLUNK_PORT}/services/search/jobs/{sid}/results'
#         params = {
#             'output_mode': 'json',
#             'count': 0 if realtime else 100
#         }
        
#         response = session.get(results_url, params=params)
#         response.raise_for_status()
#         results = response.json().get('results', [])
        
#         return jsonify({
#             'status': 'success',
#             'results': results
#         })
        
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)}), 500

# @app.route('/splunk_apps')
# def splunk_apps():
#     try:
#         session = splunk_session()
#         url = f'https://{SPLUNK_HOST}:{SPLUNK_PORT}/services/apps/local?output_mode=json'
#         response = session.get(url)
#         response.raise_for_status()

#         apps = []
#         for entry in response.json().get('entry', []):
#             apps.append({
#                 'name': entry['name'],
#                 'version': entry['content'].get('version', 'N/A'),
#                 'author': entry['content'].get('author', 'N/A'),
#                 'disabled': entry['content'].get('disabled', False)
#             })
#         return jsonify(apps)
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)}), 500

# @app.route('/splunk_users')
# def splunk_users():
#     try:
#         session = splunk_session()
#         url = f'https://{SPLUNK_HOST}:{SPLUNK_PORT}/services/authentication/users?output_mode=json'
#         response = session.get(url)
#         response.raise_for_status()

#         users = []
#         for entry in response.json().get('entry', []):
#             users.append({
#                 'name': entry['name'],
#                 'realName': entry['content'].get('realname', 'N/A'),
#                 'email': entry['content'].get('email', 'N/A'),
#                 'roles': entry['content'].get('roles', [])
#             })
#         return jsonify(users)
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)}), 500













# @app.route('/login')
# def login():
#     redirect_uri = url_for('auth', _external=True)
#     scopes = [
#         'repo', 'delete_repo', 'user', 'notifications', 'gist', 'read:org', 'write:org',
#         'admin:org', 'read:repo_hook', 'write:repo_hook', 'admin:repo_hook', 'read:discussion',
#         'write:discussion', 'admin:discussion', 'public_repo', 'repo:status', 'repo_deployment',
#         'workflow', 'security_events'
#     ]
#     return github.authorize_redirect(redirect_uri, scope=scopes)
# @app.route('/auth/github/callback')
# def auth():
#     # Get the GitHub OAuth token after successful authorization
#     token = github.authorize_access_token()

#     # Get the user's GitHub profile
#     user_response = github.get('user')
#     user = user_response.json()  # Convert the response to JSON
    
#     # Print user details for debugging
#     print(user)
    
#     # Extract and parse 'created_at' date
#     created_at_str = user.get('created_at', '')
#     repos_response = github.get('user/repos', params={'type': 'all'})
#     repos = repos_response.json()  # Convert repos response to JSON
    
#     # Print repos for debugging
#     print(repos)

#     # Parse the 'created_at' timestamp if available
#     if created_at_str:
#         created_at = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%SZ")
#         created_at_date = created_at.date().strftime("%Y-%m-%d")
#         print(created_at_date)
#     else:
#         created_at_date = ''

#     # Store the token and user info in session
#     session['github_token'] = token
#     session['github_user'] = user['login']
    
#     # Store detailed user info in session
#     session['user_info'] = {
#         'name': user.get('name', ''),
#         'username': user.get('login', ''),
#         'email': user.get('email', ''),
#         'bio': user.get('bio', ''),
#         'avatar_url': user.get('avatar_url', ''),
#         'public_repos': user.get('public_repos', 0),
#         'followers': user.get('followers', 0),
#         'following': user.get('following', 0),
#         'html_url': user.get('html_url', ''),
#         'created_at': created_at_date
#     }

#     # Redirect the user to the home page
#     return redirect(url_for('home'))
# from flask import Flask, render_template, request, redirect, session, url_for



# # Temporary user storage (in-memory dictionary)
# users = {}

# @app.route('/')
# def main():
#     if 'username' in session:
#         return render_template("deyui.html", username=session['username'])
#     return redirect(url_for('user_login'))  # Redirect to the custom login route

# @app.route('/user_login', methods=['GET', 'POST'])  # Custom login route
# def user_login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         if username in users and users[username] == password:
#             session['username'] = username
#             return redirect(url_for('main'))
#         return 'Invalid username or password'
#     return render_template('deyui.html')

# @app.route('/register', methods=['GET', 'POST'])  # Registration page
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         if username in users:
#             return 'User already exists'
#         users[username] = password
#         return redirect(url_for('user_login'))  # Redirect to custom login after registering
#     return render_template('register.html')

# # @app.route('/logout')
# # def logout():
# #     session.pop('username', None)
# #     return redirect(url_for('user_login'))



# # @app.route('/')
# # def main():
# #     return render_template("deyui.html")
# @app.route('/dashboard')
# def home():
#     if 'github_token' in session:
#         username = session['github_user']
#         token = session['github_token']['access_token']
#         headers = {'Authorization': f'token {token}'}
       
#         repos = []
#         page = 1
#         per_page = 100  # Maximum allowed by GitHub API
        
#         while True:
#             repos_resp = requests.get(
#                 f'https://api.github.com/users/{username}/repos?per_page={per_page}&page={page}',
#                 headers=headers
#             )
#             if repos_resp.ok:
#                 repos_page = repos_resp.json()
#                 if not repos_page:
#                     break
#                 repos.extend(repos_page)
#                 page += 1
#             else:
#                 break
#         for repo in repos:
#             print(f"Repo: {repo['name']}, Private: {repo.get('private')}")

       

#         private_repos = sum(1 for repo in repos if repo.get('private', False))
#         public_repos = len(repos) - private_repos  # The rest are 
#         return render_template("dashboard.html", username=username, repos=repos,private_repos=private_repos, public_repos=public_repos)

#     return render_template("login.html")


# @app.route('/repos/<owner>/<repo_name>/contents/', defaults={'path': ''})
# @app.route('/repos/<owner>/<repo_name>/contents/<path:path>')
# def show_contents(owner, repo_name, path):
#     if 'github_token' not in session:
#         return redirect(url_for('login'))

#     token = session['github_token']['access_token']
#     headers = {'Authorization': f'token {token}'}

#     repo_info_url = f"https://api.github.com/repos/{owner}/{repo_name}"
#     repo_info = requests.get(repo_info_url, headers=headers).json()
#     repo_private = repo_info.get("private", False)

#     branches_url = f"https://api.github.com/repos/{owner}/{repo_name}/branches"
#     branches_resp = requests.get(branches_url, headers=headers)
#     branches = branches_resp.json() if branches_resp.ok else []

#     api_url = f'https://api.github.com/repos/{owner}/{repo_name}/contents/{path}'
#     response = requests.get(api_url, headers=headers)
    
#     if not response.ok:
#         return jsonify({'error': 'Failed to fetch repository contents', 'details': response.json()}), 400

#     contents = response.json()
#     query = request.args.get('q', '').lower()
#     if query:
#         contents = [item for item in contents if query in item.get('name', '').lower()]

#     enriched_contents = []
#     for item in contents:
#         latest_commit_message = None
#         last_updated_time = None

#         commits_url = f'https://api.github.com/repos/{owner}/{repo_name}/commits'
#         params = {'path': item['path'], 'per_page': 1}
#         commits_response = requests.get(commits_url, headers=headers, params=params)

#         if commits_response.status_code == 200 and commits_response.json():
#             commit_data = commits_response.json()[0]
#             latest_commit_message = commit_data['commit']['message']
#             commit_date = commit_data['commit']['committer']['date']

#             commit_datetime = parser.isoparse(commit_date)
#             now = datetime.now(timezone.utc)
#             diff = relativedelta(now, commit_datetime)

#             if diff.years > 0:
#                 last_updated_time = f"{diff.years} year{'s' if diff.years > 1 else ''} ago"
#             elif diff.months > 0:
#                 last_updated_time = f"{diff.months} month{'s' if diff.months > 1 else ''} ago"
#             elif diff.days > 0:
#                 last_updated_time = f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
#             elif diff.hours > 0:
#                 last_updated_time = f"{diff.hours} hour{'s' if diff.hours > 1 else ''} ago"
#             elif diff.minutes > 0:
#                 last_updated_time = f"{diff.minutes} minute{'s' if diff.minutes > 1 else ''} ago"
#             else:
#                 last_updated_time = "just now"

#         enriched_contents.append({
#             'name': item['name'],
#             'path': item['path'],
#             'type': item['type'],
#             'latest_commit': latest_commit_message,
#             'last_updated': last_updated_time
#         })

#     parent_path = "/".join(path.strip("/").split("/")[:-1]) if path else ""
#     user_info = session.get('user_info', {})
#     return render_template(
#         'contents_form.html',
#         repo_name=repo_name,
#         contents=enriched_contents,
#         owner=owner,
#         path=path,
#         parent_path=parent_path,
#         repo_private=repo_private,
#         query=query,
#         branches=branches,
#         **user_info
#     )


# @app.route('/download_repo/<owner>/<repo_name>/<branch>')
# def download_repo(owner, repo_name, branch):
#     if 'github_token' not in session:
#         return redirect(url_for('login'))
    
#     token = session['github_token']['access_token']
#     headers = {'Authorization': f'token {token}'}
    
#     api_url = f'https://api.github.com/repos/{owner}/{repo_name}/zipball/{branch}'
#     response = requests.get(api_url, headers=headers, allow_redirects=False)
    
#     if response.status_code == 302:
#         return redirect(response.headers['Location'])
#     else:
#         flash('Failed to generate download link', 'danger')
#         return redirect(url_for('show_contents', 
#                             owner=owner, 
#                             repo_name=repo_name, 
#                             path=request.args.get('path', ''), 
#                             branch=branch))




# @app.route('/add-repo', methods=['POST'])
# def create_and_upload():
#     try:
#         if 'github_token' not in session:
#             return jsonify({'error': 'Authentication required'}), 401

#         token = session['github_token']['access_token']
#         headers = {
#             'Authorization': f'token {token}',
#             'Accept': 'application/vnd.github.v3+json'
#         }

#         repo_name = request.form['repoName']
#         repo_description = request.form['repoDescription']
#         repo_visibility = request.form['repoVisibility']
#         commit_message = request.form['commitMessage']
#         github_username = session['github_user']

#         print(f"Received data - Repo: {repo_name}, Description: {repo_description}, Visibility: {repo_visibility}, Commit Message: {commit_message}")
        
#         # 1. Create GitHub Repository
#         repo_data = {
#             "name": repo_name,
#             "description": repo_description,
#             "private": repo_visibility == 'private',
#             "auto_init": False  # Do not initialize with a README file
#         }
        
#         repo_res = requests.post(
#             'https://api.github.com/user/repos',
#             json=repo_data,
#             headers=headers
#         )
        
#         if repo_res.status_code != 201:
#             return jsonify({'error': f'Repo creation failed: {repo_res.json().get("message", "Unknown error")}' }), 400

#         # 2. Upload Files
#         uploaded_files = request.files.getlist('repoFolder[]')
        
#         for file in uploaded_files:
#             if not file.filename:
#                 continue

#             filename = secure_filename(file.filename)
#             file_path = os.path.join(*filename.split('\\'))

#             file_content = file.read()
#             encoded_content = base64.b64encode(file_content).decode('utf-8')

#             upload_url = f'https://api.github.com/repos/{github_username}/{repo_name}/contents/{file_path}'
#             payload = {
#                 "message": commit_message,
#                 "content": encoded_content,
#                 "branch": "main"
#             }

#             upload_res = requests.put(upload_url, headers=headers, json=payload)
            
#             if upload_res.status_code not in [200, 201]:
#                 return jsonify({'error': f'Failed to upload {file_path}: {upload_res.json().get("message", "Unknown error")}' }), 400

#         return jsonify({
#             'success': True,
#             'url': f'https://github.com/{github_username}/{repo_name}'
#         })

#     except Exception as e:
#         print(f"Error: {e}")
#         return jsonify({'error': str(e)}), 500



# # Git commit and push function
# def git_commit_and_push():
#     try:
#         # Ensure the current directory is a Git repository
#         if not os.path.isdir('.git'):
#             raise Exception("This is not a valid Git repository.")

#         # Stage all changes
#         subprocess.run(['git', 'add', '.'], check=True)

#         # Commit the changes
#         subprocess.run(['git', 'commit', '-m', 'Updated file content via Flask'], check=True)

#         # Push changes to the remote repository
#         subprocess.run(['git', 'push'], check=True)

#         print("Git commit and push successful.")

#     except subprocess.CalledProcessError as e:
#         print(f"Error during Git operation: {e}")
#         raise Exception("Git operation failed.")
#     except Exception as e:
#         print(f"Error: {e}")
#         raise Exception(f"Error: {e}")




# @app.route('/add-webhook', methods=['POST'])
# def add_webhook():
#     if 'github_token' not in session:
#         return jsonify({'error': 'Authentication required'}), 401

#     token = session['github_token']['access_token']
#     headers = {
#         'Authorization': f'token {token}',
#         'Accept': 'application/vnd.github.v3+json'
#     }

#     data = request.get_json()
#     logging.debug(f"Incoming data: {data}")

#     repo_owner = data.get('repo_owner')
#     repo_name = data.get('repo_name')

#     if not repo_owner or not repo_name:
#         return jsonify({'error': 'Repository owner and name are required'}), 400

#     # ✅ Check for existing webhook with same URL
#     get_hooks_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/hooks"
#     existing_hooks_res = requests.get(get_hooks_url, headers=headers)
    
#     if existing_hooks_res.status_code == 200:
#         existing_hooks = existing_hooks_res.json()
#         for hook in existing_hooks:
#             if hook['config'].get('url') == data.get("url"):
#                 return jsonify({'error': 'Webhook with this URL already exists'}), 400
#     else:
#         logging.warning("Could not fetch existing webhooks")

#     # Determine events
#     if data.get('event') == 'select':
#         events = data.get('selected_events', [])
#         if not events:
#             return jsonify({'error': 'Please select at least one event'}), 400
#     elif data.get('event') == 'all':
#         events = ['*']
#     else:
#         events = ['push']

#     payload = {
#         "name": "web",
#         "active": data.get("active", True),
#         "events": events,
#         "config": {
#             "url": data.get("url"),
#             "content_type": data.get("content_type", "json"),
#             "secret": data.get("secret", ""),
#             "insecure_ssl": "0" if data.get("ssl") == "enable" else "1"
#         }
#     }

#     logging.debug(f"Prepared payload: {payload}")
#     api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/hooks"
#     res = requests.post(api_url, headers=headers, json=payload)

#     if res.status_code == 201:
#         return jsonify({'success': True, 'webhook': res.json()})
#     else:
#         logging.debug(f"GitHub error: {res.status_code} - {res.text}")
#         return jsonify({'error': 'Failed to create webhook', 'details': res.json()}), res.status_code

# @app.route('/webhooks/<owner>/<repo>')
# def show_webhooks(owner, repo):
#     return render_template('contentsform_.html', owner=owner, repo=repo)



# @app.route('/list-webhooks/<owner>/<repo>')
# def list_webhooks(owner, repo):
#     if 'github_token' not in session:
#         return jsonify({'error': 'Authentication required'}), 401

#     token = session['github_token']['access_token']
#     headers = {
#         'Authorization': f'token {token}',
#         'Accept': 'application/vnd.github.v3+json'
#     }

#     api_url = f'https://api.github.com/repos/{owner}/{repo}/hooks'
#     webhooks = []
#     while api_url:
#         response = requests.get(api_url, headers=headers)
        
#         if response.status_code == 200:
#             hooks = response.json()
#             webhooks.extend(hooks)

#             # Check if pagination exists and get the next page URL
#             api_url = response.links.get('next', {}).get('url')
#         else:
#             return jsonify({'error': 'Failed to fetch webhooks', 'details': response.json()}), 400

#     return jsonify({'success': True, 'hooks': webhooks})


# # DELETE route to handle repo deletion
# @app.route('/delete-repo', methods=['DELETE'])
# def delete_repo():
#     print(f"[DEBUG] Session data: {dict(session)}")

#     if 'github_token' not in session or 'user_info' not in session:
#         return jsonify({
#             "success": False,
#             "message": "Authentication required",
#             "login_url": url_for('login')
#         }), 401

#     username = session.get('user_info', {}).get('username')  # FIXED this line
#     if not username:
#         return jsonify({
#             "success": False,
#             "message": "User information incomplete. Please re-login."
#         }), 401

#     data = request.get_json()
#     if not data or 'repo_name' not in data:
#         return jsonify({
#             "success": False,
#             "message": "Repository name required"
#         }), 400

#     repo_name = data['repo_name']

#     print(f"[DEBUG] Deleting repo: {username}/{repo_name}")

#     headers = {
#         'Authorization': f'token {session["github_token"]["access_token"]}',  # FIXED this line too
#         'Accept': 'application/vnd.github.v3+json'
#     }
#     api_url = f'https://api.github.com/repos/{username}/{repo_name}'

#     try:
#         # Step 1: Verify repository exists
#         verify_res = requests.get(api_url, headers=headers)
#         if verify_res.status_code == 404:
#             return jsonify({
#                 "success": False,
#                 "message": f"Repository '{repo_name}' not found",
#                 "not_found": True
#             }), 404

#         # Step 2: Delete repository
#         delete_res = requests.delete(api_url, headers=headers)
        
#         if delete_res.status_code == 204:
#             print(f"[SUCCESS] Successfully deleted {username}/{repo_name}")
#             return jsonify({
#                 "success": True,
#                 "message": f"Repository '{repo_name}' deleted",
#                 "repo_name": repo_name
#             })
#         else:
#             print(f"[ERROR] GitHub API error: {delete_res.status_code} {delete_res.text}")
#             return jsonify({
#                 "success": False,
#                 "message": f"GitHub API error: {delete_res.status_code}",
#                 "details": delete_res.text
#             }), 400

#     except Exception as e:
#         print(f"[ERROR] Exception while deleting repository: {str(e)}")
#         return jsonify({
#             "success": False,
#             "message": "Server error during deletion",
#             "error": str(e)
#         }), 500

# # View a file content
# @app.route('/view_file/<owner>/<repo>/<path:file_path>')
# def view_file(owner, repo, file_path):
#     if 'github_token' not in session:
#         return redirect(url_for('login'))

#     token = session['github_token']['access_token']
#     headers = {'Authorization': f'token {token}'}
#     api_url = f'https://api.github.com/repos/{owner}/{repo}/contents/{file_path}'
#     response = requests.get(api_url, headers=headers)

#     if response.status_code == 200:
#         content = response.json()
#         file_content = base64.b64decode(content['content']).decode('utf-8')
#         return file_content
#     else:
#         abort(404)




# # from flask import Flask, request, session, jsonify
# # from flask_socketio import SocketIO
# # import smtplib
# # from email.message import EmailMessage
# # import uuid
# # import requests
# import base64
# # from flask import Flask, request, jsonify, session
# from flask_socketio import SocketIO
# import requests, base64, uuid


# # socketio = SocketIO(app, cors_allowed_origins="*")

# # # ServiceNow Config
# # SERVICENOW_URL = "https://dev214721.service-now.com/api/now/table/change_request"
# # SERVICENOW_USER = "jenkins_api_user"
# # SERVICENOW_PASS = "Eshwar@18"

# # pending_updates = {}

# # @app.route('/update_file/<owner>/<repo>', methods=['POST'])
# # def update_file(owner, repo):
# #     if 'github_token' not in session:
# #         return jsonify({'error': 'Unauthorized'}), 401

# #     data = request.json
# #     file_path = data.get('file_path')
# #     new_content = data.get('new_content')
# #     commit_message = data.get('commit_message')

# #     if not file_path or not new_content or not commit_message:
# #         return jsonify({'error': 'Missing required fields'}), 400

# #     update_id = str(uuid.uuid4())
# #     pending_updates[update_id] = {
# #         'owner': owner,
# #         'repo': repo,
# #         'file_path': file_path,
# #         'new_content': new_content,
# #         'commit_message': commit_message,
# #         'token': session['github_token']['access_token'],
# #         'status': 'pending'
# #     }

# #     # Create Change Request in ServiceNow
# #     change_payload = {
# #         "short_description": f"GitHub File Update: {file_path}",
# #         "description": f"""Repository: {owner}/{repo}
# # File: {file_path}
# # Commit Message: {commit_message}

# # Approve: http://localhost:5000/approve_update/{update_id}
# # Reject: http://localhost:5000/reject_update/{update_id}
# # """,
# #         "category": "Software",
# #         "assignment_group": "Incident Management",
# #         "state":"Assess"
# #     }

# #     res = requests.post(
# #         SERVICENOW_URL,
# #         auth=(SERVICENOW_USER, SERVICENOW_PASS),
# #         headers={"Content-Type": "application/json"},
# #         json=change_payload
# #     )

# #     if res.status_code not in [200, 201]:
# #         return jsonify({'error': 'ServiceNow request failed', 'details': res.text}), 500

# #     result = res.json()['result']
# #     return jsonify({
# #         'message': 'Change request submitted for approval',
# #         'update_id': update_id,
# #         'change_number': result.get('number'),
# #         'sys_id': result.get('sys_id')
# #     }), 200

# # @app.route('/approve_update/<update_id>', methods=['GET'])
# # def approve_update(update_id):
# #     update = pending_updates.get(update_id)
# #     if not update:
# #         return "Invalid or expired approval link.", 404

# #     try:
# #         commit_to_github(update)
# #         update['status'] = 'approved'
# #         socketio.emit('commit_status', {'update_id': update_id, 'status': 'approved'})
# #         del pending_updates[update_id]
# #         return "✅ Update approved and committed to GitHub."
# #     except Exception as e:
# #         return f"❌ GitHub commit failed: {str(e)}", 500

# # @app.route('/reject_update/<update_id>', methods=['GET'])
# # def reject_update(update_id):
# #     update = pending_updates.get(update_id)
# #     if not update:
# #         return "Invalid or expired rejection link.", 404

# #     # Provide a rejection message
# #     rejection_message = "The proposed changes were not approved. Please review the changes and try again."  
# #     update['status'] = 'rejected'
    
# #     # Emit rejection status along with message
# #     socketio.emit('commit_status', {'update_id': update_id, 'status': 'rejected', 'reason': rejection_message})
# #     del pending_updates[update_id]
# #     return f"❌ Update rejected. Reason: {rejection_message}"

# # def commit_to_github(update):
# #     headers = {
# #         'Authorization': f'token {update["token"]}',
# #         'Accept': 'application/vnd.github.v3+json'
# #     }
# #     get_url = f'https://api.github.com/repos/{update["owner"]}/{update["repo"]}/contents/{update["file_path"]}'
# #     res = requests.get(get_url, headers=headers)
# #     if res.status_code != 200:
# #         raise Exception('Failed to fetch file info')

# #     file_sha = res.json()['sha']
# #     content_b64 = base64.b64encode(update['new_content'].encode()).decode()
# #     payload = {
# #         "message": update["commit_message"],
# #         "content": content_b64,
# #         "sha": file_sha
# #     }

# #     commit_res = requests.put(get_url, headers=headers, json=payload)
# #     if commit_res.status_code not in [200, 201]:
# #         raise Exception('Failed to update file on GitHub')


# import smtplib
# from email.message import EmailMessage



# socketio = SocketIO(app, cors_allowed_origins="*")

# pending_updates = {}

# @app.route('/update_file/<owner>/<repo>', methods=['POST'])
# def update_file(owner, repo):
#     if 'github_token' not in session:
#         return jsonify({'error': 'Unauthorized'}), 401

#     data = request.json
#     file_path = data.get('file_path')
#     new_content = data.get('new_content')
#     commit_message = data.get('commit_message')

#     if not file_path or not new_content or not commit_message:
#         return jsonify({'error': 'Missing required fields'}), 400

#     update_id = str(uuid.uuid4())

#     pending_updates[update_id] = {
#         'owner': owner,
#         'repo': repo,
#         'file_path': file_path,
#         'new_content': new_content,
#         'commit_message': commit_message,
#         'token': session['github_token']['access_token'],
#         'status': 'pending',
#         'update_id': update_id
#     }

#     approve_url = f"http://127.0.0.1:5000/approve_update/{update_id}"
#     reject_url = f"http://127.0.0.1:5000/reject_update/{update_id}"
#     msg = EmailMessage()
#     msg['Subject'] = f'Approval Required: Update to {file_path} in {owner}/{repo}'
#     msg['From'] = "yaswanthkumarch2001@gmail.com"
#     msg['To'] = "yaswanth@middlewaretalents.com"

#     # Plain text fallback
#     msg.set_content(f"""
#     A file update requires your approval.

#     Repository: {owner}/{repo}
#     File: {file_path}
#     Commit message: {commit_message}

#     Approve: {approve_url}
#     Reject: {reject_url}
#     """)

#     # HTML version with buttons
#     msg.add_alternative(f"""
#     <html>
#     <body style="font-family: Arial, sans-serif; line-height: 1.6;">
#         <p>Dear Team,</p>
#         <p>A file update in the repository requires your review and approval:</p>

#         <table style="margin-left: 20px;">
#         <tr><td><strong>📁 Repository:</strong></td><td>{owner}/{repo}</td></tr>
#         <tr><td><strong>📄 File:</strong></td><td>{file_path}</td></tr>
#         <tr><td><strong>📝 Commit Message:</strong></td><td>{commit_message}</td></tr>
#         </table>

#         <p style="margin-top: 20px;">Please take action:</p>

#         <a href="{approve_url}" style="
#         background-color: #28a745;
#         color: white;
#         padding: 10px 20px;
#         text-decoration: none;
#         border-radius: 5px;
#         font-weight: bold;
#         margin-right: 10px;
#         display: inline-block;"> Approve</a>

#         <a href="{reject_url}" style="
#         background-color: #dc3545;
#         color: white;
#         padding: 10px 20px;
#         text-decoration: none;
#         border-radius: 5px;
#         font-weight: bold;
#         display: inline-block;"> Reject</a>

#         <p style="margin-top: 30px;">Thank you,<br>DevOps Approval System</p>
#     </body>
#     </html>
#     """, subtype='html')
#     try:
#         print("Connecting to SMTP server...")
#         smtp = smtplib.SMTP('smtp.gmail.com', 587)
        
#         # Enable debug output
#         smtp.set_debuglevel(1)

#         print("Starting TLS...")
#         smtp.starttls()
        
#         print("Logging into Gmail...")
#         smtp.login("yaswanthkumarch2001@gmail.com", "uqjc bszf djfw bsor")
        
#         print("Sending the message...")
#         response = smtp.send_message(msg)
#         print("SMTP send response:", response)  # This is usually an empty dict if successful

#         smtp.quit()
#         print("SMTP connection closed.")

#         return jsonify({'message': 'Approval email sent', 'update_id': update_id}), 200

#     except Exception as e:
#         print("SMTP error occurred:", str(e))
#         return jsonify({'error': 'Email failed', 'details': str(e)}), 500


# @app.route('/approve_update/<update_id>', methods=['GET'])
# def approve_update(update_id):
#     update = pending_updates.get(update_id)
#     if not update:
#         return "Invalid or expired approval link.", 404

#     update['status'] = 'approved'
#     try:
#         commit_to_github(update)
#         socketio.emit('commit_status', {'update_id': update_id, 'status': 'approved'})
#     except Exception as e:
#         return f"Error committing to GitHub: {str(e)}", 500

#     del pending_updates[update_id]
#     return "✅ Update approved and committed."



# @app.route('/reject_update/<update_id>', methods=['GET', 'POST'])
# def reject_update(update_id):
#     update = pending_updates.get(update_id)
#     if not update:
#         return "Invalid or expired rejection link.", 404

#     if request.method == 'GET':
#         # Show the form to enter rejection reason
#         return f"""
#         <form method="post">
#             <label for="reason">Reason for rejection:</label><br>
#             <textarea name="reason" rows="4" cols="50" required></textarea><br><br>
#             <input type="submit" value="Submit Rejection">
#         </form>
#         """

#     elif request.method == 'POST':
#         reason = request.form.get('reason')
#         update['status'] = 'rejected'
#         update['rejection_reason'] = reason

#         # Emit the reason to frontend
#         socketio.emit('commit_status', {
#             'update_id': update_id,
#             'status': 'rejected',
#             'reason': reason
#         })

#         del pending_updates[update_id]
#         return "❌ Update has been rejected with reason: " + reason

# # @app.route('/reject_update/<update_id>', methods=['GET'])
# # def reject_update(update_id):
# #     update = pending_updates.get(update_id)
# #     if not update:
# #         return "Invalid or expired rejection link.", 404

# #     update['status'] = 'rejected'
# #     socketio.emit('commit_status', {'update_id': update_id, 'status': 'rejected'})
# #     del pending_updates[update_id]
# #     return "❌ Update has been rejected."

# def commit_to_github(update):
#     headers = {
#         'Authorization': f'token {update["token"]}',
#         'Accept': 'application/vnd.github.v3+json'
#     }
#     get_url = f'https://api.github.com/repos/{update["owner"]}/{update["repo"]}/contents/{update["file_path"]}'
#     res = requests.get(get_url, headers=headers)
#     if res.status_code != 200:
#         raise Exception('Failed to fetch file details from GitHub')

#     file_sha = res.json()['sha']
#     content_b64 = base64.b64encode(update['new_content'].encode()).decode()
#     payload = {
#         "message": update["commit_message"],
#         "content": content_b64,
#         "sha": file_sha
#     }
#     commit_res = requests.put(get_url, headers=headers, json=payload)
#     if commit_res.status_code not in [200, 201]:
#         raise Exception('Failed to update file on GitHub')



# @app.route('/debug/session')
# def debug_session():
#     return jsonify(dict(session))

# # @app.route('/logout')
# # def logout():
# #     session.clear()
# #     return redirect(url_for('home'))
# @app.route('/logout')
# def logout():
#     session.pop('username', None)
#     return redirect(url_for('user_login'))

# if __name__ == '__main__':
#     app.run(debug=True) 



