import subprocess
import os
import sys
import argparse
import platform

def get_default_blender_path():
    """
    Determine the default Blender executable path based on the operating system.
    """
    system = platform.system()
    
    if system == "Darwin":  # macOS
        return '/Applications/Blender.app/Contents/MacOS/Blender'
    elif system == "Windows":
        # Common Windows installation paths
        possible_paths = [
            'C:\\Program Files\\Blender Foundation\\Blender\\blender.exe',
            'C:\\Program Files (x86)\\Blender Foundation\\Blender\\blender.exe'
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return 'blender'  # Fallback to PATH
    elif system == "Linux":
        # Try common Linux paths
        possible_paths = [
            '/usr/bin/blender',
            '/usr/local/bin/blender',
            '/opt/blender/blender'
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return 'blender'  # Fallback to PATH
    else:
        return 'blender'  # Generic fallback

def main():
    """
    Constructs and executes a headless Blender render command based on CLI arguments.
    """
    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description="Render a Blender scene with specified settings.")
    
    default_blender_path = get_default_blender_path()
    parser.add_argument('--blender-path', type=str, default=default_blender_path, help='Path to the Blender executable. (Default: ' + default_blender_path + ')')
    parser.add_argument('--input-script', type=str, default='scene.py', help='Path to the Blender Python script that generates the scene.')
    parser.add_argument('--output-path', type=str, default='render/movie.mkv', help='Path for the final rendered video file.')
    
    parser.add_argument('--width', type=int, default=3840, help='Render width in pixels.')
    parser.add_argument('--height', type=int, default=2160, help='Render height in pixels.')
    parser.add_argument('--fps', type=int, default=60, help='Frames per second.')
    parser.add_argument('--duration', type=int, default=60, help='Animation duration in seconds.')
    
    parser.add_argument('--container', type=str, default='MKV', help='FFmpeg container (e.g., MKV, MP4).')
    parser.add_argument('--codec', type=str, default='AV1', help='FFmpeg video codec (e.g., AV1, H264).')
    parser.add_argument('--crf', type=str, default='20', help='Constant Rate Factor for video quality (lower is better).')

    args = parser.parse_args()

    print("--- Starting CI/CD Render Pipeline with CLI Arguments ---")
    print("Detected OS: " + platform.system())
    print("Default Blender path: " + default_blender_path)
    print("Configuration: " + str(args))

    # --- Script Logic ---
    if not os.path.exists(args.input_script):
        print("Error: Input script not found at '" + args.input_script + "'")
        sys.exit(1)

    output_dir = os.path.dirname(args.output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    render_output_path_arg = os.path.join(os.getcwd(), args.output_path)
    
    # Calculate total frames
    total_frames = args.fps * args.duration
    
    # Map CRF values to Blender's enum values for different codecs
    if args.codec == 'AV1':
        # AV1 codec uses quality presets, not numeric CRF
        crf_value = 'MEDIUM'  # Options: LOSSLESS, PERC_LOSSLESS, HIGH, MEDIUM, LOW, VERYLOW, LOWEST
    else:
        # For other codecs like H264, use the numeric CRF value
        crf_value = args.crf

    # Build the command with settings from arguments
    command = [
        args.blender_path,
        "--background",
        "--python", args.input_script,
        "--render-format", "FFMPEG",
        "--render-output", render_output_path_arg,
        
        # Use python expressions to inject settings into the Blender scene
        "--python-expr", "import bpy; bpy.context.scene.render.resolution_x = " + str(args.width),
        "--python-expr", "import bpy; bpy.context.scene.render.resolution_y = " + str(args.height),
        "--python-expr", "import bpy; bpy.context.scene.render.fps = " + str(args.fps),
        "--python-expr", "import bpy; bpy.context.scene.frame_end = " + str(total_frames),
        "--python-expr", "import bpy; bpy.context.scene.render.ffmpeg.format = '" + args.container + "'",
        "--python-expr", "import bpy; bpy.context.scene.render.ffmpeg.codec = '" + args.codec + "'",
        "--python-expr", "import bpy; bpy.context.scene.render.ffmpeg.constant_rate_factor = '" + crf_value + "'",
        
        "--render-anim"
    ]

    print("\nExecuting Blender command:")
    print(" ".join(command))
    print("\n--- Blender Output ---")

    try:
        subprocess.run(command, check=True)
        print("--- End of Blender Output ---\n")
        print("SUCCESS: Render complete.")
        print("Video saved to: " + args.output_path)

    except FileNotFoundError:
        print("\n--- ERROR: Blender executable not found at '" + args.blender_path + "'. ---")
        sys.exit(1)
        
    except subprocess.CalledProcessError as e:
        print("\n--- ERROR: Blender returned a non-zero exit code. ---")
        sys.exit(1)

if __name__ == "__main__":
    main()