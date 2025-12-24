# Steam Library AI Recommender

A desktop GUI application that scans your Steam library and uses Google's Gemini AI to recommend what to play next based on your specific mood or request.

## Features

* **Library Scanning:** Fetches your entire owned games list using the Steam Web API.
* **AI Recommendations:** Uses Gemini 3.0 Flash preview to analyze your specific library and suggest games based on natural language queries (e.g., "I want a sci-fi RPG with good companions").
* **Proxy Support:** Built-in support for local proxies/VPNs.
* **Secure:** API keys are stored locally on your machine, not on a server.

## Prerequisites

1. **Python 3.x** installed.
2. **Steam API Key:** Get it free [here](https://steamcommunity.com/dev/apikey "null").
3. **Steam ID:** Your 64-bit Steam ID (find it at [steamid.io](https://steamid.io/ "null")).
4. **Gemini API Key:** Get it free [here](https://aistudio.google.com/app/apikey "null").

## Installation

1. Clone this repository:
   ```
   git clone [https://github.com/YOUR_USERNAME/steam-ai-recommender.git](https://github.com/YOUR_USERNAME/steam-ai-recommender.git)
   cd steam-ai-recommender

   ```
2. Install the required libraries:
   ```
   pip install -r requirements.txt

   ```

## Usage

1. Run the application:
   ```
   python steam_recommender_v2.py

   ```
2. Enter your Steam ID and API Keys in the "Configuration" section.
3. (Optional) Set your Proxy URL if you are behind a VPN.
4. Click  **Load Steam Library** .
5. Type your request (e.g., "Short games under 5 hours") and click  **Get AI Recommendations** .

## Privacy Note

This application saves your API keys locally in a `steam_recommender/config.json` file on your computer. These keys are never sent to any third-party server other than the official Steam and Google APIs.
