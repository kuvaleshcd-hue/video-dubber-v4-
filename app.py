import streamlit as st
import os
import tempfile
from dotenv import load_dotenv
from pipeline.auth import init_db, register_user, login_user
from pipeline.extractor import extract_audio
from pipeline.transcriber import transcribe
from pipeline.translator import translate_segments, generate_srt, LANGUAGES
from pipeline.synthesizer import synthesize_segments
from pipeline.merger import merge_audio_video

load_dotenv()
init_db()
st.set_page_config(page_title="VideoDubber AI", page_icon="🎬", layout="wide")

VOICE_LABELS = {
    # Edge-TTS voices
    "kn-IN-GaganNeural":    "Gagan - Kannada Male (Azure)",
    "kn-IN-SapnaNeural":    "Sapna - Kannada Female (Azure)",
    "hi-IN-MadhurNeural":   "Madhur - Hindi Male (Azure)",
    "hi-IN-SwaraNeural":    "Swara - Hindi Female (Azure)",
    "ta-IN-ValluvarNeural": "Valluvar - Tamil Male (Azure)",
    "ta-IN-PallaviNeural":  "Pallavi - Tamil Female (Azure)",
    "te-IN-MohanNeural":    "Mohan - Telugu Male (Azure)",
    "te-IN-ShrutiNeural":   "Shruti - Telugu Female (Azure)",
    # ElevenLabs voices
    "ELEVENLABS_MALE_VOICE":   "Adam - Male (ElevenLabs)",
    "ELEVENLABS_FEMALE_VOICE": "Rachel - Female (ElevenLabs)",
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "page" not in st.session_state:
    st.session_state.page = "login"

def show_login():
    st.markdown('<style>body{background:#0a0a0f}</style>', unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;color:#FF8C00;font-size:3rem;'>VideoDubber AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#555;letter-spacing:3px;'>MULTILINGUAL NEURAL VIDEO DUBBING</p>", unsafe_allow_html=True)
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("Welcome back")
        email = st.text_input("Email Address", placeholder="you@example.com", key="li_email")
        password = st.text_input("Password", type="password", placeholder="Your password", key="li_pass")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Sign In", use_container_width=True, type="primary"):
            if not email or not password:
                st.error("Please fill in all fields!")
            else:
                success, name, message = login_user(email, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.user_name = name
                    st.session_state.page = "app"
                    st.rerun()
                else:
                    st.error(message)
        st.markdown("---")
        st.markdown("<p style='text-align:center;color:#555;'>Don't have an account?</p>", unsafe_allow_html=True)
        if st.button("Create New Account", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a: st.markdown("<div style='text-align:center;background:rgba(255,140,0,0.1);border:1px solid rgba(255,140,0,0.3);border-radius:20px;padding:4px;color:#FF8C00;font-size:0.75rem;'>Kannada</div>", unsafe_allow_html=True)
        with col_b: st.markdown("<div style='text-align:center;background:rgba(255,140,0,0.1);border:1px solid rgba(255,140,0,0.3);border-radius:20px;padding:4px;color:#FF8C00;font-size:0.75rem;'>Hindi</div>", unsafe_allow_html=True)
        with col_c: st.markdown("<div style='text-align:center;background:rgba(255,140,0,0.1);border:1px solid rgba(255,140,0,0.3);border-radius:20px;padding:4px;color:#FF8C00;font-size:0.75rem;'>Tamil</div>", unsafe_allow_html=True)
        with col_d: st.markdown("<div style='text-align:center;background:rgba(255,140,0,0.1);border:1px solid rgba(255,140,0,0.3);border-radius:20px;padding:4px;color:#FF8C00;font-size:0.75rem;'>Telugu</div>", unsafe_allow_html=True)

def show_register():
    st.markdown("<h1 style='text-align:center;color:#FF8C00;font-size:3rem;'>VideoDubber AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#555;letter-spacing:3px;'>MULTILINGUAL NEURAL VIDEO DUBBING</p>", unsafe_allow_html=True)
    st.markdown("---")
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1: st.markdown("<div style='text-align:center;padding:1rem;border:1px solid rgba(255,255,255,0.1);border-radius:12px;'><div style='font-size:1.5rem;'>🎙</div><div style='color:#555;font-size:0.8rem;margin-top:5px;'>Neural Voice</div></div>", unsafe_allow_html=True)
    with col_f2: st.markdown("<div style='text-align:center;padding:1rem;border:1px solid rgba(255,255,255,0.1);border-radius:12px;'><div style='font-size:1.5rem;'>🌐</div><div style='color:#555;font-size:0.8rem;margin-top:5px;'>4 Languages</div></div>", unsafe_allow_html=True)
    with col_f3: st.markdown("<div style='text-align:center;padding:1rem;border:1px solid rgba(255,255,255,0.1);border-radius:12px;'><div style='font-size:1.5rem;'>📝</div><div style='color:#555;font-size:0.8rem;margin-top:5px;'>Auto Subtitles</div></div>", unsafe_allow_html=True)
    with col_f4: st.markdown("<div style='text-align:center;padding:1rem;border:1px solid rgba(255,255,255,0.1);border-radius:12px;'><div style='font-size:1.5rem;'>⚡</div><div style='color:#555;font-size:0.8rem;margin-top:5px;'>Fast Processing</div></div>", unsafe_allow_html=True)
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("Create account")
        full_name = st.text_input("Full Name", placeholder="Your full name", key="rg_name")
        email = st.text_input("Email Address", placeholder="you@example.com", key="rg_email")
        password = st.text_input("Password", type="password", placeholder="Min 6 characters", key="rg_pass")
        confirm = st.text_input("Confirm Password", type="password", placeholder="Repeat password", key="rg_confirm")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Create Account", use_container_width=True, type="primary"):
            if not full_name or not email or not password or not confirm:
                st.error("Please fill in all fields!")
            elif password != confirm:
                st.error("Passwords do not match!")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters!")
            else:
                success, message = register_user(full_name, email, password)
                if success:
                    st.success("Account created! Please login.")
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    st.error(message)
        st.markdown("---")
        st.markdown("<p style='text-align:center;color:#555;'>Already have an account?</p>", unsafe_allow_html=True)
        if st.button("Back to Login", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()

def show_app():
    col_logo, col_logout = st.columns([8, 1])
    with col_logo:
        st.markdown(f"<h2 style='color:#FF8C00;padding-top:0.5rem;'>VideoDubber AI <span style='color:#444;font-size:0.9rem;font-weight:400;'>Welcome, {st.session_state.user_name}</span></h2>", unsafe_allow_html=True)
    with col_logout:
        st.markdown("<div style='padding-top:1rem;'>", unsafe_allow_html=True)
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_name = ""
            st.session_state.page = "login"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        uploaded = st.file_uploader("Upload a video file", type=["mp4","mkv","avi","mov"])
    with col2:
        target_language = st.selectbox("Target language", list(LANGUAGES.keys()))
        voice_gender = st.radio("Voice gender", ["Male","Female"], horizontal=True)
        lang_info = LANGUAGES[target_language]
        available_voices = lang_info["voices_male"] if voice_gender == "Male" else lang_info["voices_female"]
        selected_voice = st.selectbox("Select voice", available_voices, format_func=lambda v: VOICE_LABELS.get(v, v))
        generate_subtitles = st.checkbox("Generate subtitle file (.srt)", value=True)

    if uploaded:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f:
            f.write(uploaded.read())
            video_path = f.name
        st.video(uploaded)
        if st.button("Start Dubbing", type="primary"):
            lang_code = lang_info["code"]
            progress = st.progress(0)
            status = st.empty()
            status.info("Step 1/5 - Extracting audio...")
            audio_path = extract_audio(video_path)
            progress.progress(20)
            status.info("Step 2/5 - Transcribing speech...")
            segments = transcribe(audio_path)
            progress.progress(40)
            with st.expander(f"Transcription ({len(segments)} segments)"):
                for seg in segments:
                    st.write(f"{seg['start']:.1f}s to {seg['end']:.1f}s: {seg['text']}")
            status.info(f"Step 3/5 - Translating to {target_language}...")
            translated = translate_segments(segments, target_lang=lang_code)
            progress.progress(60)
            with st.expander(f"Translation ({target_language})"):
                for seg in translated:
                    st.write(f"{seg['start']:.1f}s to {seg['end']:.1f}s: {seg['text']}")
            status.info(f"Step 4/5 - Generating voice ({VOICE_LABELS.get(selected_voice)})...")
            audio_segs = synthesize_segments(
                translated,
                voice_gender=voice_gender.lower(),
                voice_male=selected_voice if voice_gender == "Male" else lang_info["voices_male"][0],
                voice_female=selected_voice if voice_gender == "Female" else lang_info["voices_female"][0],
            )
            progress.progress(80)
            status.info("Step 5/5 - Merging audio and video...")
            output = merge_audio_video(video_path, audio_segs)
            progress.progress(100)
            if generate_subtitles:
                srt_path = generate_srt(translated)
            status.success(f"✅ Dubbing complete! Voice: {VOICE_LABELS.get(selected_voice)}")
            st.subheader("Download outputs")
            dl_col1, dl_col2 = st.columns(2)
            with dl_col1:
                with open(output, "rb") as f:
                    st.download_button(label="Download Dubbed Video", data=f, file_name=f"dubbed_{target_language.lower()}.mp4", mime="video/mp4")
            if generate_subtitles:
                with dl_col2:
                    with open(srt_path, "rb") as f:
                        st.download_button(label="Download Subtitles (.srt)", data=f, file_name=f"subtitles_{target_language.lower()}.srt", mime="text/plain")

if st.session_state.page == "login":
    show_login()
elif st.session_state.page == "register":
    show_register()
elif st.session_state.page == "app":
    if st.session_state.logged_in:
        show_app()
    else:
        st.session_state.page = "login"
        st.rerun();