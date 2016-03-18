#!/bin/bash

# ARGUMENTS:
# $1 skip       [optional - skip unit tests]
# $2 no-cache   [optional - use --no-cache argument when building Docker container]

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
if [[ $1 = 'skip' ]]; then
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
credentials=$(head -n 1 gen3va/prod.conf)
debug=$(tail -n +2 gen3va/prod.conf)
printf '%s\n%s' $credentials $debug > $dbconf

docker-machine start default
eval "$(docker-machine env default)"
DOCKER_IMAGE='maayanlab/gen3va:latest'
echo 'building container'
if [[ $2 = 'no-cache' ]]; then
    docker build --no-cache -t $DOCKER_IMAGE .
else
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
printf '%s\n' 'Pushing to Docker repo'
docker push $DOCKER_IMAGE
