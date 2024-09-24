import gradio as gr
import whisper
import subprocess
from moviepy.editor import *

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
    
    # 添加字幕
    # 這裡需要進一步處理SRT內容,將其轉換為MoviePy可用的格式
    
    final_video = CompositeVideoClip([video])
    final_video = final_video.set_audio(audio)
    
    output_file = "output.mp4"
    # 指定fps為24（或其他適合的值）
    final_video.write_videofile(output_file, fps=24)
    
    return output_file

# Gradio介面
with gr.Blocks() as demo:
    gr.Markdown("MP3 to Video Converter")
    
    with gr.Row():
        audio_input = gr.Audio(type="filepath", label="上傳MP3")
        background_image = gr.Image(type="filepath", label="上傳背景圖")
    
    generate_srt_btn = gr.Button("生成SRT")
    srt_output = gr.Textbox(label="SRT內容", lines=10)
    
    create_video_btn = gr.Button("產生影片")
    video_output = gr.Video(label="輸出影片")
    
    generate_srt_btn.click(generate_srt, inputs=audio_input, outputs=srt_output)
    create_video_btn.click(create_video, inputs=[audio_input, background_image, srt_output], outputs=video_output)

demo.launch()
