elifePipeline {
    def commit
    DockerImage image
    stage 'Checkout', {
        checkout scm
        commit = elifeGitRevision()
    }

    elifeOnNode(
        {
            stage 'Build images', {
                checkout scm
                sh "IMAGE_TAG=${commit} docker-compose -f docker-compose.yml -f docker-compose.ci.yml build"
            }

            stage 'Project tests', {
                def coverallsToken = sh(script:'cat /etc/coveralls/tokens/profiles', returnStdout: true).trim()
                withEnv(["COVERALLS_REPO_TOKEN=$coverallsToken"]) {
                    dockerComposeProjectTests 'profiles', commit
                }
                try {
                    sh "IMAGE_TAG=${commit} docker-compose -f docker-compose.yml -f docker-compose.ci.yml up -d"
                    sh "IMAGE_TAG=${commit} docker-compose -f docker-compose.yml -f docker-compose.ci.yml exec -T wsgi ./smoke_tests_wsgi.sh"
                } finally {
                    sh 'docker-compose -f docker-compose.yml -f docker-compose.ci.yml down'
                }
            }

            elifeMainlineOnly {
                stage 'Push image', {
                    image = DockerImage.elifesciences(this, "profiles", commit)
                    image.push()
                }
            }
        },
        'elife-libraries--ci'
    )


    elifeMainlineOnly {
        stage 'End2end tests', {
            elifeSpectrum(
                deploy: [
                    stackname: 'profiles--end2end',
                    revision: commit,
                    folder: '/srv/profiles'
                ],
                marker: 'profiles'
            )
        }

        stage 'Deploy to continuumtest', {
            lock('profiles--continuumtest') {
                builderDeployRevision 'profiles--continuumtest', commit
                builderSmokeTests 'profiles--continuumtest', '/srv/profiles'
            }
        }

        stage 'Approval', {
            elifeGitMoveToBranch commit, 'approved'
            elifeOnNode(
                {
                    image.tag('approved').push()
                },
                'elife-libraries--ci'
            )
        }
    }
}

