import json
import uuid
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom

FPS_DEFAULT = 30
WIDTH_DEFAULT = 1080
HEIGHT_DEFAULT = 1350
AUDIO_SAMPLERATE_DEFAULT = 48000
AUDIO_BIT_DEPTH_DEFAULT = 16

def file_url(p: Path) -> str:
    return "file://localhost" + p.as_posix().replace(" ", "%20")

def add_text(parent, tag, value):
    el = ET.SubElement(parent, tag)
    el.text = str(value)
    return el

def prettify(xml_root: ET.Element) -> str:
    rough = ET.tostring(xml_root, encoding="utf-8", xml_declaration=False)
    return minidom.parseString(rough).toprettyxml(indent="\t", encoding="UTF-8").decode("utf-8")

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"
if not CONFIG_PATH.exists():
    raise FileNotFoundError(f"No se encontró config.json en {CONFIG_PATH}")

config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
PROYECTO = config.get("nombre_proyecto")
if not PROYECTO:
    raise ValueError("config.json debe incluir 'nombre_proyecto'")

PROJ_DIR = ROOT / PROYECTO
IMGS_DIR = PROJ_DIR / "IMGS"
VOICE_DIR = PROJ_DIR / "VOICE"
SLIDES_PATH = PROJ_DIR / "slides.json"
if not SLIDES_PATH.exists():
    alt = ROOT / "slides.json"
    if alt.exists():
        SLIDES_PATH = alt
    else:
        raise FileNotFoundError(f"No se encontró slides.json en {PROYECTO} ni en la raíz")

slides = json.loads(SLIDES_PATH.read_text(encoding="utf-8"))

