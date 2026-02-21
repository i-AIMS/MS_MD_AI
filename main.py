import os
import time
import argparse
import requests
import pandas as pd
from tqdm import tqdm
from pypdf import PdfReader
from pypdf.errors import PdfStreamError
from requests.adapters import HTTPAdapter, Retry


def download_file(url: str, save_path: str):
    """
    Adapted from: https://realpython.com/python-download-file-from-url/
    Additional source:
    - https://stackoverflow.com/questions/60798728/put-a-time-limit-on-a-request (to avoid hanging when no response from server)
    - ChatGPT
    - https://stackoverflow.com/questions/606191/
    Action: downloads.
    returns: Boolean (downloaded?)
    """
    session = create_session()

    try:
        response = session.get(
            url,
            stream=True,
            timeout=30,
        )
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)

        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError or requests.exceptions.ChunkedEncodingError:
        return False


def create_session():
    # Sources:
    # - https://stackoverflow.com/questions/15778466/using-python-requests-sessions-cookies-and-post
    # - https://github.com/psf/requests/blob/main/docs/user/advanced.rst#example-automatic-retries
    # - https://stackoverflow.com/questions/15431044/can-i-set-max-retries-for-requests-request
    # - ChatGPT

    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--download_folder_path', type=str)
    parser.add_argument('--excel_path', type=str)
    args = parser.parse_args()
    return args.download_folder_path, args.excel_path


if __name__ == '__main__':
    # Keep log
    time_now = time.time()
    log = f'###########\n{time_now}\n###########\n\n'

    # Get download folder path and which downloads already performed
    path_download_folder, excel_path = parse_arguments()
    if not os.path.exists(path_download_folder):
        os.makedirs(path_download_folder)
    downloaded_files = os.listdir(path_download_folder)

    # Download and load dataframe
    df = pd.read_excel(excel_path)
    log += f'Total number of submission numbers in Excel: {df.shape[0]}\n\n'

    # Loop over dataframe and download summaries
    for submission_number in tqdm(df['Submission Number']):
        if f'{submission_number}.pdf' in downloaded_files:
            print(f'Already downloaded {submission_number}. Skipping.')
            continue
        # Potential improvements: sometimes summary in "/review/"
        download_urls = [f'https://www.accessdata.fda.gov/cdrh_docs/pdf{pdf_nr}/{submission_number}.pdf' for pdf_nr in reversed([''] + list(range(1, 26)))]
        download_urls += [f'https://www.accessdata.fda.gov/cdrh_docs/pdf{pdf_nr}/{submission_number}B.pdf' for pdf_nr in reversed([''] + list(range(1, 26)))]
        for download_url in download_urls:
            found = download_file(download_url, os.path.join(path_download_folder, os.path.basename(download_url)))
            if found:
                break
        if not found:
            log_sn = f'PDF for submission number {submission_number} not found'
            log += log_sn
            print(log_sn)

    with open(os.path.join(path_download_folder, 'log.txt'), 'w') as f:
        f.write(log)

    # Read PDFs and check if "multiple sclerosis" present in lowercase text
    # Source:
    txt_ms_in_summary = f'###########\n{time_now}\n###########\n\n'
    txt_ms_in_summary += f'Total number of submission numbers in Excel: {df.shape[0]}\n\n'
    for file in tqdm(os.listdir(path_download_folder)):
        if file.endswith('.pdf'):
            # Read PDF text and make lowercase
            # Occasional Warnings:
            # - "invalid pdf header":
            # - Advanced encoding /UniJIS-UTF16-H not implemented yet
            # More info: https://github.com/py-pdf/pypdf/issues/1840
            try:
                reader = PdfReader(os.path.join(path_download_folder, file))

                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                text = text.lower()

                # Check if "multiple sclerosis" occurs in the document
                if "multiple sclerosis" in text:
                    match_txt = f'{file}\n{dict(df[df["Submission Number"] == file.removesuffix(".pdf")].iloc[0])}\n\n'
                    txt_ms_in_summary += match_txt
                    print(match_txt)

            except PdfStreamError:
                msg = f'PDF Stream Error for {file}'
                txt_ms_in_summary += f'\n\n{msg}\n\n'

    with open(os.path.join(path_download_folder, 'submission_summaries_with_ms.txt'), 'w') as fp:
        fp.write(txt_ms_in_summary)
