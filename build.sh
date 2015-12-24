#!/bin/bash

# ARGUMENTS:
# $1 dev | prod [required - configure for development or production]
# $2 skip       [optional - skip unit tests]
# $3 build      [optional - use any other string to skip]
# $4 push       [optional - use any other string to skip]

# Any subsequent(*) commands which fail will cause the shell script to exit
# immediately:
# http://www.gnu.org/software/bash/manual/bashref.html#The-Set-Builtin
set -e

# Setup virtual environment
# =============================================================================
if hash deactivate 2 > /dev/null; then
    deactivate
    source venv/bin/activate
else
    source venv/bin/activate
fi

# Run unit tests
# =============================================================================
if [[ $2 = 'skip' ]]; then
    printf '%s\n' 'Skipping Python unit tests'
else
    printf '%s\n' 'Running Python unit tests'
    nosetests --exe -v --pdb
fi

# Run Docker
# =============================================================================
# Even if Docker fails at this point, we want the script to finish. Otherwise,
# we may have a dev.conf file pointing to the production DB.
set +e

# Configure DB. Do this *after* running the unit tests, so tests don't get
# logged in production.
printf '%s\n' 'Configuring the database.'
dbconf='gen3va/app.conf'
if [[ $1 = 'dev' ]]; then
    credentials=$(head -n 1 gen3va/dev.conf)
    debug=$(tail -n +2 gen3va/dev.conf)
    printf '%s\n%s' $credentials $debug > $dbconf
else
    credentials=$(head -n 1 gen3va/prod.conf)
    debug=$(tail -n +2 gen3va/prod.conf)
    printf '%s\n%s' $credentials $debug > $dbconf
fi

docker-machine start default
eval "$(docker-machine env default)"
DOCKER_IMAGE='maayanlab/gen3va:latest'
if [[ $3 = 'build' ]]; then
    echo 'building container'
    docker build -t $DOCKER_IMAGE .
fi

# Critical step! We need to reset the DB credentials so we can keep developing
# locally.
reset_credentials=$(head -n 1 gen3va/dev.conf)
reset_debug=$(tail -n +2 gen3va/dev.conf)
printf 'Reseting credentials\n'
printf '%s\n%s' $reset_credentials $reset_debug > $dbconf

# Push to private docker repo if asked
# =============================================================================
if [[ $4 = 'push' ]]; then
    printf '%s\n' 'Pushing to Docker repo'
    docker push $DOCKER_IMAGE
else
    printf '%s\n' 'Not pushing to Docker repo'
fi