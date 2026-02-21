# Find AI-based medical devices built for multiple sclerosis
This repository aims to find AI-based MDs for MS from the [FDA website](https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-enabled-medical-devices).\
Run time (21/02/2026):
- PDF download: ± 45 min
- PDF read: ± 5 min

***

# How to get started:
1. Fork repository in GitHub
2. Clone the repository locally `git clone https://github.com/YOUR_USERNAME/MS_MD_AI.git`
3. Download the Excel file from the [FDA website](https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-enabled-medical-devices)
4. Run script: `python3 main.py --download_folder_path LOCAL_DOWNLOAD_PATH --excel_path LOCAL_EXCEL_PATH`
    - `--download_folder_path`: Local path to where you want to download PDF files
    - `--excel_path`: Local path to the downloaded Excel from the FDA website

***

## How it works:
1. The script tries to download the summary PDF associated with each submission number in the Excel.
2. The PDFs are read in Python (text), made lower case.
3. Check whether "multiple sclerosis" is in the lower case text
