# WhatsApp Chat Analysis

This project is a Streamlit application that allows you to analyze WhatsApp chat data. It provides various visualizations and insights into the chat, including basic information, author stats, emoji distribution, emoji usage by author, top days with the most messages, message distribution by day, and a word cloud.

## Live Link
[Check Out Live](https://whatsapp-chat-69.streamlit.app/)

## Features

- **Basic Information**: Displays the first 20 conversations from the chat.
- **Author Stats**: Shows statistics for each author, including the number of messages sent, words per message, emoji count, and average response time.
- **Emoji Distribution**: Presents a pie chart depicting the distribution of emojis used in the chat.
- **Emoji Usage by Author**: Displays a stacked bar chart showing the usage of emojis by each author.
- **Top 10 Days with Most Messages**: Highlights the top 10 days with the highest number of messages using a bar chart.
- **Message Distribution by Day**: Visualizes the distribution of messages across different days of the week using a polar line chart.
- **Word Cloud**: Generates a word cloud from the chat messages, excluding common stopwords.

## Prerequisites

Before running the application, make sure you have the following dependencies installed:

- Python
- Streamlit
- Pandas
- Plotly
- Matplotlib
- Seaborn
- Wordcloud
- NLTK

You can install the required packages using the following command:<br>
```pip install -r requirements.txt```

## Usage

1. Clone or download the repository to your local machine.
2. Navigate to the project directory in your terminal or command prompt.
3. Run the following command to start the Streamlit application:<br>
    ```streamlit run app.py```
4. The application will open in your default web browser.
5. Upload a WhatsApp chat file in either .txt or .zip format.
6. The application will process the chat file and display various visualizations and insights.

## Obtaining the WhatsApp Chat File

To obtain the WhatsApp chat file, follow these steps:

### For Android Devices:

1. Open the WhatsApp chat you want to analyze.
2. Tap on the three-dot menu in the top-right corner of the chat.
3. Select "More" > "Export Chat".
4. Choose whether to export with or without media.
5. Select the export format as ".txt" or ".zip".
6. Choose the destination location to save the file.

### For iOS Devices:

1. Open the WhatsApp chat you want to analyze.
2. Tap on the group name or contact at the top of the chat.
3. Select "Export Chat".
4. Choose whether to export with or without media.
5. Select the export format as ".txt" or ".zip".
6. Choose the destination location to save the file.

Note: The exported chat file may contain sensitive information, so handle it with care and respect the privacy of others.

## Contributing

Contributions are welcome! If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- [Streamlit](https://streamlit.io/) for providing an excellent framework for building data-centric applications.
- [Pandas](https://pandas.pydata.org/), [Plotly](https://plotly.com/python/), [Matplotlib](https://matplotlib.org/), [Seaborn](https://seaborn.pydata.org/), [Wordcloud](https://github.com/amueller/word_cloud), and [NLTK](https://www.nltk.org/) for their powerful data manipulation and visualization libraries.
