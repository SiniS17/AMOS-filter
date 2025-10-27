\# Google Drive File Download and Processing Script



This project is a Python script to download and process Excel files from Google Drive, based on the \*\*`wp`\*\* (work package) value in the file. The files are downloaded into specific folders named after the `wp` value. Once downloaded, the files are processed, and a processed output file is generated with timestamp-based naming.



\## Features

\- Download files from Google Drive to specific folders.

\- Automatically create folders based on `wp` value in the Excel file.

\- Add filters to Excel columns.

\- Process the Excel file and add a "Reason" column based on specific checks.

&nbsp; 

\## Requirements

\- Python 3.x

\- Google API Key and Folder ID for accessing Google Drive



\## Setup Instructions



1\. Clone this repository:

&nbsp;   ```bash

&nbsp;   git clone https://github.com/your-username/google-drive-excel-process.git

&nbsp;   cd google-drive-excel-process

&nbsp;   ```



2\. Install the dependencies:

&nbsp;   ```bash

&nbsp;   pip install -r requirements.txt

&nbsp;   ```



3\. Create a `link.txt` file in the root directory with the following structure:

&nbsp;   ```

&nbsp;   GG\_API\_KEY=your\_google\_api\_key

&nbsp;   GG\_FOLDER\_ID=your\_google\_folder\_id

&nbsp;   ```



4\. Run the script:

&nbsp;   ```bash

&nbsp;   python main.py

&nbsp;   ```



\## How It Works

1\. \*\*Authentication\*\*: Uses the provided Google API Key to authenticate and access Google Drive.

2\. \*\*File Download\*\*: The script dynamically downloads Excel files from the specified Google Drive folder and names them based on the `wp` value found in the file.

3\. \*\*Processing\*\*: The file is processed, and a "Reason" column is added based on predefined rules.

4\. \*\*Saving\*\*: The processed file is saved in the respective folder under the `DATA` directory.



\## License

This project is licensed under the MIT License - see the \[LICENSE](LICENSE) file for details.



