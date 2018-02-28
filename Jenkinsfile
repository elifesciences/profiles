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
                dockerComposeBuild(commit)
            }

            stage 'Project tests', {
                try {
                    def coverallsToken = sh(script:'cat /etc/coveralls/tokens/profiles', returnStdout: true).trim()
                    withEnv(["COVERALLS_REPO_TOKEN=$coverallsToken"]) {
                        dockerComposeProjectTests('profiles', commit)
                    }
                    sh "IMAGE_TAG=${commit} docker-compose -f docker-compose.ci.yml up -d"
                    sh "docker wait profiles_migrate_1"
                    sh "IMAGE_TAG=${commit} docker-compose -f docker-compose.ci.yml exec -T wsgi ./smoke_tests_wsgi.sh"
                } finally {
                    sh "docker cp profiles_ci_project_tests:/srv/profiles/build ."
                    step([$class: "JUnitResultArchiver", testResults: 'build/*.xml'])
                    sh "IMAGE_TAG=${commit} docker-compose -f docker-compose.ci.yml down"
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