def build_sequence(project_name: str, slides: list) -> ET.Element:
    xmeml = ET.Element("xmeml", {"version": "4"})
    sequence = ET.SubElement(xmeml, "sequence", {
        "id": f"sequence-{uuid.uuid4()}",
        "TL.SQAudioVisibleBase": "0",
        "TL.SQVideoVisibleBase": "0",
        "TL.SQVisibleBaseTime": "0",
        "TL.SQAVDividerPosition": "0.5",
        "TL.SQHideShyTracks": "0",
        "TL.SQHeaderWidth": "204",
        "TL.SQDataTrackViewControlState": "0",
        "Monitor.ProgramZoomOut": "372556800000",
        "Monitor.ProgramZoomIn": "364089600000",
        "TL.SQTimePerPixel": "0.025",
        "MZ.EditLine": "364089600000",
        "MZ.Sequence.PreviewFrameSizeHeight": str(HEIGHT_DEFAULT),
        "MZ.Sequence.PreviewFrameSizeWidth": str(WIDTH_DEFAULT),
        "MZ.Sequence.AudioTimeDisplayFormat": "200",
        "MZ.Sequence.PreviewRenderingClassID": "1061109567",
        "MZ.Sequence.PreviewRenderingPresetCodec": "1919706400",
        "MZ.Sequence.PreviewRenderingPresetPath": "EncoderPresets/SequencePreview/795454d9-d3c2-429d-9474-923ab13b7018/QuickTime.epr",
        "MZ.Sequence.PreviewUseMaxRenderQuality": "false",
        "MZ.Sequence.PreviewUseMaxBitDepth": "false",
        "MZ.Sequence.EditingModeGUID": "795454d9-d3c2-429d-9474-923ab13b7018",
        "MZ.Sequence.VideoTimeDisplayFormat": "104",
        "MZ.ZeroPoint": "0",
        "explodedTracks": "true"
    })
    add_text(sequence, "uuid", str(uuid.uuid4()))
    add_text(sequence, "name", project_name)

    total_frames = sum(int(max(0, s.get("duracion_frames", 0))) for s in slides)
    add_text(sequence, "duration", int(total_frames))

    rate = ET.SubElement(sequence, "rate")
    add_text(rate, "timebase", int(FPS_DEFAULT))
    add_text(rate, "ntsc", "FALSE")

    media = ET.SubElement(sequence, "media")

    video = ET.SubElement(media, "video")
    vformat = ET.SubElement(video, "format")
    vsamps = ET.SubElement(vformat, "samplecharacteristics")
    vrate = ET.SubElement(vsamps, "rate")
    add_text(vrate, "timebase", int(FPS_DEFAULT))
    add_text(vrate, "ntsc", "FALSE")
    vcodec = ET.SubElement(vsamps, "codec")
    add_text(vcodec, "name", "Apple ProRes 422")
    appdata = ET.SubElement(vcodec, "appspecificdata")
    add_text(appdata, "appname", "Final Cut Pro")
    add_text(appdata, "appmanufacturer", "Apple Inc.")
    add_text(appdata, "appversion", "7.0")
    data = ET.SubElement(appdata, "data")
    qtcodec = ET.SubElement(data, "qtcodec")
    add_text(qtcodec, "codecname", "Apple ProRes 422")
    add_text(qtcodec, "codectypename", "Apple ProRes 422")
    add_text(qtcodec, "codectypecode", "apcn")
    add_text(qtcodec, "codecvendorcode", "appl")
    add_text(qtcodec, "spatialquality", "1024")
    add_text(qtcodec, "temporalquality", "0")
    add_text(qtcodec, "keyframerate", "0")
    add_text(qtcodec, "datarate", "0")
    add_text(vsamps, "width", int(WIDTH_DEFAULT))
    add_text(vsamps, "height", int(HEIGHT_DEFAULT))
    add_text(vsamps, "anamorphic", "FALSE")
    add_text(vsamps, "pixelaspectratio", "square")
    add_text(vsamps, "fielddominance", "none")
    add_text(vsamps, "colordepth", "24")

    vtrack = ET.SubElement(video, "track", {
        "TL.SQTrackShy": "0",
        "TL.SQTrackExpandedHeight": "65",
        "TL.SQTrackExpanded": "0",
        "MZ.TrackTargeted": "1"
    })

    vtrack2 = ET.SubElement(video, "track", {
        "TL.SQTrackShy": "0",
        "TL.SQTrackExpandedHeight": "65",
        "TL.SQTrackExpanded": "0",
        "MZ.TrackTargeted": "0"
    })


    audio = ET.SubElement(media, "audio")
    add_text(audio, "numOutputChannels", 2)
    aformat = ET.SubElement(audio, "format")
    asamps = ET.SubElement(aformat, "samplecharacteristics")
    add_text(asamps, "depth", int(AUDIO_BIT_DEPTH_DEFAULT))
    add_text(asamps, "samplerate", int(AUDIO_SAMPLERATE_DEFAULT))

    outputs = ET.SubElement(audio, "outputs")
    g1 = ET.SubElement(outputs, "group"); add_text(g1, "index", 1); add_text(g1, "numchannels", 1); add_text(g1, "downmix", 0)
    ch1 = ET.SubElement(g1, "channel"); add_text(ch1, "index", 1)
    g2 = ET.SubElement(outputs, "group"); add_text(g2, "index", 2); add_text(g2, "numchannels", 1); add_text(g2, "downmix", 0)
    ch2 = ET.SubElement(g2, "channel"); add_text(ch2, "index", 2)

    atrack = ET.SubElement(audio, "track", {
        "TL.SQTrackAudioKeyframeStyle": "0",
        "TL.SQTrackShy": "0",
        "TL.SQTrackExpandedHeight": "41",
        "TL.SQTrackExpanded": "0",
        "MZ.TrackTargeted": "1",
        "PannerCurrentValue": "0.5",
        "PannerStartKeyframe": "-91445760000000000,0.5,0,0,0,0,0,0",
        "PannerName": "Balance",
        "currentExplodedTrackIndex": "0",
        "totalExplodedTrackCount": "1",
        "premiereTrackType": "Stereo"
    })

    current_start_frames = 0
    for idx, slide in enumerate(slides, start=1):
        img_name = slide.get("nombre_imagen")
        frames = int(slide.get("duracion_frames", 0))
        voice_name = slide.get("nombre_audio") or None

        if not img_name or frames <= 0:
            raise ValueError(f"Slide {idx} sin nombre_imagen o duracion_frames inválida.")

        img_path = (IMGS_DIR / img_name).resolve()
        a_path = (VOICE_DIR / voice_name).resolve() if voice_name else None

        vclip = ET.SubElement(vtrack, "clipitem", {"id": f"vclip-{idx}"})
        add_text(vclip, "masterclipid", f"masterclip-v-{idx}")
        add_text(vclip, "name", img_path.name)
        add_text(vclip, "enabled", "TRUE")
        add_text(vclip, "duration", frames)
        vr = ET.SubElement(vclip, "rate"); add_text(vr, "timebase", int(FPS_DEFAULT)); add_text(vr, "ntsc", "FALSE")
        add_text(vclip, "start", current_start_frames)
        add_text(vclip, "end", current_start_frames + frames)
        add_text(vclip, "in", 0)
        add_text(vclip, "out", frames)
        add_text(vclip, "alphatype", "none")
        add_text(vclip, "pixelaspectratio", "square")
        add_text(vclip, "anamorphic", "FALSE")

        filt = ET.SubElement(vclip, "filter")
        eff = ET.SubElement(filt, "effect")
        add_text(eff, "name", "Basic Motion")
        add_text(eff, "effectid", "basic")
        add_text(eff, "effectcategory", "motion")
        add_text(eff, "effecttype", "motion")
        add_text(eff, "mediatype", "video")
        add_text(eff, "pproBypass", "false")

        p_scale = ET.SubElement(eff, "parameter", {"authoringApp": "PremierePro"})
        add_text(p_scale, "parameterid", "scale")
        add_text(p_scale, "name", "Scale")
        add_text(p_scale, "valuemin", 0)
        add_text(p_scale, "valuemax", 1000)
        add_text(p_scale, "value", 133)

        p_rot = ET.SubElement(eff, "parameter", {"authoringApp": "PremierePro"})
        add_text(p_rot, "parameterid", "rotation")
        add_text(p_rot, "name", "Rotation")
        add_text(p_rot, "valuemin", -8640)
        add_text(p_rot, "valuemax", 8640)
        add_text(p_rot, "value", 0)

        p_center = ET.SubElement(eff, "parameter", {"authoringApp": "PremierePro"})
        add_text(p_center, "parameterid", "center")
        add_text(p_center, "name", "Center")
 
        val = ET.SubElement(p_center, "value")
        add_text(val, "horiz", -0.0279018)
        add_text(val, "vert", 0)

        kf1 = ET.SubElement(p_center, "keyframe")
        add_text(kf1, "when", 0)
        v1 = ET.SubElement(kf1, "value")
        add_text(v1, "horiz", -0.0223214)
        add_text(v1, "vert", 0)

        kf2 = ET.SubElement(p_center, "keyframe")
        add_text(kf2, "when", frames - 1)
        v2 = ET.SubElement(kf2, "value")
        add_text(v2, "horiz", 0.0502232)
        add_text(v2, "vert", 0)

        p_anchor = ET.SubElement(eff, "parameter", {"authoringApp": "PremierePro"})
        add_text(p_anchor, "parameterid", "centerOffset")
        add_text(p_anchor, "name", "Anchor Point")
        val_anchor = ET.SubElement(p_anchor, "value")
        add_text(val_anchor, "horiz", 0)
        add_text(val_anchor, "vert", 0)

        p_af = ET.SubElement(eff, "parameter", {"authoringApp": "PremierePro"})
        add_text(p_af, "parameterid", "antiflicker")
        add_text(p_af, "name", "Anti-flicker Filter")
        add_text(p_af, "valuemin", 0.0)
        add_text(p_af, "valuemax", 1.0)
        add_text(p_af, "value", 0)

        vfile = ET.SubElement(vclip, "file", {"id": f"vfile-{idx}"})
        add_text(vfile, "name", img_path.name)
        add_text(vfile, "pathurl", file_url(img_path))
        vfr = ET.SubElement(vfile, "rate"); add_text(vfr, "timebase", int(FPS_DEFAULT)); add_text(vfr, "ntsc", "TRUE")
        vtc = ET.SubElement(vfile, "timecode")
        vtr = ET.SubElement(vtc, "rate"); add_text(vtr, "timebase", int(FPS_DEFAULT)); add_text(vtr, "ntsc", "TRUE")
        add_text(vtc, "string", "00;00;00;00")
        add_text(vtc, "frame", 0)
        add_text(vtc, "displayformat", "DF")
        vmedia = ET.SubElement(vfile, "media")
        vvid = ET.SubElement(vmedia, "video")
        vs = ET.SubElement(vvid, "samplecharacteristics")
        vr2 = ET.SubElement(vs, "rate"); add_text(vr2, "timebase", int(FPS_DEFAULT)); add_text(vr2, "ntsc", "TRUE")
        add_text(vs, "width", int(WIDTH_DEFAULT))
        add_text(vs, "height", int(HEIGHT_DEFAULT))
        add_text(vs, "anamorphic", "FALSE")
        add_text(vs, "pixelaspectratio", "square")
        add_text(vs, "fielddominance", "none")


        sub_path = (PROJ_DIR / "SUBS" / f"sub_{idx:04d}.png").resolve()
        if sub_path.exists():
            sclip = ET.SubElement(vtrack2, "clipitem", {"id": f"sclip-{idx}"})
            add_text(sclip, "masterclipid", f"masterclip-s-{idx}")
            add_text(sclip, "name", sub_path.name)
            add_text(sclip, "enabled", "TRUE")
            add_text(sclip, "duration", frames)
            sr = ET.SubElement(sclip, "rate"); add_text(sr, "timebase", int(FPS_DEFAULT)); add_text(sr, "ntsc", "FALSE")
            add_text(sclip, "start", current_start_frames)
            add_text(sclip, "end", current_start_frames + frames)
            add_text(sclip, "in", 0)
            add_text(sclip, "out", frames)
            add_text(sclip, "alphatype", "none")
            add_text(sclip, "pixelaspectratio", "square")
            add_text(sclip, "anamorphic", "FALSE")

            sfile = ET.SubElement(sclip, "file", {"id": f"sfile-{idx}"})
            add_text(sfile, "name", sub_path.name)
            add_text(sfile, "pathurl", file_url(sub_path))
            sfr = ET.SubElement(sfile, "rate"); add_text(sfr, "timebase", int(FPS_DEFAULT)); add_text(sfr, "ntsc", "TRUE")
            stc = ET.SubElement(sfile, "timecode")
            strt = ET.SubElement(stc, "rate"); add_text(strt, "timebase", int(FPS_DEFAULT)); add_text(strt, "ntsc", "TRUE")
            add_text(stc, "string", "00;00;00;00")
            add_text(stc, "frame", 0)
            add_text(stc, "displayformat", "DF")
            smedia = ET.SubElement(sfile, "media")
            svid = ET.SubElement(smedia, "video")
            ssamp = ET.SubElement(svid, "samplecharacteristics")
            sr2 = ET.SubElement(ssamp, "rate"); add_text(sr2, "timebase", int(FPS_DEFAULT)); add_text(sr2, "ntsc", "TRUE")
            add_text(ssamp, "width", int(WIDTH_DEFAULT))
            add_text(ssamp, "height", int(HEIGHT_DEFAULT))
            add_text(ssamp, "anamorphic", "FALSE")
            add_text(ssamp, "pixelaspectratio", "square")
            add_text(ssamp, "fielddominance", "none")

        if a_path and a_path.exists():
            aclip = ET.SubElement(atrack, "clipitem", {"id": f"aclip-{idx}", "premiereChannelType": "stereo"})
            add_text(aclip, "masterclipid", f"masterclip-a-{idx}")
            add_text(aclip, "name", a_path.name)
            add_text(aclip, "enabled", "TRUE")
            add_text(aclip, "duration", frames)
            ar = ET.SubElement(aclip, "rate"); add_text(ar, "timebase", int(FPS_DEFAULT)); add_text(ar, "ntsc", "FALSE")
            add_text(aclip, "start", current_start_frames)
            add_text(aclip, "end", current_start_frames + frames)
            add_text(aclip, "in", 0)
            add_text(aclip, "out", frames)

            afile = ET.SubElement(aclip, "file", {"id": f"afile-{idx}"})
            add_text(afile, "name", a_path.name)
            add_text(afile, "pathurl", file_url(a_path))
            afr = ET.SubElement(afile, "rate"); add_text(afr, "timebase", int(FPS_DEFAULT)); add_text(afr, "ntsc", "FALSE")
            add_text(afile, "duration", max(1, frames - 1))
            atc = ET.SubElement(afile, "timecode")
            atrate = ET.SubElement(atc, "rate"); add_text(atrate, "timebase", int(FPS_DEFAULT)); add_text(atrate, "ntsc", "FALSE")
            add_text(atc, "string", "00:00:00:00")
            add_text(atc, "frame", 0)
            add_text(atc, "displayformat", "NDF")
            amedia = ET.SubElement(afile, "media")
            aaudio = ET.SubElement(amedia, "audio")
            asamp = ET.SubElement(aaudio, "samplecharacteristics")
            add_text(asamp, "depth", int(AUDIO_BIT_DEPTH_DEFAULT))
            add_text(asamp, "samplerate", int(AUDIO_SAMPLERATE_DEFAULT))
            add_text(aaudio, "channelcount", 2)

            source = ET.SubElement(aclip, "sourcetrack")
            add_text(source, "mediatype", "audio")
            add_text(source, "trackindex", 1)

            add_text(atrack, "enabled", "TRUE")
            add_text(atrack, "locked", "FALSE")
            add_text(atrack, "outputchannelindex", 1)

        current_start_frames += frames

    timecode = ET.SubElement(sequence, "timecode")
    tr = ET.SubElement(timecode, "rate"); add_text(tr, "timebase", int(FPS_DEFAULT)); add_text(tr, "ntsc", "FALSE")
    add_text(timecode, "string", "00:00:00:00")
    add_text(timecode, "frame", 0)
    add_text(timecode, "displayformat", "NDF")

    labels = ET.SubElement(sequence, "labels"); add_text(labels, "label2", "Forest")
    logginginfo = ET.SubElement(sequence, "logginginfo")
    for tag in ("description","scene","shottake","lognote","good","originalvideofilename","originalaudiofilename"):
        add_text(logginginfo, tag, "")

    return xmeml

def main():
    xmeml = build_sequence(PROYECTO, slides)
    xml_body = prettify(xmeml)
    header = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n'
    final_xml = header + xml_body

    out_path = PROJ_DIR / f"{PROYECTO}.xml"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(final_xml, encoding="utf-8")
    print(f"✅ XML generado en: {out_path}")

if __name__ == "__main__":
    main()
