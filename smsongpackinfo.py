#!/usr/bin/env python
import os
import re
import sys

class SMSong(object):
    path = None

    title = None
    subtitle = None
    artist = None
    genre = None
    origin = None
    credit = None
    songfile = None
    bpms = None
    version = None

    def __init__(self, songfile_path=None):
        super(SMSong, self).__init__()
        if (songfile_path != None):
            self.path = songfile_path
            self.parse_songfile(songfile_path)

    def __str__(self):
        return "<{} {} title={}, artist={}>".format(
            self.__class__.__name__,
            hex(id(self)),
            self.title,
            self.artist
        )

    @classmethod
    def csv_header(self, delim=','):
        return delim.join([
            "title",
            "subtitle",
            "artist",
            "genre",
            "songfile"
        ])

    def parse_songfile(self, path):
        field_re = re.compile(r"#(?P<property>.+):(?P<value>.*);")
        songfile = open(path, "r")
        charbuf = ""

        while True:
            char = songfile.read(1)
            if (not char):
                break

            if (char not in ['\r', '\n']):
                charbuf += char

            if (char == ';'):
                match = field_re.search(charbuf)
                if (match):
                    prop = match.group("property")
                    value = match.group("value")
                    self._store_property(prop, value)

                charbuf = ""

        songfile.close()
        return True

    def csv(self, delim=','):
        values = [
            self.title,
            self.subtitle,
            self.artist,
            self.genre,
            self.songfile
        ]
        return delim.join([v if v else "" for v in values])

    def _store_property(self, prop, value):
        prop_to_attr = {
            "TITLE" : "title",
            "SUBTITLE" : "subtitle",
            "ARTIST" : "artist",
            "GENRE" : "genre",
            "ORIGIN" : "origin",
            "CREDIT" : "credit",
            "MUSIC" : "songfile",
            "BPMS" : "bpms",
            "VERSION" : "version"
        }
        prop_key = prop.upper()
        if (prop_key in prop_to_attr):
            attr = prop_to_attr[prop_key]
            if (attr == "version"):
                value = float(value)
            elif (attr == "songfile"):
                value = os.path.join(self.path, value)
            elif (attr == "bpms"):
                bpms = []
                bpm_pairs = value.split(",")
                for bpm_pair in bpm_pairs:
                    bpm_strs = bpm_pair.split("=")
                    bpms += [float(bpm_str) for bpm_str in bpm_strs]

                value = bpms

            setattr(self, attr, value)

        return True

def generate_csv(songs):
    csvstr = SMSong.csv_header() + '\n'
    for song in songs:
        csvstr += song.csv() + '\n'
    return csvstr

def main(argv):
    if (len(argv) > 1):
        path = argv[1]

        songs = []
        songfile_exts = [".sm", ".ssc", ".dwi"]
        parsed_songfiles = []
        for root, subdirs, files in os.walk(path):
            songfiles = [f for f in files if os.path.splitext(f)[1] in songfile_exts]
            for songfile in songfiles:
                songfile_name = os.path.splitext(songfile)[0]
                if (songfile_name not in parsed_songfiles):
                    songfile_path = os.path.join(root, songfile)
                    song = SMSong(songfile_path)
                    songs.append(song)
                    parsed_songfiles.append(songfile_name)

        csv = generate_csv(songs)
        print >> sys.stdout, csv
    else:
        print("Usage: {} <path_to_songpack>".format(os.path.basename(argv[0])))

if (__name__ == "__main__"):
    sys.exit(main(sys.argv))
