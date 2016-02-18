import sys
import subprocess


CONFIG = {
    5: {
        "audio": "Audio/5-matthieu-amiguet-python-for-live-music.flac",
        "video": "Video/block3.mp4",
        "video_offset": {
            "start": 29.45,
            "end": 46.0 * 60 + 53,
        },
        "audio_offset": 0.0,
        "intro": "Images/5-matthieu-amiguet.png",
        "outro": "Images/outro.png",
        "output": "Video/5-matthieu-amiguet-python-for-live-music.mp4",
    },
    6: {
        "audio": "Audio/6-chihway-chang-decoding-the-cosmos.flac",
        "video": "Video/block3.mp4",
        "video_offset": {
            "start": 49.0 * 60 + 11.0,
            "end": 86.0 * 60 + 50.0,
        },
        "audio_offset": 0.4504,
        "intro": "Images/6-chihway-chang.png",
        "outro": "Images/outro.png",
        "output": "Video/6-chihway-chang-decoding-the-cosmos.mp4",
    }
}


def process(item):
    audio = item['audio']
    video = item['video']
    offset = (item['video_offset']['start'], item['video_offset']['end'], item['audio_offset'])
    duration = offset[1] - offset[0]
    print('--> Using audio "%s"...' % audio)
    print('--> Using video "%s"...' % video)
    intro_duration = 3
    outro_duration = 6
    framerate = 25
    command = [
        'ffmpeg',

        # Input 0: Intro
        '-loop', '1',
        '-i', str(item['intro']),

        # Input 1: Talk
        '-itsoffset', str(intro_duration),
        '-ss', str(offset[0]),
        '-t', str(offset[1]),
        '-i', video,

        # Input 2: Outro
        '-itsoffset', str(intro_duration + duration),
        '-loop', '1',
        '-i', str(item['outro']),

        # Input 3: Audio
        '-itsoffset', str(intro_duration + offset[2]),
        '-i', audio,

        # Codecs
        '-codec:v', 'h264',
        '-codec:a', 'aac', '-strict', '-2',

        # Bitrate and framerate
        '-b:v', '8000k',
        '-b:a', '384k',
        '-r:v', str(framerate),

        # Filter
        '-filter_complex', '[0:v] fade=out:%s:%s:alpha=1 [intro];' \
                           % (framerate * intro_duration, framerate) +
                           '[2:v] fade=in:0:%s:alpha=1 [outro];' \
                           % (framerate + outro_duration) +
                           '[1:v] hqdn3d [talk];' + \
                           '[talk][intro] overlay [tmp];' + \
                           '[tmp][outro] overlay [v]',
        #'-filter_complex', 'amix=inputs=2:duration=first',

        # Input channel mapping
        '-map', '[v]',
        '-map', '3:a:0',

        # Total duration
        '-t', str(intro_duration + duration + outro_duration),

        # Output file
        item['output'],
    ]
    print('--> Running: %s' % ' '.join(command))
    subprocess.check_call(command)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: ./%s <talk-nr>' % sys.argv[0])
        print('Example for second talk: ./%s 2' % sys.argv[0])
        sys.exit(1)
    nr = int(sys.argv[1])
    if nr not in CONFIG:
        print('%s is not a valid talk number.' % nr)
        print('Choose from: %s' % list(CONFIG.keys()))
        sys.exit(1)
    print('Processing talk number %s...' % nr)
    process(CONFIG[nr])
