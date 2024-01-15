# Development

## Release Checklist

* create a release branch called `release-v<version>` like `release-v0.1.1`
* rename every occurrence of old Docker images like `ghcr.io/medizininformatik-initiative/feasibility-monitoring:0.1.0` into the new image, say `ghcr.io/medizininformatik-initiative/feasibility-monitoring:0.1.1`
* update the CHANGELOG based on the milestone
* create a commit with the title `Release v<version>`
* create a PR from the release branch into main
* merge that PR
* create and push a tag called `v<version>` like `v0.1.1` on main at the merge commit
* create a new branch called `next-dev` on top of the release branch
* merge the `next-dev` branch back into develop
* create release notes on GitHub
