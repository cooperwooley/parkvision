# Run and Test App

## Start Services
```bash
docker-compose up --build
```
Note: use `podman-compose` if podman is your Docker engine

You may also have to remove your podman container network firewall. To do this open the conflist file: `nano ~/.config/cni/net.d/parking-system_default.conflist` and remove the entire `type: firewall` block.

### Run Tests
Run your test suite from outside the containers like this:
```bash
pytest tests/tests_routes.py
python3 tests/test_detection.py
```
