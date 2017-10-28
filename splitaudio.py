import os
import subprocess
import argparse
import json
import sys


def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


parser = argparse.ArgumentParser(description='Split out all audio channels from input file')
parser.add_argument('input', metavar='I', type=str, help='Input file')
parser.add_argument('--output_format', type=str, help='Output format', default='mp3')
args = parser.parse_args()

if which('ffprobe') or which('ffmpeg'):
    print('FFProbe or FFmpeg could not be found in the environment')
    sys.exit(1)

if os.path.exists(args.input):
    proc = subprocess.run(
        ['ffprobe', '-i', args.input, '-print_format', 'json', '-show_streams', '-loglevel' , '-8'],
        stdout=subprocess.PIPE
    )
    streams = json.loads(proc.stdout.decode('utf-8'))

    for stream in streams['streams']:
        if stream.get('codec_type') == 'audio':
            index = stream.get('index')
            title = stream.get('tags', {}).get('title')
            title = title if title else index

            subprocess.run(
                ['ffmpeg', '-i', args.input, '-map', '0:'+str(index), title+'.'+args.output_format, '-y']
            )
