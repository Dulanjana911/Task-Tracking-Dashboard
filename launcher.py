import os

if __name__ == "__main__":
    python_path = r"C:/Users/DulanjanaK/OneDrive - MAS Holdings (Pvt) Ltd/Desktop/Dulanjana/Python_API/.venv/Scripts/python.exe"
    os.system(f'"{python_path}" -m streamlit run app.py --server.port=8501 --server.address=127.0.0.1')  