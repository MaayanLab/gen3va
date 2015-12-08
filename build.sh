#!/bin/bash

# This script takes 1-4 arguments
# $1 'dev' or 'prod'
# $2 'skip'  [optional]
# $3 'build' [optional - use any other string to skip]
# $4 'push'  [optional - use any other string to skip]

# Any subsequent(*) commands which fail will cause the shell script to exit immediately
# http://www.gnu.org/software/bash/manual/bashref.html#The-Set-Builtin
set -e

# Run unit tests
# =============================================================================

# Setup virtual environment
# -----------------------------------------------------------------------------

if hash deactivate 2 > /dev/null; then
    deactivate
    source venv/bin/activate
else
    source venv/bin/activate
fi

if [[ $2 = 'skip' ]]; then
    printf '%s\n' 'Skipping Python unit tests'
else
    printf '%s\n' 'Running Python unit tests'
    nosetests --exe -v --pdb
fi

# Build container
# =============================================================================

# Even if Docker files at this point, we want the script to finish. Otherwise,
# we may have a dev.config file pointing to the production DB.
set +e

printf '%s\n' 'Configuring the database.'
dbconf='geneva/app.conf'
if [[ $1 = 'dev' ]]; then
    credentials=$(head -n 1 geneva/dev.conf)
    debug=$(tail -n +2 geneva/dev.conf)
    printf '%s\n%s' $credentials $debug > $dbconf
else
    credentials=$(head -n 1 geneva/prod.conf)
    debug=$(tail -n +2 geneva/prod.conf)
    printf '%s\n%s' $credentials $debug > $dbconf
fi

# Run Docker
# -----------------------------------------------------------------------------
DOCKER_IMAGE='maayanlab/geneva:latest'
if [[ $3 = 'build' ]]; then
    boot2docker init
    boot2docker up
    boot2docker shellinit
    docker build -t $DOCKER_IMAGE .
fi

# Critical step! We need to reset the DB credentials so we can keep developing locally.
reset_credentials=$(head -n 1 geneva/dev.conf)
reset_debug=$(tail -n +2 geneva/dev.conf)
printf 'Reseting credentials\n'
printf '%s\n%s' $reset_credentials $reset_debug > $dbconf

# Push to private docker repo if asked
# -----------------------------------------------------------------------------
if [[ $4 = 'push' ]]; then
    # We use an insecure, private registry. If this script errors, run the
    # following command to tell Docker to go ahead anyway.
    #
    # boot2docker ssh "echo $'EXTRA_ARGS=\"--insecure-registry 146.203.54.165:5000\"' | sudo tee -a /var/lib/boot2docker/profile && sudo /etc/init.d/docker restart"
    printf '%s\n' 'Pushing to Docker repo'
    docker push $DOCKER_IMAGE
else
    printf '%s\n' 'Not pushing to Docker repo'
fi