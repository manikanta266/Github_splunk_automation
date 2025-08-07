pipeline {
  agent {
    label 'Azure Team'
  }
  environment {
    INDEX_NAME = 'employee_application_logs-yash-ai-logs-2025'
    REPO_NAME = '6ee'
    REPO_URL = 'https://github.com/yaswanthkumar12-cmyk/6ee'
    SPLUNK_USERNAME = 'default_user'  # Use environment variable for security
    SPLUNK_PASSWORD = 'default_password'  # Use environment variable for security
    SPLUNK_APPS_DIR = 'C:\program files\Splunk\etc\apps'
    EMAIL_RECIPIENT = 'yaswanthchennareddy25@gmail.com'
  }
  triggers {
    cron('*/2 * * * *')
  }
  stages {
    stage('Clone Repo to Splunk Apps Directory') {
      steps {
        bat """cd "${SPLUNK_APPS_DIR}"
if not exist "${REPO_NAME}" (
    git clone ${REPO_URL}
    rmdir /s /q "${SPLUNK_APPS_DIR}\${REPO_NAME}\.git"
    echo Repository cloned successfully.
) else (
    echo Repository already exists. Skipping clone.
)"""
      }
    }
    stage('Restart Splunk') {
      steps {
        bat '"C:\Program Files\Splunk\bin\splunk" restart'
      }
    }
    stage('Send Completion Email') {
      steps {
        emailext(
          subject: 'Splunk Deployment Completed Successfully',
          to: "${EMAIL_RECIPIENT}",
          mimeType: 'text/html',
          body: """<p>Hello,</p>
<p>The Splunk deployment has been completed successfully. Here are the details:</p>
<ul>
  <li>Repository: ${REPO_NAME}</li>
  <li>Splunk was restarted successfully</li>
</ul>
<p>Thanks,<br>Jenkins Automation</p>"""
        )
      }
    }
  }
  post {
    success {
      echo "Deployment completed successfully."
    }
    failure {
      echo "Deployment failed."
    }
    always {
      echo "Pipeline complete!"
    }
  }
}