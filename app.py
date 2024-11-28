import streamlit as st
import whisper
import torch
import os
import time

def format_time(seconds):
    if seconds < 60:
        return f"{seconds:.2f} sec"
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    time_parts = []
    if minutes > 0:
        time_parts.append(f"{minutes} min")
    if remaining_seconds > 0:
        time_parts.append(f"{remaining_seconds} sec")
    return " ".join(time_parts)

def transcribe_audio(file_path, model_size='medium'):
    progress_bar = st.progress(0)
    status_text = st.empty()
    time_text = st.empty()
    start_time = time.time()
    try:
        status_text.text("Loading Whisper model...")
        model_start = time.time()
        model = whisper.load_model(model_size)
        model_load_time = time.time() - model_start
        
        status_text.text("Preparing audio for transcription...")
        progress_bar.progress(10)
        status_text.text("Starting transcription...")
        progress_bar.progress(20)
        
        transcribe_start = time.time()
        result = model.transcribe(file_path)
        transcribe_time = time.time() - transcribe_start
        
        progress_bar.progress(50)
        status_text.text("Generating transcription details...")
        time.sleep(0.5)
        progress_bar.progress(75)
        status_text.text("Creating SRT file...")
        
        srt_start = time.time()
        srt_filename = os.path.splitext(file_path)[0] + '.srt'
        with open(srt_filename, 'w', encoding='utf-8') as srt_file:
            for i, segment in enumerate(result['segments'], start=1):
                start = segment['start']
                end = segment['end']
                text = segment['text']
                start_str = f"{int(start//3600):02d}:{int((start%3600)//60):02d}:{start%60:06.3f}".replace('.', ',')
                end_str = f"{int(end//3600):02d}:{int((end%3600)//60):02d}:{end%60:06.3f}".replace('.', ',')
                srt_file.write(f"{i}\n")
                srt_file.write(f"{start_str} --> {end_str}\n")
                srt_file.write(f"{text.strip()}\n\n")
        srt_time = time.time() - srt_start
        progress_bar.progress(100)
        status_text.text("Transcription Complete!")
        total_time = time.time() - start_time
        time_text.markdown(f"""
        **Transcription Time Breakdown:**
        - Model Loading: {format_time(model_load_time)}
        - Transcription: {format_time(transcribe_time)}
        - SRT File Generation: {format_time(srt_time)}
        - **Total Time**: {format_time(total_time)}
        """)
        return result, srt_filename, {
            'model_load_time': model_load_time,
            'transcribe_time': transcribe_time,
            'srt_time': srt_time,
            'total_time': total_time
        }
    except Exception as e:
        progress_bar.progress(0)
        status_text.text("Transcription Failed")
        st.error(f"Transcription Error: {str(e)}")
        raise


