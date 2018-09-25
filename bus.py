"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6
 
For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""
 
from __future__ import print_function
import urllib2
import xml.etree.ElementTree as etree
from datetime import datetime as dt
 
def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])
 
    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")
 
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])
 
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
 
 
def on_session_started(session_started_request, session):
    """ Called when the session starts """
 
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])
 
 
def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
 
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()
 
 
def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """
 
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])
 
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
 
    # Dispatch to your skill's intent handlers
    if intent_name == "NextBus":
        return get_58_time(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    else:
        raise ValueError("Invalid intent")
 
 
def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
 
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here
 
# --------------- Functions that control the skill's behavior ------------------
 
 
def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
 
    session_attributes = {}
    card_title = "Bienvenue"
    speech_output = "Bienvenue" \
                    "Vous pouvez demander: " \
                    "Quand passe le prochain bus?"
    card_output = "Bienvenue" \
                    "Vous pouvez demander: " \
                    "Quand passe le prochain bus?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Vous pouvez demander:" \
                    "Quand passe le prochain bus?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session, card_output))
 
 
def get_58_time(intent, session):
    """Cherche les minutes avant les prochains passages
    """
 
    card_title = "Ligne 58 Lesage/Parc"
    session_attributes = {}
    should_end_session = True
 
    url="http://webservices.nextbus.com/service/publicXMLFeed?command=predictions&a=stl&r=58O&s=42562"
    xml_data = urllib2.urlopen(url)

    tree = etree.parse(xml_data)

    xml_data.close()
 
    #Find the root element
    rootElem = tree.getroot()
 
    #list that will hold the minutes before next busses
    minutesList = []


    #iterates over elements in rootElem finding minutes in the prediction tag
    for element in rootElem.iter('prediction'):
        if element.attrib:
            minutes = element.get('minutes')
            minutesList.append(minutes)

    #counter to dertermine how the speech output will proceed
    count = 0
    for element in rootElem.iter('prediction'):
        count += 1
 
    if count == 0:
        speech_output = "Pas de bus dans l'horaire"
        card_output = "Pas de bus dans l'horaire."
        reprompt_text = ""
    if count == 1:
        speech_output = "Le prochain bus arrive dans " + str(minutesList[0]) + " minutes"
        card_output =  str(minutesList[0]) + " minutes."
        reprompt_text = ""
    if count == 2:
        speech_output = "Les prochains bus arrivent dans " + str(minutesList[0]) + " et " + str(minutesList[1]) + " minutes"
        card_output =  str(minutesList[0]) + " et " + str(minutesList[1]) + " minutes."
        reprompt_text = ""
    if count >= 3:
        speech_output = "Les prochains bus arrivent dans " + str(minutesList[0]) + " , " + str(minutesList[1]) + " et " + str(minutesList[2]) + " minutes"
        card_output =  str(minutesList[0]) + " , " + str(minutesList[1]) + " et " + str(minutesList[2]) + " minutes"
        reprompt_text = ""		
	
    else:
        reprompt_text = "Vous pouvez dire: " \
                        "Quand passe le prochain bus?"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session, card_output))
 
 
# --------------- Helpers that build all of the responses ----------------------
 
 
def build_speechlet_response(title, output, reprompt_text, should_end_session, card):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': card
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }
 
 
def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
