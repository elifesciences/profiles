elifePipeline {
    def commit
    stage 'Checkout', {
        checkout scm
        commit = elifeGitRevision()
    }

    stage 'Deploy to demo', {
        lock('profiles--demo') {
            builderDeployRevision 'profiles--demo', commit
            builderSmokeTests 'profiles--end2end', '/srv/profiles'
        }
    }
}

