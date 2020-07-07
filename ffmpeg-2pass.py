#!/usr/bin/env python3
import functools
import sys
from argparse import ArgumentParser
from typing import List

from sh import ffmpeg

visible_ffmpeg = ffmpeg.bake(_in=sys.stdin, _out=sys.stdout, _err=sys.stderr)


def build_pass(input_file: str, output_file: str, output_format: str, h265: bool, ffmpeg_args: List[str],
               npass) -> List[str]:
    if npass == 1:
        ffmpeg_args.insert(0, '-y')
        output_file = '/dev/null'

    if h265:
        pass_params = ['-x265-params', 'pass=' + str(npass)]
    else:
        pass_params = ['-pass', str(npass)]

    return ['-i', input_file, *ffmpeg_args, *pass_params, '-f', output_format, output_file]


def safely_run_ffmpeg(*args):
    proc = visible_ffmpeg(*args, _bg=True, _bg_exc=False)
    # noinspection PyBroadException
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.kill()


def run_2pass(input_file: str, output_file: str, output_format: str, h265: bool, ffmpeg_args: List[str]):
    partial_build = functools.partial(build_pass, input_file, output_file, output_format, h265, ffmpeg_args)
    print("Running with args", *partial_build('N'))

    safely_run_ffmpeg(*partial_build(1))
    safely_run_ffmpeg(*partial_build(2))

    print("Done!")


def main():
    parser = ArgumentParser(description="A way to automatically run two-pass encoding with FFmpeg")
    parser.add_argument('-i', help='Input file for FFmpeg', dest='input_file', required=True)
    parser.add_argument('-o', help='Output file for FFmpeg', dest='output_file', required=True)
    parser.add_argument('-f', help='Output format type for FFmpeg', dest='output_format', required=True)
    parser.add_argument('--h265', help='Are you encoding h.265?', action='store_true')
    parser.add_argument("ffmpeg_args", help='General arguments for FFmpeg', nargs='*')

    args = parser.parse_args()
    run_2pass(**vars(args))


if __name__ == '__main__':
    main()
