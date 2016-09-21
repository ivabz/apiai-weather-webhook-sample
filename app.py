#!/usr/bin/env python

import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "yahooWeatherForecast":
        return {}
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = makeYqlQuery(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + urllib.urlencode({'q': yql_query}) + "&format=json"
    result = urllib.urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResult(data)
    return res


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"


def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    
    facebook_message = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {
                        "title": Vero Moda,
                        "image_url": "data:image/jpeg;base64,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",
                        "subtitle": "Get Rs. 500 off on spend of Rs. 3000 and above",
                        "buttons": [{
                                "url": "www.veromoda.com",
                                "title": "Validity upto 30 November 2016."
                    }]
                    },
                    {
                        "title": Puma,
                        "image_url": "data:image/png;base64,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",
                        "subtitle": "Enjoy 10% Discount",
                        "buttons": [
                            {
                                "url": "www.puma.com",
                                "title": "Validity upto 1 December 2016."
                            }
                        ]
                    }
                ]
            }
        }
    }
    
    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        "data": {"facebook": facebook_message},
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')
