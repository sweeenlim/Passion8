from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

nltk.download("vader_lexicon")


def load_vader():
    analyzer = SentimentIntensityAnalyzer()
    return analyzer


def get_vader_score(text: str, vader_model):
    score = vader_model.polarity_scores(text).get("compound")
    return score


def display_sentiment_analysis_tab(tab):
    tab.title("Sentiment Analysis")

    # Input field for text
    text_input = tab.text_area("Enter text for sentiment analysis")

    # Load the VADER model
    vader_model = load_vader()

    # Display button to perform sentiment analysis
    if tab.button("Analyse Sentiment"):
        if text_input:
            sentiment_score = get_vader_score(text_input, vader_model)
            if sentiment_score >= 0.05:
                tab.markdown(
                    f"Sentiment: <p style='color:green;'>Positive</p>",
                    unsafe_allow_html=True,
                )
            elif sentiment_score <= -0.05:
                tab.markdown(
                    f"Sentiment:<p style='color:red;'> Negative</p>",
                    unsafe_allow_html=True,
                )
            else:
                tab.markdown(
                    f"Sentiment: <p style='color:yellow;'>Neutral</p>",
                    unsafe_allow_html=True,
                )
        else:
            tab.write("Please enter some text for analysis.")
