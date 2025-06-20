# Blender Auto Render

An automated Blender rendering pipeline designed for CI/CD environments and Docker deployments, featuring AI-generated Blender scripts for procedural 3D content creation.

## Overview

This project provides a headless Blender rendering system that can be integrated into continuous integration/continuous deployment (CI/CD) workflows or containerized environments. The pipeline includes AI-generated Blender Python scripts that create complex 3D scenes procedurally, making it ideal for automated content generation and batch rendering.

## Features

- **Headless Rendering**: Fully automated Blender rendering without GUI requirements
- **CI/CD Ready**: Designed for integration with automated build systems
- **Docker Compatible**: Can be easily containerized for consistent deployment
- **AI-Generated Scripts**: Includes sophisticated Blender Python scripts created with AI assistance
- **Configurable Parameters**: Command-line interface for customizing render settings
- **Multiple Output Formats**: Support for various video containers and codecs (MKV, MP4, AV1, H264)
- **High-Quality Rendering**: Supports 4K resolution and high frame rates

## Components

### Core Files

- `pipeline.py` - Main orchestration script with CLI interface
- `scene.py` - AI-generated Blender script that creates a complex 3D processor grid visualization
- `main.py` - Simple entry point for the application

### Scene Generation

The included `scene.py` script generates a sophisticated 3D visualization of a "Massively Parallel Forth Processor Grid" featuring:

- 16×16×16 grid of processing cores and routers
- Animated data packets traveling through the network
- 3D cooling system visualization
- Dynamic camera movement with orbital perspective
- Advanced materials and lighting effects

## Usage

### Environment Setup

This project uses `uv` for Python environment management. Make sure you have `uv` installed:

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Before running the pipeline, synchronize the project dependencies:

```bash
uv sync
```

### Getting Help

To see all available command-line options:

```bash
uv run pipeline.py --help
```

### Basic Usage

Run the pipeline with default settings using `uv`:

```bash
uv run pipeline.py
```

Alternative direct Python execution:

```bash
python pipeline.py
```

### Custom Configuration

```bash
uv run pipeline.py \
  --width 1920 \
  --height 1080 \
  --fps 30 \
  --duration 30 \
  --codec H264 \
  --output-path render/output.mp4
```

Or with Python directly:

```bash
python pipeline.py \
  --width 1920 \
  --height 1080 \
  --fps 30 \
  --duration 30 \
  --codec H264 \
  --output-path render/output.mp4
```

### Available Parameters

- `--blender-path`: Path to Blender executable (default: `/Applications/Blender.app/Contents/MacOS/Blender` on macOS)
- `--input-script`: Blender Python script to execute (default: scene.py)
- `--output-path`: Output video file path (default: render/movie.mkv)
- `--width`: Render width in pixels (default: 3840)
- `--height`: Render height in pixels (default: 2160)
- `--fps`: Frames per second (default: 60)
- `--duration`: Animation duration in seconds (default: 60)
- `--container`: Video container format (default: MKV)
- `--codec`: Video codec (default: AV1)
- `--crf`: Constant Rate Factor for quality (default: 20)

### Platform-Specific Notes

**macOS**: The default Blender path is `/Applications/Blender.app/Contents/MacOS/Blender`  
**Linux**: Typically `/usr/bin/blender` or downloaded from Blender.org  
**Windows**: Usually `C:\Program Files\Blender Foundation\Blender\blender.exe`

## CI/CD Integration

This pipeline is designed to work seamlessly in automated environments using `uv` for dependency management:

### GitHub Actions Example

```yaml
name: Render Blender Animation
on: [push]
jobs:
  render:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      - name: Install Blender
        run: |
          wget https://download.blender.org/release/Blender4.4/blender-4.4.3-linux-x64.tar.xz
          tar -xf blender-4.4.3-linux-x64.tar.xz
      - name: Render Scene
        run: uv run pipeline.py --blender-path ./blender-4.4.3-linux-x64/blender
```

### GitLab CI Example

```yaml
# .gitlab-ci.yml
stages:
  - render

render_animation:
  stage: render
  image: ubuntu:24.04
  before_script:
    - apt-get update && apt-get install -y wget xz-utils curl python3
    - curl -LsSf https://astral.sh/uv/install.sh | sh
    - source $HOME/.cargo/env
    - wget https://download.blender.org/release/Blender4.4/blender-4.4.3-linux-x64.tar.xz
    - tar -xf blender-4.4.3-linux-x64.tar.xz
  script:
    - uv run pipeline.py --blender-path ./blender-4.4.3-linux-x64/blender
  artifacts:
    paths:
      - render/
    expire_in: 1 week
  only:
    - main
    - develop
```

### GitLab CI Example

```yaml
# .gitlab-ci.yml
stages:
  - render

render_animation:
  stage: render
  image: ubuntu:24.04
  before_script:
    - apt-get update && apt-get install -y wget xz-utils curl python3
    - curl -LsSf https://astral.sh/uv/install.sh | sh
    - source $HOME/.cargo/env
    - wget https://download.blender.org/release/Blender4.4/blender-4.4.3-linux-x64.tar.xz
    - tar -xf blender-4.4.3-linux-x64.tar.xz
  script:
    - uv run pipeline.py --blender-path ./blender-4.4.3-linux-x64/blender
  artifacts:
    paths:
      - render/
    expire_in: 1 week
  only:
    - main
    - develop
```

### Docker Integration

The pipeline can be containerized for consistent rendering across environments:

```dockerfile
FROM ubuntu:24.04
RUN apt-get update && apt-get install -y blender python3 curl
# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
COPY . /app
WORKDIR /app
CMD ["uv", "run", "pipeline.py"]
```

## Requirements

- Python 3.12+
- `uv` for Python environment management (recommended)
- Blender 4.4+ (with Python API)
- FFmpeg (for video encoding)

### Installation

1. Install `uv` if not already installed:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. The project dependencies are managed via `pyproject.toml` and `uv.lock`
3. Run commands using `uv run` to automatically manage the virtual environment

## AI-Generated Content

The Blender scripts in this project were created with AI assistance, demonstrating the potential for automated 3D content generation. The scripts showcase:

- Procedural geometry creation
- Complex material systems
- Animation scripting
- Camera rigging
- Lighting setup

This makes the pipeline particularly valuable for:
- Automated visualization generation
- Batch processing of 3D content
- Rapid prototyping of 3D scenes
- Educational content creation
- Data visualization

## Output

The pipeline generates high-quality video files suitable for:
- Technical presentations
- Educational materials
- Marketing content
- Data visualization
- Proof-of-concept demonstrations

## License

This project is designed for automated rendering workflows and can be adapted for various commercial and educational use cases.