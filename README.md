# Container image for formatting attached block devices (works on raspberry pi)

## Features
- A perfect init container for kubernetes deployments with block persistent storage
- Accepts file system type as input parameter
- Accepts multiple devices to format as input parameter

## How to use

```
docker run -it --rm --device=/dev/sdb --device=/dev/sdc satishweb/format-disk -d /dev/sdb,/dev/sdc -t ext4
```
