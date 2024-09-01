from Adfluence import create_app
import os

app = create_app()

if __name__ == "__main__":
    port = int(
        os.environ.get("PORT", 5000)
    )  # Get the PORT environment variable, default to 5000 if not set
    app.run(
        host="0.0.0.0", port=port, debug=True
    )  # Run the app on all available network interfaces

# todo end budget after its end date or give the option to end it.
# limit budget of adrequests to budget of the campaign.
# todo make my editCampaign's form better.
