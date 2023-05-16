pipeline {
    agent any
    parameters {
    gitParameter branch: '', branchFilter: '.*', defaultValue: 'dev', description: 'select branch', name: 'branch_name', quickFilterEnabled: false, selectedValue: 'NONE', sortMode: 'NONE', tagFilter: '*', type: 'GitParameterDefinition'
}

    stages {
      stage('Clone Repository for production') {
        steps {
            git branch: "main", credentialsId: "${env.JENKINS_USERID}", url: "${env.REPOSITORY_URL}"
        }
      }
       stage('Deploy on AWS through Code Deploy on main branch') {
        steps {
            sh 'docker build --build-arg Parser_Name=$PARSER_NAME -t $ECR_REGISTRY/$ECR_REPOSITORY:$CI_COMMIT_SHA -f Dockerfile .'        
     } 
     
    } 
}
  environment {
    HOME = '.'  
    REPOSITORY_URL = 'https://github.com/Pridhvi511/parsers.git'
  }
  
}
