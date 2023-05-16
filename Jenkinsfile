pipeline {
    agent {
      label 'JenkinsDockerAgent'
}
    
    stages {
      stage('Clone Repository for production') {
        steps {
            git branch: "main", credentialsId: "${env.JENKINS_USERID}", url: "${env.REPOSITORY_URL}"
        }
      }

     stage('Deploy on AWS through Code Deploy on main branch') {
     steps {
        step([$class: 'AWSCodeDeployPublisher', applicationName: 'OM-stg-pyt-eurobet', awsAccessKey: '', awsSecretKey: '', credentials: 'awsAccessKey', deploymentGroupAppspec: false, deploymentGroupName: 'om-stg-pyt-eurobet-DG', deploymentMethod: 'deploy',deploymentConfig: 'CodeDeployDefault.OneAtATime', excludes: '', iamRoleArn: '', includes: '**', proxyHost: '', proxyPort: 0, region: 'eu-west-1', s3bucket: 'om-backoffice-web-deployment-bucket', s3prefix: 'eurobet', subdirectory: '', versionFileName: '', waitForCompletion: true])
     } 
     
    } 
    stage('Deploy on AWS through Code Deploy on main branch') {
     steps {
         docker build --build-arg Parser_Name=$PARSER_NAME -t $ECR_REGISTRY/$ECR_REPOSITORY:$CI_COMMIT_SHA -f Dockerfile .        
     } 
     
    } 
}
  environment {
    HOME = '.'  
    REPOSITORY_URL = 'https://github.com/Pridhvi511/parsers.git'
  }
  
}
