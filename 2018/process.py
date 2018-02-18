import sys
import subprocess


CONFIG = {
    1: {
        'video': 'raw/block1.mts',
        'video_offset': {
            'start': 40.0,
            'end': 2983.0,
        },
        'intro': 'img/gael-varoquaux.png',
        'outro': 'img/outro.png',
        'output': '1-carina-haupt-keynote.mp4',
    },
    2: {
        'video': 'raw/block1.mts',
        'video_offset': {
            'start': 3067.0,
            'end': 5272.0,
        },
        'intro': 'img/gael-varoquaux.png',
        'outro': 'img/outro.png',
        'output': '2-tim-head-mybinder.mp4',
    },
    3: {
        'video': 'raw/block2.mts',
        'video_offset': {
            'start': 165.0,
            'end': 1850.0,
        },
        'intro': 'img/gael-varoquaux.png',
        'outro': 'img/outro.png',
        'output': '3-raphael-das-gupta-comprehensions.mp4',
    },
    4: {
        'video': 'raw/block2.mts',
        'video_offset': {
            'start': 1903.0,
            'end': 3801.0,
        },
        'intro': 'img/gael-varoquaux.png',
        'outro': 'img/outro.png',
        'output': '4-gabriel-krummenacher-sbb-delays.mp4',
    },
    5: {
        'video': 'raw/block2.mts',
        'video_offset': {
            'start': 3865.0,
            'end': 5610.0,
        },
        'intro': 'img/gael-varoquaux.png',
        'outro': 'img/outro.png',
        'output': '5-iacopo-spalletti-real-time-django.mp4',
    },
}


def process(item, part1=True, part2=True):
    print('--> Part a: %s, part b: %s...' % (part1, part2))
    video = item['video']
    offset = (item['video_offset']['start'], item['video_offset']['end'])
    duration = offset[1] - offset[0]
    print('--> Using video "%s"...' % video)
    output_parts = item['output'].rsplit('.', 1)
    output_tmp = '%s.tmp.%s' % (output_parts[0], output_parts[1])
    print('--> Intermediate file: "%s"' % output_tmp)
    intro_duration = 3
    outro_duration = 6
    framerate = 25
    if part1:
        command1 = [
            'ffmpeg',

            # Input 1: Talk video
            '-ss', str(offset[0] - intro_duration),
            '-t', str(offset[1] + intro_duration),
            '-i', video,

            # Input 2: Talk audio
            '-itsoffset', str(4 / 25),  # 4 frames
            '-ss', str(offset[0] - intro_duration),
            '-t', str(offset[1] + intro_duration),
            '-i', video,

            # Codecs
            '-codec:v', 'h264',
            '-codec:a', 'aac', '-strict', '-2',

            # Bitrate and framerate
            '-b:v', '8000k',
            '-b:a', '384k',
            '-r:v', str(framerate),

            # Apply hqdn3d filter (denoise) to talk
            '-filter_complex', '[0:v] hqdn3d [v]',

            # Total duration
            '-t', str(duration),

            # Output file
            '-map', '[v]',
            '-map', '1:1',
            output_tmp,
        ]
        print('--> Running: %s' % ' '.join(command1))
        subprocess.check_call(command1)

    if part2:
        command2 = [
            'ffmpeg',

            # Input 0: Intro
            '-loop', '1',
            '-i', str(item['intro']),

            # Input 1: Talk
            '-i', output_tmp,

            # Input 2: Outro
            '-itsoffset', str(intro_duration + duration - outro_duration),
            '-loop', '1',
            '-i', str(item['outro']),

            # Codecs
            '-codec:v', 'h264',
            '-codec:a', 'aac', '-strict', '-2',

            # Bitrate and framerate
            '-b:v', '8000k',
            '-b:a', '384k',
            '-r:v', str(framerate),

            # Filter
            '-filter_complex',

                # Fade out first input (intro) to alpha channel
                '[0:v] fade=t=out:st=%s:d=1:alpha=1 [intro];' \
                % intro_duration +

                # Fade in third input (outro) from alpha channel
                '[2:v] fade=in:0:%s:alpha=1 [outro];' \
                % (framerate + outro_duration) +

                # Overlay talk with intro and outro
                '[1:v][intro] overlay [tmp];' + \
                '[tmp][outro] overlay [v];' + \

                # Add fade in and fade out to audio
                '[1:a] afade=t=in:st=%s:d=%s,afade=t=out:st=%s:d=%s [a]' \
                % (intro_duration, intro_duration,
                   intro_duration + duration, outro_duration / 2),

            # Total duration
            '-t', str(intro_duration + duration),

            # Output file (video / audio)
            '-map', '[v]',
            '-map', '[a]',
            item['output'],
        ]
        print('--> Running: %s' % ' '.join(command2))
        subprocess.check_call(command2)


if __name__ == '__main__':
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print('Usage: ./%s <talk-nr> [a|b]' % sys.argv[0])
        print('Example for second talk: ./%s 2' % sys.argv[0])
        sys.exit(1)
    nr = int(sys.argv[1])
    if nr not in CONFIG:
        print('%s is not a valid talk number.' % nr)
        print('Choose from: %s' % list(CONFIG.keys()))
        sys.exit(1)
    if len(sys.argv) == 3:
        if sys.argv[2] == 'a':
            part1 = True
            part2 = False
        elif sys.argv[2] == 'b':
            part1 = False
            part2 = True
        else:
            print('%s is not a valid part specifier.' % sys.argv[2])
            print('Choose from: a, b')
            sys.exit(1)
    else:
        part1 = True
        part2 = True
    print('Processing talk number %s...' % nr)
    process(CONFIG[nr], part1, part2)
