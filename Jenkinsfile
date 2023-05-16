pipeline {
    agent any
    parameters {
  choice choices: ['Oddsmarket', 'Unibet', 'Bet365'], description: 'Choose parser to deploy', name: 'Parsers'
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
