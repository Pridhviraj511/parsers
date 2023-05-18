pipeline
 {
    agent any
    parameters {
  choice choices: ['oddsmarket', 'pinnacle', 'feedmaker', 'feedmakernew', 'pinnacle2', 'unibet2', 'better', 'betfair', 'betradaruof', 'goldbet', 'scomesseitalia', 'vincitu', 'eurobet'], description: 'Choose parser to build', name: 'Parser_Name'
   gitParameter branch: '', branchFilter: 'origin/(.*)', defaultValue: 'main', description: 'select branch', name: 'BRANCH', type: 'PT_BRANCH', useRepository: 'https://github.com/pridhvi511/parsers.git'
    }


    stages {
      stage('Clone Repository for production') {
        steps {
            git 'https://github.com/Pridhviraj511/parsers.git'
        }
      }
       stage('Build Dockerfile') {
        steps {
            sh 'sudo docker build --build-arg Parser_Name=$PARSER_NAME -t $ECR_REGISTRY/$ECR_REPOSITORY:$TAG -f Dockerfile .'  
            } 
    } 
    stage('Push Dockerfile to ECR') {
        steps {
            sh '''aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
                aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
                aws configure set region $AWS_DEFAULT_REGION
                aws ecr get-login-password --region $AWS_DEFAULT_REGION | sudo docker login --username AWS --password-stdin "$ECR_REGISTRY/$ECR_REPOSITORY"
                sudo docker push $ECR_REGISTRY/$ECR_REPOSITORY:$TAG'''  
            } 
    } 
}
  environment {
    HOME = '.'  
    REPOSITORY_URL = 'https://github.com/Pridhvi511/parsers.git'
    ECR_REGISTRY = '610938775231.dkr.ecr.us-east-1.amazonaws.com'
    ECR_REPOSITORY = 'davs_demo'
    PARSER_NAME = 'params.Parser_Name'
    TAG = "${currentBuild.number}"
    AWS_ACCESS_KEY_ID = 'AKIAY4PWJ427ZSYIVQIL'
    AWS_SECRET_ACCESS_KEY = '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'
    AWS_DEFAULT_REGION = 'us-east-1'
  }
}
