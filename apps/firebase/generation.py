import streamlit as st
from vertexai.generative_models import Part
import os
import json

def load_prompt(prompt_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(script_dir, 'prompts', f'{prompt_name}_prompt.md')
    with open(prompt_path, 'r') as file:
        return file.read().strip()

def get_gemini_pro_response(model, prompt, generation_config={}):
    generation_config = {"temperature": 0.1, "max_output_tokens": 8192}
    response = model.generate_content(prompt, generation_config=generation_config, stream=True)
    
    full_response = []
    for chunk in response:
        if chunk.text:
            full_response.append(chunk.text)
            yield chunk.text
    return "".join(full_response)

def generate_video_description(use_case, language, selected_video_uri, multimodal_model_pro):
    if st.button("Generate Video Description", key="generate_video_description", disabled=st.session_state.get('video_description_status') == "Running"):
        st.session_state['video_description_status'] = "Running"
        
        video_description_prompt = load_prompt("video_description")
        video_description_prompt = video_description_prompt.format(language=language, use_case=use_case)
        
        with st.spinner("Generating Video Description..."):
            video_part = Part.from_uri(selected_video_uri, mime_type="video/mp4")
            video_description_response = ""
            for chunk in get_gemini_pro_response(multimodal_model_pro, [video_description_prompt, video_part]):
                video_description_response += chunk
            st.session_state['video_description'] = video_description_response
        st.session_state['video_description_status'] = "Completed"

def generate_robo_script(use_case, language, selected_video_uri, multimodal_model_pro):
    if st.button("Generate Robo Script", key="generate_robo_script", disabled=st.session_state.get('robo_script_status') == "Running"):
        st.session_state['robo_script_status'] = "Running"
        
        if not st.session_state.get('video_description'):
            st.error("Please generate a video description first.")
            st.session_state['robo_script_status'] = "Ready"
            return
        
        robo_script_prompt = load_prompt("robo_script")
        robo_script_prompt = robo_script_prompt.format(
            language=language,
            use_case=use_case,
            video_description=st.session_state['video_description']
        )
        
        with st.spinner("Generating Robo Script..."):
            video_part = Part.from_uri(selected_video_uri, mime_type="video/mp4")
            robo_script_response = ""
            for chunk in get_gemini_pro_response(multimodal_model_pro, [robo_script_prompt, video_part]):
                robo_script_response += chunk
            st.session_state['robo_script'] = robo_script_response
        st.session_state['robo_script_status'] = "Completed"

def generate_test_execution_script(use_case, language, multimodal_model_pro):
    if st.button("Generate Test Execution Script", key="generate_test_script", disabled=st.session_state.get('test_script_status') == "Running"):
        st.session_state['test_script_status'] = "Running"
        
        if not st.session_state.get('robo_script'):
            st.error("Please generate a Robo script first.")
            st.session_state['test_script_status'] = "Ready"
            return
        
        
        robo_script_json = st.session_state['robo_script']
        robo_script_formatted = robo_script_json
        
        test_script_prompt = load_prompt("test_execution")
        test_script_prompt = test_script_prompt.format(
            use_case=use_case,
            robo_script=robo_script_formatted
        )
        
        with st.spinner("Generating Test Execution Script..."):
            test_script_response = ""
            for chunk in get_gemini_pro_response(multimodal_model_pro, test_script_prompt):
                test_script_response += chunk
            st.session_state['test_execution_script'] = test_script_response
        st.session_state['test_script_status'] = "Completed"