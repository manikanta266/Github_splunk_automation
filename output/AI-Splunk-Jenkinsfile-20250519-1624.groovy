
pipeline {
  agent {
    label 'Azure Team'
  }
  environment {
    INDEX_NAME = 'dummylogs-ai-streams'
    MONITOR_PATH = '/var/log/app/*.log'
    SOURCE_TYPE = 'json'
    REPO_NAME = 'birthday.in'
    REPO_URL = 'https://github.com/yaswanthkumarch/birthday.in'
    SPLUNK_USERNAME = 'admin'
    SPLUNK_PASSWORD = 'changeme'
    SPLUNK_APPS_DIR = 'C:\Splunk\etc\apps'
    EMAIL_RECIPIENT = 'yaswanthkumarch2001@gmail.com'
  }
  triggers {
    cron('*/1 * * * *')
  }
  stages {
    stage('AI Monitor Setup') {
      steps {
        echo "AI Assistant: Setting up intelligent monitoring"
        echo "Index: ${INDEX_NAME}"
        echo "Path: ${MONITOR_PATH}"
        echo "Type: ${SOURCE_TYPE}"
      }
    }
    stage('AI Validation') {
      steps {
        echo "Validating configuration..."
        script {
          if (env.MONITOR_PATH.contains('*')) {
            echo "Wildcard path detected"
          }
          if (env.SOURCE_TYPE == '') {
            echo "Warning: Specify a sourcetype"
          }
        }
      }
    }
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
    stage('Create Splunk Index') {
      steps {
        bat """cd "C:\Program Files\Splunk\bin"
splunk list index ${INDEX_NAME} -auth ${SPLUNK_USERNAME}:${SPLUNK_PASSWORD} > nul 2>&1
if errorlevel 1 (
    echo Index does not exist. Creating index: ${INDEX_NAME}
    splunk add index ${INDEX_NAME} -auth ${SPLUNK_USERNAME}:${SPLUNK_PASSWORD}
) else (
    echo Index '${INDEX_NAME}' already exists. Skipping creation.
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
  <li>Index: ${INDEX_NAME}</li>
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