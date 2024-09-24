import gradio as gr
import whisper
import subprocess
from moviepy.editor import *
import os
import tempfile

# 載入Whisper模型
model = whisper.load_model("large")

def generate_srt(audio_file):
    # 使用Whisper生成字幕
    result = model.transcribe(audio_file)
    
    # 將結果轉換為SRT格式
    srt = ""
    for i, segment in enumerate(result["segments"]):
        start = segment["start"]
        end = segment["end"]
        text = segment["text"]
        srt += f"{i+1}\n{start:.2f} --> {end:.2f}\n{text}\n\n"
    
    return srt

def create_video(audio_file, background_image, srt_content):
    # 使用MoviePy創建影片
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
        return "請上傳SRT文件"
    
    with open(file.name, 'r', encoding='utf-8') as f:
        content = f.read()
    return content

def generate_video_with_subs(image_file, audio_file, srt_content, output_file="output.mp4"):
    # 創建臨時 SRT 文件
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.srt', delete=False, encoding='utf-8') as temp_srt:
        temp_srt.write(srt_content)
        temp_srt_path = temp_srt.name

    # 構建新的 FFmpeg 命令
    ffmpeg_command = (
        f'ffmpeg -loop 1 -i "{image_file}" -i "{audio_file}" '
        f'-vf "subtitles={temp_srt_path}" '
        f'-c:v libx264 -c:a aac -b:a 192k -shortest "{output_file}"'
    )

    # 執行 FFmpeg 命令
    os.system(ffmpeg_command)

    # 刪除臨時 SRT 文件
    os.unlink(temp_srt_path)

    return output_file

# Gradio介面
with gr.Blocks() as demo:
    gr.Markdown("## 音頻轉寫為SRT字幕並生成視頻")
    
    with gr.Row():
        upload_mp3_btn = gr.Audio(label="上傳MP3", type="filepath")
        upload_bg_btn = gr.Image(label="上傳背景圖", type="filepath")
        upload_srt_btn = gr.File(label="上傳SRT", file_types=[".srt"])

    generate_srt_btn = gr.Button("生成SRT")
    srt_output = gr.TextArea(label="SRT字幕", lines=10)

    generate_video_btn = gr.Button("生成視頻")
    video_output = gr.Video(label="生成的視頻")

    # 事件處理
    upload_srt_btn.change(upload_srt, inputs=upload_srt_btn, outputs=srt_output)
    
    generate_video_btn.click(
        generate_video_with_subs,
        inputs=[upload_bg_btn, upload_mp3_btn, srt_output],
        outputs=video_output
    )

    # 其他原有的事件處理...

if __name__ == "__main__":
    demo.launch()
