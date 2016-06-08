import pkg_resources
import argparse
import mido


def version_info():
    versions = []
    for pkg in ("swood", "pillow-simd", "pillow", "PIL", "pyFFTW", "mido"):
        try:
            versions.append(str(pkg_resources.get_distribution(pkg)))
        except pkg_resources.DistributionNotFound:
            pass
    return " ".join(versions)


def swoodlive_installed():
    import importlib.util
    return importlib.util.find_spec("swoodlive") is not None


def run_cmd():
    parser = argparse.ArgumentParser(description="swood.exe: the automatic ytpmv generator", add_help=False)
    #mex = parser.add_mutually_exclusive_group()

    cmd = parser#mex.add_argument_group("arguments", "Use these if you want to specify everything with arguments.")
    cmd.add_argument("in_wav", type=argparse.FileType("rb"), help="a short wav file to sample as the instrument")
    cmd.add_argument("in_midi", type=mido.MidiFile, help="the MIDI to play with the wav sample")
    cmd.add_argument("out_wav", type=argparse.FileType("wb"), help="path for the output wav file")

    cmd.add_argument("--transpose", "-t", type=int, default=0, help="amount to transpose (semitones)")
    cmd.add_argument("--speed", "-s", type=float, default=1.0, help="speed multiplier for the MIDI")
    cmd.add_argument("--cachesize", "-c", type=float, default=7.5, help="wait time for cache notes the higher the quicker the render but the more memory it uses")
    cmd.add_argument("--binsize", "-b", type=int, default=8192, help="FFT bin size; lower numbers make it faster but more off-pitch")
    cmd.add_argument("--fullclip", "-f", action="store_true", help="always use the full sample without cropping")

    #config.add_argument("--config", "--cfg", type=argparse.FileType("r"), help="the config file ")
    
    if swoodlive_installed():
        mex.add_argument("--live", help="listen on a midi input and generate the output in realtime")

    parser.add_argument("--optout", "-o", action="store_true", help="opt out of automatic bug reporting (or set the env variable SWOOD_OPTOUT)")
    parser.add_argument("--version", "-v", action="version", version=version_info(), help="get the versions of swood and its dependencies")

    args = parser.parse_args()

    from . import complain
    from . import midiparse
    from . import renderer
    from . import sample

    with complain.ComplaintFormatter():
        sample = sample.Sample(args.in_wav, args.binsize)
        midi = midiparse.MIDIParser(args.in_midi, sample, args.transpose, args.speed)
        renderer = renderer.NoteRenderer(sample, args.fullclip, args.cachesize)
        renderer.render(midi, args.out_wav)



if __name__ == "__main__":
    run_cmd()
