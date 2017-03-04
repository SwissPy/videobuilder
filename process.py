import sys
import subprocess


CONFIG = {
    1: {
        "audio": "Audio/1-tom-ron-pythons-guide-to-the-galaxy.flac",
        "video": "Video/block1.mp4",
        "video_offset": {
            "start": 12.0 * 60 + 40.7,
            "end": 35.0 * 60 + 54.2,
        },
        "audio_offset": 0.5,
        "intro": "Images/1-tom-ron.png",
        "outro": "Images/outro.png",
        "output": "Video/1-tom-ron-pythons-guide-to-the-galaxy.mp4",
    },
    2: {
        "audio": "Audio/2-dave-halter-api-design-is-hard-shorter.flac",
        "video": "Video/block1.mp4",
        "video_offset": {
            "start": 39.0 * 60 + 39.5,
            "end": 85.0 * 60 + 40.0,
        },
        "audio_offset": 0.33,
        "intro": "Images/2-dave-halter.png",
        "outro": "Images/outro.png",
        "output": "Video/2-dave-halter-api-design-is-hard.mp4",
    },
    3: {
        "audio": "Audio/3-armin-rigo-cffi.flac",
        "video": "Video/block2.mp4",
        "video_offset": {
            "start": 13.9855,
            "end": 37.0 * 60 + 30.85,
        },
        "audio_offset": 0.08,
        "intro": "Images/3-armin-rigo.png",
        "outro": "Images/outro.png",
        "output": "Video/3-armin-rigo-cffi.mp4",
    },
    4: {
        "audio": "Audio/4-martin-3d-graphics-shortened.flac",
        "video": "Video/block2.mp4",
        "video_offset": {
            "start": 38.0 * 60 + 34.0,
            "end": 3600.0 + 15.0 * 60 + 19.0,
        },
        "audio_offset": 0.5,
        "intro": "Images/4-martin-christen.png",
        "outro": "Images/outro.png",
        "output": "Video/4-martin-christen-3d-graphics.mp4",
    },
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
    },
    7: {
        "audio": "Audio/7-michael-scrapy.flac",
        "video": "Video/block4.mp4",
        "video_offset": {
            "start": 0.0 * 60 + 24.0,
            "end": 31.0 * 60 + 58.0,
        },
        "audio_offset": 0.2,
        "intro": "Images/7-michael-ruuegg.png",
        "outro": "Images/outro.png",
        "output": "Video/7-michael-ruuegg-scrapy.mp4",
    },
    8: {
        "audio": "Audio/8-jacinda-ipython.flac",
        "video": "Video/block4.mp4",
        "video_offset": {
            "start": 33.0 * 60 + 40.1,
            "end": 60.0 * 60 + 47.0,
        },
        "audio_offset": 0.24,
        "intro": "Images/8-jacinda-shelly.png",
        "outro": "Images/outro.png",
        "output": "Video/8-jacinda-shelly-ipython.mp4",
    },
    9: {
        "audio": "Audio/9-florian-bruhin-pytest.flac",
        "video": "Video/block4.mp4",
        "video_offset": {
            "start": 3600.0 + 4.0 * 60 + 29.0,
            "end": 3600.0 + 25.0 * 60 + 45.0,
        },
        "audio_offset": 0.4663,
        "intro": "Images/9-florian-bruhin.png",
        "outro": "Images/outro.png",
        "output": "Video/9-florian-bruhin-pytest.mp4",
    },
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
