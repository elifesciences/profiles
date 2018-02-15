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
                sh "IMAGE_TAG=${commit} docker-compose -f docker-compose.ci.yml run --name profiles_ci_project_tests ci ./project_tests.sh"
                // TODO: need to be done in a finally clause
                sh "docker cp profiles_ci_project_tests:/srv/profiles/build ."
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

