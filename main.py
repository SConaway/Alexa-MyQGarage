import requests
import os
import json
import time
import myq

USERNAME  = os.environ['username']
PASSWORD  = os.environ['password']
SKILL_ID  = os.environ['skill_id']
mq = myq.MyQ(USERNAME,PASSWORD)

def lambda_handler(event, context):


    failFunc = "N"
    
    if (USERNAME == ""):
        print("username environment variable cannot be blank and needs to be set to your MyQ username")
        failFunc = "Y"
    
    if (PASSWORD == ""):
        print("password environment variable cannot be blank and needs to be set to your MyQ password")
        failFunc = "Y"
    
    if (SKILL_ID == ""):
        print("skill_id environment variable cannot be blank and needs to be set to your Alexa Skill's Application ID")
        failFunc = "Y"
    
    if (failFunc == "Y"):
        raise
    
    if event['session']['application']['applicationId'] != SKILL_ID:
        print "Invalid Application ID"
        raise
    else:
        # Not using sessions for now
        sessionAttributes = {}
        mq.login()
        mq.get_device_id()

        if event['session']['new']:
            onSessionStarted(event['request']['requestId'], event['session'])
        if event['request']['type'] == "LaunchRequest":
            speechlet = onLaunch(event['request'], event['session'])
            response = buildResponse(sessionAttributes, speechlet)
        elif event['request']['type'] == "IntentRequest":
            speechlet = onIntent(event['request'], event['session'])
            response = buildResponse(sessionAttributes, speechlet)
        elif event['request']['type'] == "SessionEndedRequest":
            speechlet = onSessionEnded(event['request'], event['session'])
            response = buildResponse(sessionAttributes, speechlet)

        # Return a response for speech output
        return(response)



# Called when the session starts
def onSessionStarted(requestId, session):
    print("onSessionStarted requestId=" + requestId + ", sessionId=" + session['sessionId'])

# Called when the user launches the skill without specifying what they want.
def onLaunch(launchRequest, session):
    # Dispatch to your skill's launch.
    getWelcomeResponse()

# Called when the user specifies an intent for this skill.
def onIntent(intentRequest, session):
    intent = intentRequest['intent']
    intentName = intentRequest['intent']['name']

    # Dispatch to your skill's intent handlers
    if intentName == "StateIntent":
        return stateResponse(intent)
    elif intentName == "MoveIntent":
        return moveIntent(intent)
    elif intentName == "HelpIntent":
        return getWelcomeResponse()
    else:
        print "Invalid Intent (" + intentName + ")"
        raise

# Called when the user ends the session.
# Is not called when the skill returns shouldEndSession=true.
def onSessionEnded(sessionEndedRequest, session):
    # Add cleanup logic here
    print "Session ended"

def getWelcomeResponse():
    cardTitle = "Welcome"
    speechOutput = """You can turn on or turn off your light by saying, ask my light to turn on."""

    # If the user either does not reply to the welcome message or says something that is not
    # understood, they will be prompted again with this text.
    repromptText = 'Ask me to turn your light off by saying ask my light to turn off'
    shouldEndSession = True

    return (buildSpeechletResponse(cardTitle, speechOutput, repromptText, shouldEndSession))

def moveIntent(intent):
    """
    Ask my garage to {turned on|turned off|on|off}
        "intent": {
          "name": "StateIntent",
          "slots": {
            "lightstate": {
              "name": "lightstate",
              "value": "close"
            }
          }
        }
    """
    if (intent['slots']['lightstate']['value'] == "off") or (intent['slots']['lightstate']['value'] == "turn off"):
        mq.lamp_off()
        speechOutput = "Ok, I'm turning off your light"
        cardTitle = "turning off your light"
    elif (intent['slots']['lightstate']['value'] == "on") or (intent['slots']['lightstate']['value'] == "turn on"):
        mq.lamp_on()
        speechOutput = "Ok, I'm turning on your light"
        cardTitle = speechOutput
    else:
        speechOutput = "I didn't understand that. You can say ask the light to turn on or off"
        cardTitle = "Try again"

    repromptText = "I didn't understand that. You can say ask the light if it's on, or tell it to turn on or off"
    shouldEndSession = True

    return(buildSpeechletResponse(cardTitle, speechOutput, repromptText, shouldEndSession))

def stateResponse(intent):
    """
    Ask my light if it's {turned on|turned off}
        "intent": {
          "name": "StateIntent",
          "slots": {
            "lightstate": {
              "name": "lightstate",
              "value": "turned off"
            }
          }
        }
    """
    lightstate = mq.lamp_status()

    if (intent['slots']['lightstate']['value'] == "on") or (intent['slots']['lightstate']['value'] == "turned on"):
        if lightstate == "on":
            speechOutput = "Yes, your light is on"
            cardTitle = "Yes, your light is on"
        elif lightstate == "off":
            speechOutput = "No, your light is off"
            cardTitle = "No, your light is off"
        else:
            speechOutput = "Your light is " + lightstate
            cardTitle = "Your light is " + lightstate

    elif (intent['slots']['lightstate']['value'] == "off") or (intent['slots']['lightstate']['value'] == "turned off"):
        if lightstate == "of":
            speechOutput = "Yes, your light is off"
            cardTitle = "Yes, your light is off"
        elif lightstate == "on":
            speechOutput = "No, your light is on"
            cardTitle = "No, your light is on"
        else:
            speechOutput = "Your light is " + lightstate
            cardTitle = "Your light is " + lightstate

    else:
        speechOutput = "I didn't understand that. You can say ask the light if it's turned on"
        cardTitle = "Try again"

    repromptText = "I didn't understand that. You can say ask the light if it's turned on"
    shouldEndSession = True

    return(buildSpeechletResponse(cardTitle, speechOutput, repromptText, shouldEndSession))


# --------------- Helpers that build all of the responses -----------------------
def buildSpeechletResponse(title, output, repromptText, shouldEndSession):
    return ({
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": "MyQ - " + title,
            "content": "MyQ - " + output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": repromptText
            }
        },
        "shouldEndSession": shouldEndSession
    })

def buildResponse(sessionAttributes, speechletResponse):
    return ({
        "version": "1.0",
        "sessionAttributes": sessionAttributes,
        "response": speechletResponse
    })
