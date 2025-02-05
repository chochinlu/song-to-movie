import gradio as gr
import whisper
import subprocess
from moviepy.editor import *
import os
import tempfile

model = whisper.load_model("large")

def generate_srt(audio_file):
    result = model.transcribe(audio_file)
    
    srt = ""
    for i, segment in enumerate(result["segments"]):
        start = segment["start"]
        end = segment["end"]
        text = segment["text"]
        srt += f"{i+1}\n{start:.2f} --> {end:.2f}\n{text}\n\n"
    
    return srt

def create_video(audio_file, background_image, srt_content):
    audio = AudioFileClip(audio_file)
    video = ImageClip(background_image).set_duration(audio.duration)
    
    final_video = CompositeVideoClip([video])
    final_video = final_video.set_audio(audio)
    
    output_file = "output.mp4"
    final_video.write_videofile(output_file, fps=24)
    
    output_file_with_subs = output_file.replace(".mp4", "_with_subs.mp4")
    os.system(f'ffmpeg -i "{output_file}" -vf subtitles="{srt_content}" "{output_file_with_subs}"')
    
    return output_file_with_subs

def upload_srt(file):
    if file is None:
        return "Please upload SRT file"
    
    with open(file.name, 'r', encoding='utf-8') as f:
        content = f.read()
    return content

def generate_video_with_subs(image_file, audio_file, srt_content, output_file="output.mp4"):
    # create temporary SRT file
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.srt', delete=False, encoding='utf-8') as temp_srt:
        temp_srt.write(srt_content)
        temp_srt_path = temp_srt.name

    # if output_file exists, delete it
    if os.path.exists(output_file):
        os.remove(output_file)

    ffmpeg_command = (
        f'ffmpeg -loop 1 -i "{image_file}" -i "{audio_file}" '
        f'-vf "subtitles={temp_srt_path}:force_style=\'FontSize=28\'" '
        f'-c:v libx264 -c:a aac -b:a 192k -shortest "{output_file}"'
    )

    os.system(ffmpeg_command)

    # delete temporary SRT file
    os.unlink(temp_srt_path)

    return output_file

# Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("## Mp3 Video Subtitle Generator")
    gr.Markdown("Subtitle generation can be used at https://www.subeasy.ai")
    
    with gr.Row():
        upload_mp3_btn = gr.Audio(label="Upload MP3", type="filepath")
        upload_bg_btn = gr.Image(label="Upload Background Image", type="filepath")
        upload_srt_btn = gr.File(label="Upload SRT", file_types=[".srt"])

    generate_srt_btn = gr.Button("Generate SRT")
    srt_output = gr.TextArea(label="SRT Subtitles (Editable)", lines=10)

    generate_video_btn = gr.Button("Generate Video")
    video_output = gr.Video(label="Generated Video")

    # event handling
    upload_srt_btn.change(upload_srt, inputs=upload_srt_btn, outputs=srt_output)
    
    generate_video_btn.click(
        generate_video_with_subs,
        inputs=[upload_bg_btn, upload_mp3_btn, srt_output],
        outputs=video_output
    )


if __name__ == "__main__":
    demo.launch()
