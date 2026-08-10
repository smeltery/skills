# Sandboxed Repository References

Use this optional protocol when an unfamiliar repository must execute and an
approved local Docker or Podman environment is available. Static inspection and
script review still happen first; a container reduces host exposure but does not
make unknown code trustworthy.

The bundled runner requires a reviewed image that already exists locally. It
mounts the repository read-only, copies it into a disposable writable mount,
drops Linux capabilities, uses a read-only container root, disables networking
by default, and deletes the working copy afterward.

```bash
./scripts/sandbox-reference.sh \
  --repo <reference-repository> \
  --image <reviewed-local-image> \
  -- <install-or-start-command>
```

Do not pass secrets into the container. Keep network mode `none` unless the
reviewed bootstrap genuinely requires access and the user approves it; then use
`--network <mode> --allow-network`. The runner does not pull images, expose
ports, grant host sockets, or persist package caches. When browser investigation
must occur inside the sandbox, use an image that already contains compatible
Playwright browsers and run the capture harness there.

If the repository needs real services, production data, privileged containers,
host networking, or credentials, stop and request a purpose-built environment
instead of weakening the sandbox ad hoc.
