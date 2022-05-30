# Contributing to Neon

## Bugs

For reporting bugs to Neon, please follow the process outlined on the
[issues wiki page](https://github.com/DDMAL/Neon/wiki/Issues).

## Branches and Naming

When developing a feature or fixing a bug or doing anything more substantial than fixing a typo, it's best to
create a *feature* or *fix* branch addressing it and create a pull request rather than committing directly to
`develop` or `master`.

Feature branches introduce new features to Neon. Fix branches fix something not working. If an issue exists
for the feature or branch, it is recommended to name the branch after the branch type followed by a forward slash
and the issue number. (e.g. if a branch is to introduce a feature described in issue number 20, the branch should
be named `feature/20`.)
If there is no issue number and for some reason it is best not to create one, replace the number with something
descriptive of what the branch is doing.

## Commits

Commit titles should be short while more should be elaborated on in the body if necessary.
Referencing an issue in a commit is not necessary, but recommended.

### Updates to Third-Party Code

In cases where the Verovio toolkit or another compiled feature **not** managed by yarn is updated,
include a reference to the commit it was compiled from in the commit body.
If the project is hosted on GitHub, the reference should be in the form of
`[user]/[repo]@[commit]` so a link can automatically be created. So a commit from the DDMAL verovio would be
`DDMAL/verovio@[commit]`.
If the project is hosted elsewhere, the short commit SHA-1 and where the repository can be found is enough.

## Pull Requests

Before opening a pull request, perform automated tests to ensure nothing has broken and manually test any fixes
or features. The pull request contents should reference the related issue, if any, and include an overview of
what was done.
Requesting a reviewer is not required, but recommended for anything that isn't straightforward.
