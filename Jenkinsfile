pipeline {
    agent any

    environment {
        IMAGE_NAME = "aceest-gym-app"
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
    }

    stages {

        stage('Source Checkout') {
            steps {
                echo "Fetching latest source from GitHub..."
                checkout scm
                sh 'git log --oneline -3'
            }
        }

        stage('Snapshot Previous Build') {
            steps {
                echo "Preserving current image as fallback for rollback..."
                sh '''
                    if docker image inspect ${IMAGE_NAME}:latest > /dev/null 2>&1; then
                        docker tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:previous
                        echo "Snapshot saved: ${IMAGE_NAME}:previous"
                    else
                        echo "No existing image — first run, nothing to snapshot"
                    fi
                '''
            }
        }

        stage('Syntax Check') {
            steps {
                echo "Validating Python syntax..."
                sh 'python3 -m py_compile app.py && echo "app.py syntax OK"'
            }
        }

        stage('Docker Build') {
            steps {
                echo "Assembling Docker image..."
                sh 'docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .'
            }
        }

        stage('Containerised Tests') {
            steps {
                echo "Executing pytest inside container..."
                sh '''
                    docker run --rm ${IMAGE_NAME}:${IMAGE_TAG} \
                        pytest tests/ -v --tb=short
                '''
            }
        }

        stage('Promote to Latest') {
            steps {
                sh 'docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest'
                echo "Build ${IMAGE_TAG} promoted to ${IMAGE_NAME}:latest"
            }
        }
    }

    post {
        success {
            echo "PIPELINE PASSED — ${IMAGE_NAME}:${IMAGE_TAG} is live"
        }
        failure {
            echo "PIPELINE FAILED — initiating rollback"
            sh '''
                if docker image inspect ${IMAGE_NAME}:previous > /dev/null 2>&1; then
                    docker tag ${IMAGE_NAME}:previous ${IMAGE_NAME}:latest
                    echo "ROLLBACK DONE — ${IMAGE_NAME}:previous restored as latest"
                else
                    echo "No snapshot available — cannot rollback"
                fi
                docker rmi ${IMAGE_NAME}:${IMAGE_TAG} || true
            '''
        }
        always {
            cleanWs()
        }
    }
}
