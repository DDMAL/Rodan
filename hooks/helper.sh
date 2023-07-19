GetDockerTag() {
    current_branch_full=$(git symbolic-ref HEAD) # ref/heads/<branch name> or pull/#PR-id/head
    current_branch_short=$(git symbolic-ref --short HEAD) # <branch name> or ?
    _DOCKER_TAG=$1

    # Release branch will always use git tag
    if [[ $current_branch_short =~ ^release ]]; then
        # Search for tag in release branch
        tags=$(git tag --points-at HEAD) # git tags attached to theh HEAD
        _DOCKER_TAG=$(echo $tags | sed -n '1p')
        if [[ -z $_DOCKER_TAG ]]; then
            # echo "no tag on release branch, fallback to use docker tag=release"
            _DOCKER_TAG="release"
            echo $_DOCKER_TAG
            return 2
        fi
    elif [[ $_DOCKER_TAG =~ ^placeholder$ ]]; then
        # develop branch has a weird funny tag called placeholder, change it to nightly so commits and PRs will use the nightly tag
        _DOCKER_TAG="nightly"
    fi
    # Finally, use custom tags send by docker hub. e.g.: a feature branch that has its build rule on docker hub

    # Replace invalid char / in docker tag with - 
    _DOCKER_TAG=$(echo $_DOCKER_TAG | sed 's/\//-/g')
    echo $_DOCKER_TAG
    return 0
}