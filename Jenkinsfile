elifePipeline {
    def commit
    stage 'Checkout', {
        checkout scm
        commit = elifeGitRevision()
    }

    stage 'Project tests', {
        lock('profiles--ci') {
            builderDeployRevision 'profiles--ci', commit
            builderProjectTests 'profiles--ci', '/srv/profiles', ['/srv/profiles/build/pytest.xml']
        }
    }

    elifeMainlineOnly {
        stage 'Deploy to end2end', {
            lock('profiles--end2end') {
                builderDeployRevision 'profiles--end2end', commit
                builderSmokeTests 'profiles--end2end', '/srv/profiles'
            }
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