def main():
    st.title("Whisper Audio Transcription App")
    uploaded_file = st.file_uploader("Choose an MP3 file", type=['mp3'])
    model_size = st.selectbox("Select Whisper Model Size", 
                              ['tiny', 'base', 'small', 'medium', 'large'])
    
    if "transcription_result" not in st.session_state:
        st.session_state.transcription_result = None
        st.session_state.srt_path = None
        st.session_state.audio_duration = None
    
    if uploaded_file is not None:
        # Get the original file name
        original_filename = uploaded_file.name
        
        # Save the uploaded MP3 file with the original name
        with open(original_filename, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        if st.button("Transcribe"):
            try:
                # Pass the MP3 file path and the desired SRT file name
                result, srt_path, time_metrics = transcribe_audio(original_filename, model_size)
                
                # Create SRT filename from the original MP3 file name
                srt_filename = os.path.splitext(original_filename)[0] + ".srt"
                
                st.session_state.transcription_result = result
                st.session_state.srt_path = srt_filename
                st.session_state.audio_duration = result.get('duration', 'N/A')
                
                # Save the SRT file with the dynamic name
                with open(srt_filename, 'w', encoding='utf-8') as srt_file:
                    for i, segment in enumerate(result['segments'], start=1):
                        start = segment['start']
                        end = segment['end']
                        text = segment['text']
                        
                        # Format timestamps
                        start_str = f"{int(start//3600):02d}:{int((start%3600)//60):02d}:{start%60:06.3f}".replace('.', ',')
                        end_str = f"{int(end//3600):02d}:{int((end%3600)//60):02d}:{end%60:06.3f}".replace('.', ',')
                        
                        # Write SRT entry
                        srt_file.write(f"{i}\n")
                        srt_file.write(f"{start_str} --> {end_str}\n")
                        srt_file.write(f"{text.strip()}\n\n")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    
    if st.session_state.transcription_result:
        st.success("Transcription Complete!")
        duration = st.session_state.audio_duration
        result = st.session_state.transcription_result
        srt_path = st.session_state.srt_path
        # st.write(f"**Audio Duration:** {duration} seconds")
        st.write(f"**Number of Segments:** {len(result['segments'])}")
        st.text_area("Transcribed Text", result['text'], height=200)
        
        # Use the dynamically generated SRT file name
        with open(srt_path, 'rb') as srt_file:
            st.download_button(
                label="Download SRT File",
                data=srt_file.read(),
                file_name=srt_path,
                mime='text/srt'
            )

if __name__ == "__main__":
    main()



# import streamlit as st
# import whisper
# import torch
# import os
# import time

# def format_time(seconds):
#     if seconds < 60:
#         return f"{seconds:.2f} sec"
#     minutes = int(seconds // 60)
#     remaining_seconds = int(seconds % 60)
#     time_parts = []
#     if minutes > 0:
#         time_parts.append(f"{minutes} min")
#     if remaining_seconds > 0:
#         time_parts.append(f"{remaining_seconds} sec")
#     return " ".join(time_parts)

# def transcribe_audio(file_path, model_size='medium'):
#     progress_bar = st.progress(0)
#     status_text = st.empty()
#     time_text = st.empty()
#     start_time = time.time()
#     try:
#         status_text.text("Loading Whisper model...")
#         model_start = time.time()
#         model = whisper.load_model(model_size)
#         model_load_time = time.time() - model_start
        
#         status_text.text("Preparing audio for transcription...")
#         progress_bar.progress(10)
#         status_text.text("Starting transcription...")
#         progress_bar.progress(20)
        
#         transcribe_start = time.time()
#         result = model.transcribe(file_path)
#         transcribe_time = time.time() - transcribe_start
        
#         progress_bar.progress(50)
#         status_text.text("Generating transcription details...")
#         time.sleep(0.5)
#         progress_bar.progress(75)
#         status_text.text("Creating SRT file...")
        
#         srt_start = time.time()
#         srt_filename = os.path.splitext(file_path)[0] + '.srt'
#         with open(srt_filename, 'w', encoding='utf-8') as srt_file:
#             for i, segment in enumerate(result['segments'], start=1):
#                 start = segment['start']
#                 end = segment['end']
#                 text = segment['text']
#                 start_str = f"{int(start//3600):02d}:{int((start%3600)//60):02d}:{start%60:06.3f}".replace('.', ',')
#                 end_str = f"{int(end//3600):02d}:{int((end%3600)//60):02d}:{end%60:06.3f}".replace('.', ',')
#                 srt_file.write(f"{i}\n")
#                 srt_file.write(f"{start_str} --> {end_str}\n")
#                 srt_file.write(f"{text.strip()}\n\n")
#         srt_time = time.time() - srt_start
#         progress_bar.progress(100)
#         status_text.text("Transcription Complete!")
#         total_time = time.time() - start_time
#         time_text.markdown(f"""
#         **Transcription Time Breakdown:**
#         - Model Loading: {format_time(model_load_time)}
#         - Transcription: {format_time(transcribe_time)}
#         - SRT File Generation: {format_time(srt_time)}
#         - **Total Time**: {format_time(total_time)}
#         """)
#         return result, srt_filename, {
#             'model_load_time': model_load_time,
#             'transcribe_time': transcribe_time,
#             'srt_time': srt_time,
#             'total_time': total_time
#         }
#     except Exception as e:
#         progress_bar.progress(0)
#         status_text.text("Transcription Failed")
#         st.error(f"Transcription Error: {str(e)}")
#         raise

# def main():
#     st.title("Whisper Audio Transcription App")
#     uploaded_file = st.file_uploader("Choose an MP3 file", type=['mp3'])
#     model_size = st.selectbox("Select Whisper Model Size", 
#                               ['tiny', 'base', 'small', 'medium', 'large'])
    
#     if "transcription_result" not in st.session_state:
#         st.session_state.transcription_result = None
#         st.session_state.srt_path = None
#         st.session_state.audio_duration = None
    
#     if uploaded_file is not None:
#         with open("uploaded_audio.mp3", "wb") as f:
#             f.write(uploaded_file.getbuffer())
#         if st.button("Transcribe"):
#             try:
#                 result, srt_path, time_metrics = transcribe_audio("uploaded_audio.mp3", model_size)
#                 st.session_state.transcription_result = result
#                 st.session_state.srt_path = srt_path
#                 st.session_state.audio_duration = result.get('duration', 'N/A')
#             except Exception as e:
#                 st.error(f"An error occurred: {str(e)}")
    
#     if st.session_state.transcription_result:
#         st.success("Transcription Complete!")
#         duration = st.session_state.audio_duration
#         result = st.session_state.transcription_result
#         srt_path = st.session_state.srt_path
#         # st.write(f"**Audio Duration:** {duration} seconds")
#         st.write(f"**Number of Segments:** {len(result['segments'])}")
#         st.text_area("Transcribed Text", result['text'], height=200)
#         with open(srt_path, 'rb') as srt_file:
#             st.download_button(
#                 label="Download SRT File",
#                 data=srt_file.read(),
#                 file_name=os.path.basename(srt_path),
#                 mime='text/srt'
#             )

# if __name__ == "__main__":
#     main()    