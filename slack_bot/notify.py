import os
import json
import base64
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
import functions_framework
from flask import Request, jsonify

load_dotenv()

# --- Configuration ---
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#general")

# Initialize Slack client
try:
    slack_client = WebClient(token=SLACK_BOT_TOKEN)
except Exception as e:
    print(f"Error initializing Slack client: {e}")
    slack_client = None

# --- Message Formatting ---
def format_slack_message(signal_data: dict) -> list:
    """Formats the signal data into a Slack message block."""
    asset_type = signal_data.get("asset_type", "N/A").replace("_", " ").title()
    last_price = signal_data.get("last_price", 0)
    mean_price = signal_data.get("rolling_mean_30d", 0)
    z_score = signal_data.get("z_score", 0)

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f":money_with_wings: New Deal Signal: {asset_type}",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Asset Type:*\n{asset_type}"},
                {"type": "mrkdwn", "text": f"*Current Price:*\n${last_price:,.2f}"},
                {"type": "mrkdwn", "text": f"*30-Day Avg Price:*\n${mean_price:,.2f}"},
                {"type": "mrkdwn", "text": f"*Z-Score:*\n{z_score:.2f}"}
            ]
        },
        {"type": "divider"}
    ]
    return blocks

# --- Cloud Function Entrypoint for Pub/Sub ---
@functions_framework.http
def notify_slack(request: Request):
    """
    HTTP-triggered Cloud Function that receives a Pub/Sub message
    and posts a notification to Slack.
    """
    envelope = request.get_json()
    if not envelope or "message" not in envelope:
        print("Invalid Pub/Sub message format")
        return "Bad Request: Invalid Pub/Sub message format", 400

    pubsub_message = envelope["message"]
    
    # The actual data is Base64-encoded in the 'data' field.
    if "data" in pubsub_message:
        try:
            # Decode the message data
            data_str = base64.b64decode(pubsub_message["data"]).decode("utf-8")
            signal_data = json.loads(data_str)
            print(f"Received signal: {signal_data}")

            # Check if it's a deal worth notifying about
            if signal_data.get("is_deal"):
                if not slack_client or not SLACK_BOT_TOKEN:
                    raise ValueError("Slack client is not initialized. Check SLACK_BOT_TOKEN.")

                message_blocks = format_slack_message(signal_data)
                
                try:
                    response = slack_client.chat_postMessage(
                        channel=SLACK_CHANNEL,
                        text=f"New Deal Signal: {signal_data.get('asset_type')}", # Fallback text
                        blocks=message_blocks
                    )
                    print(f"Message posted to {SLACK_CHANNEL}")
                    return jsonify({"status": "success"}), 200
                except SlackApiError as e:
                    print(f"Error posting to Slack: {e.response['error']}")
                    return jsonify({"status": "error", "message": str(e)}), 500
            else:
                print("Signal received, but not a deal. No notification sent.")
                return jsonify({"status": "success", "message": "Not a deal"}), 200

        except json.JSONDecodeError as e:
            print(f"Error decoding message data: {e}")
            return "Bad Request: Invalid JSON in message data", 400
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return "Internal Server Error", 500
            
    return "OK", 204 