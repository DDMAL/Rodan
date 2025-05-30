# IIPImage - High Resolution Streaming Image Server
> GPLv3 Licensed

- `iipsrv` is high-performance feature-rich image server for web-based streamed viewing and zooming of ultra high-resolution images
- Source code: https://github.com/ruven/iipsrv

## Dockerfile
(Courtesy of ChatGPT) Here is a short bullet-point description of what this Dockerfile does:

### Build Stage
* **Base Image (Build Stage)**: Uses `alpine:3.18.5` for a lightweight build environment.
* **Installs Build Tools**: Adds necessary packages like `autoconf`, `automake`, `build-base`, and image libraries.
* **Downloads iipsrv Source**: Fetches the latest `iipsrv` source code from GitHub.
* **Builds iipsrv**: Configures and compiles `iipsrv` with OpenJPEG support.

### Runtime Stage / Main Image
* **Base Image (Runtime Stage)**: Uses `alpine:3.18.5` for the final runtime container.
* **Installs Runtime Dependencies**: Includes required libraries like `libpng`, `tiff`, and `openjpeg`.
* **Copies Compiled Binary**: Transfers the built `iipsrv.fcgi` binary from the build stage.
* **Sets Environment Variables**: Configures image quality, file path prefix, verbosity, and server port.
* **Exposes Port**: Opens the specified port (default: 9003) for incoming connections.
* **Entrypoint**: Launches the `iipsrv` server bound to all interfaces on the given port.
