pipeline {
    agent {
      label 'JenkinsDockerAgent'
}
    
    stages {
      stage('Clone Repository for testing') {
       when {
          branch "test" 
        }
        steps {
            git branch: "test", credentialsId: "${env.JENKINS_USERID}", url: "${env.REPOSITORY_URL}"
        }
      }
      stage('Clone Repository for staging') {
       when {
          branch "develop" 
        }
        steps {
            git branch: "develop", credentialsId: "${env.JENKINS_USERID}", url: "${env.REPOSITORY_URL}"
        }
      }
      stage('Clone Repository for production') {
       when {
          branch "main" 
        }
        steps {
            git branch: "main", credentialsId: "${env.JENKINS_USERID}", url: "${env.REPOSITORY_URL}"
        }
      }

 stage('Deploy on AWS through Code Deploy on main branch') {
     steps {
        step([$class: 'AWSCodeDeployPublisher', applicationName: 'OM-stg-pyt-eurobet', awsAccessKey: '', awsSecretKey: '', credentials: 'awsAccessKey', deploymentGroupAppspec: false, deploymentGroupName: 'om-stg-pyt-eurobet-DG', deploymentMethod: 'deploy',deploymentConfig: 'CodeDeployDefault.OneAtATime', excludes: '', iamRoleArn: '', includes: '**', proxyHost: '', proxyPort: 0, region: 'eu-west-1', s3bucket: 'om-backoffice-web-deployment-bucket', s3prefix: 'eurobet', subdirectory: '', versionFileName: '', waitForCompletion: true])
     } 
     
    } 
}
  environment {
    HOME = '.'  
    REPOSITORY_URL = 'https://github.com/oddsandmore/hybrid-parser.git'
    JENKINS_USERID = '8552dd97-4991-43a7-b543-cb5ccb1edc20'
  }
  
}
