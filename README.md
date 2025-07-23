# MRScraper

## Description
MRScraper is a Python application that provides users a quick, easy and efficient way to mass-download ROMs from the media preservation site [myrient.erista.me](https://myrient.erista.me/). The app is designed to help streamline the process of acquiring ROMs with various filters in place to make sure the user is getting only the top-quality material while still being comprehensive.

## Features
- Mass downloads from media preservation site [myrient.erista.me](https://myrient.erista.me/)
- User-friendly GUI
- Select console system from a predefined list
- Options for custom downloads
- Filter ROMs by region
- Smart filtering to optimal ROMs
- Enable/Disable various download filters
- Choose region for the files
- Specify output directory
- Progress bar to show download status
- Cancel download option
- Pause download option

## Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/gearandpens/MRScraper.git
    ```
2. Navigate to the project directory:
    ```sh
    cd MRScraper
    ```
3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage
1. Run the application:
    ```sh
    python main.py
    ```
2. Select the console system from the dropdown list.
3. Choose the region for the files.
4. (Optional) Check the "Limit files" option and set upper boundary.
5. Specify the output directory.
6. Click "Start Download" to begin downloading files.
7. Use the "Cancel Download" button to stop the download process.

## Requirements
-  Python 3.x
- `requests`
- `beautifulsoup4`

## Contributing
1. Fork the repository.
2. Create a new branch:
    ```sh
    git checkout -b feature/your-feature
    ```
3. Make your changes and commit them:
    ```sh
    git commit -m "Add your feature"
    ```
4. Push to the branch:
    ```sh
    git push origin feature/your-feature
    ```
5. Open a pull request.

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Acknowledgements
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [Requests](https://docs.python-requests.org/en/latest/)
