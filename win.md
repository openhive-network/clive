1. Extend WSL configuration by adding to /etc/wsl.configuration

```
[automount]
options = "metadata"
```

Build image (if needed):
```
./scripts/ci-helpers/build_instance.sh clive4hf $(pwd) registry.gitlab.syncad.com/hive/clive --clive-version=1.27.11.5.dev361+4ee2517ad
```

2. Prepare new one or copy an existing clive profile inside HOME directory of WSL user (it simplifies furthere usage)

3. Start cli and additionally pass --name=clive-cli to have stable container name:
```
./start_clive_cli.sh registry.gitlab.syncad.com/hive/clive/instance:clive4hf --docker-option="--name=clive-cli"
```

4. It should be possible to access the spawned clive session from separate docker exec spawns:
```
docker exec clive-cli bash /clive/scripts/clive-cmd.sh show account
```
