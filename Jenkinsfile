elifePipeline {
    def commit
    stage 'Checkout', {
        checkout scm
        commit = elifeGitRevision()
    }

    elifeOnNode(
        {
            stage 'Build images', {
                checkout scm
                sh "IMAGE_TAG=${commit} docker-compose build"
            }

            stage 'Project tests', {
                // TODO: this could have better error handling
                sh "docker rm profiles_ci_project_tests || true"
                sh "IMAGE_TAG=${commit} docker-compose -f docker-compose.ci.yml run --name profiles_ci_project_tests ci ./project_tests.sh"
                try {
                    sh "IMAGE_TAG=${commit} docker-compose -f docker-compose.ci.yml up -d"
                    sh "IMAGE_TAG=${commit} docker-compose -f docker-compose.ci.yml exec -T wsgi ./smoke_tests_wsgi.sh profiles--dev"
                } finally {
                    // TODO: failure of the first step may prevent the second from running
                    sh "docker cp profiles_ci_project_tests:/srv/profiles/build ."
                    step([$class: "JUnitResultArchiver", testResults: 'build/*.xml'])

                    sh "IMAGE_TAG=${commit} docker-compose -f docker-compose.ci.yml down"
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
        }
    }
}

