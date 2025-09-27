import sys
import streamlit.web.cli as stcli

if __name__ == "__main__":
    sys.argv = ["streamlit", "run", "src/main.py", "--server.port", "8501"]
    sys.exit(stcli.main())
