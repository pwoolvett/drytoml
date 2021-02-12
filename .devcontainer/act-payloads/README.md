# Act payloads

This folder contains sample payloads to run github actions locally, using [act](https://github.com/nektos/act#events)

Example:

```json
$ act \
    -W .github/workflows/deploy.yml \
    push \
    --detect-event \
    --eventpath=.devcontainer/act-payloads/push.json
```

```console
$ act \
    -W .github/workflows/deploy.yml \
    push \
    --detect-event \
    --eventpath=.devcontainer/act-payloads/push.json
```
