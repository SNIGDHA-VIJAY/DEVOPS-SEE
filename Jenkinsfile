pipeline {
  agent { docker { image 'python:3.11' } }

  options {
    timestamps()
    ansiColor('xterm')
  }

  parameters {
    // Keep schema in Jenkins so you can adjust without code changes
    string(name: 'REQUIRED_COLUMNS',
           defaultValue: 'id,name,email',
           description: 'Comma-separated required columns')
    string(name: 'CSV_GLOB',
           defaultValue: 'data/*.csv',
           description: 'Glob pattern for CSV files')
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Install deps (none needed)') {
      steps {
        sh 'python --version'
        // If you add dependencies later:
        // sh 'pip install -r requirements.txt'
      }
    }

    stage('Validate CSV schema') {
      steps {
        sh '''
          mkdir -p report
          scripts/validate_csv_schema.py \
            --csv-glob "${CSV_GLOB}" \
            --required-cols "${REQUIRED_COLUMNS}" \
            --out report/data_quality_summary.json
        '''
      }
    }

    stage('Archive report') {
      steps {
        archiveArtifacts artifacts: 'report/*.json', fingerprint: true, onlyIfSuccessful: false
      }
    }
  }

  // 5) Trigger downstream cleanup job ONLY when the build fails
  post {
    failure {
      // Optional: pass context to cleanup job
      build job: 'cleanup', wait: false, parameters: [
        string(name: 'SOURCE_JOB', value: env.JOB_NAME ?: ''),
        string(name: 'SOURCE_BUILD', value: env.BUILD_NUMBER ?: ''),
        string(name: 'REPORT_PATH', value: 'report/data_quality_summary.json')
      ]
    }
  }
}
