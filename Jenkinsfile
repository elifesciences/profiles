elifePipeline {
    def commit
    DockerImage image
    stage 'Checkout', {
        checkout scm
        commit = elifeGitRevision()
    }

    node('containers-jenkins-plugin') {
            stage 'Build images', {
                checkout scm
                dockerComposeBuild(commit)
            }

            stage 'Project tests', {
                def coverallsToken = sh(script:'cat /etc/coveralls/tokens/profiles', returnStdout: true).trim()
                withEnv(["COVERALLS_REPO_TOKEN=$coverallsToken"]) {
                    dockerComposeProjectTests('profiles', commit, ['/srv/profiles/build/*.xml'])
                }
                dockerComposeSmokeTests(commit, [
                    'waitFor': ['profiles_migrate_1'],
                    'scripts': [
                        'wsgi': './smoke_tests_wsgi.sh',
                    ],
                ])
            }

            elifeMainlineOnly {
                stage 'Push image', {
                    image = DockerImage.elifesciences(this, "profiles", commit)
                    image.push()
                }
            }
    }


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

