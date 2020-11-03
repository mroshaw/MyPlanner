# -*- coding: utf-8 -*-

import logging

import ask_sdk_core.utils as ask_utils
from ask_sdk_core.dispatch_components import (AbstractRequestHandler, AbstractExceptionHandler,
                                              AbstractRequestInterceptor)
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_model import Response
from ask_sdk_core.utils.request_util import get_slot

import json

from alexa_jira_helper import AlexaJiraHelper
import prompts

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Get localised strings
        data = handler_input.attributes_manager.request_attributes["_"]

        # Must have linked to Jira account before using the skill
        user = handler_input.request_envelope.session.user
        if user.access_token is None:
            print("Access token not found")
            speak_output = data[prompts.ERROR_NOT_LINKED]
        else:
            print("Access token found")
            print(user.access_token)
            speak_output = data[prompts.WELCOME]
        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


class CatchAccountLinkingErrorHandler(AbstractExceptionHandler):

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        # considering there will be an attribute error for no access_token
        # attribute found, when using
        # handler_input.request_envelope.session.user.access_token
        return type(exception).__name__ == 'AttributeError'

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.info("In CatchAccountLinkingErrorHandler")

        # Get localised strings
        data = handler_input.attributes_manager.request_attributes["_"]

        handler_input.response_builder.speak(data[prompts.ERROR_NOT_LINKED])
        return handler_input.response_builder.response


class AddNewTaskIntentHandler(AbstractRequestHandler):
    """Handler for Add New Task Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AddNewTaskIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Get localised strings
        data = handler_input.attributes_manager.request_attributes["_"]

        # We like to keep an eye on the access_token, just in case it expires or fails to refresh
        user = handler_input.request_envelope.session.user
        access_token = user.access_token
        if access_token is None:
            speak_output = data[prompts.ERROR_NOT_LINKED]
        else:
            task_name_slot = get_slot(handler_input, "taskName")
            task_name = task_name_slot.value.capitalize()
            print(f"Got task name {task_name} from slot")

            # Call the Jira function API
            jira_handler = AlexaJiraHelper(access_token)

            if jira_handler.connected:
                ret_status, issue_id = jira_handler.add_new_todo_task(task_name)
                print(f"Return status: {ret_status}")
                if not ret_status:
                    speak_output = data[prompts.ERROR_UNKNOWN]
                else:
                    speak_output = f"{data[prompts.TASK_CREATED]} {issue_id}"
            else:
                speak_output = data[prompts.ERROR_UNKNOWN]
        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )


class GetToDoCountIntentHandler(AbstractRequestHandler):
    """Handler for Add New Task Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetToDoCountIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Get localised strings
        data = handler_input.attributes_manager.request_attributes["_"]

        # We like to keep an eye on the access_token, just in case it expires or fails to refresh
        user = handler_input.request_envelope.session.user
        access_token = user.access_token
        if access_token is None:
            speak_output = data[prompts.ERROR_NOT_LINKED]
        else:
            # Call the Jira function API
            jira_handler = AlexaJiraHelper(access_token)

            if jira_handler.connected:
                ret_status, count = jira_handler.todo_task_count()
                print(f"Return status: {ret_status}")
                if not ret_status:
                    speak_output = data[prompts.ERROR_UNKNOWN]
                else:
                    speak_output = f"{data[prompts.TASK_COUNT_1]} {count} {data[prompts.TASK_COUNT_2]}"
            else:
                speak_output = data[prompts.ERROR_UNKNOWN]
        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )


class GetToDoListIntentHandler(AbstractRequestHandler):
    """Handler for Add New Task Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetToDoListIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Get localised strings
        data = handler_input.attributes_manager.request_attributes["_"]

        # We like to keep an eye on the access_token, just in case it expires or fails to refresh
        user = handler_input.request_envelope.session.user
        access_token = user.access_token
        if access_token is None:
            speak_output = data[prompts.ERROR_NOT_LINKED]
        else:
            # Call the Jira function API
            jira_handler = AlexaJiraHelper(access_token)

            if jira_handler.connected:
                ret_status, task_summaries = jira_handler.todo_task_list()
                print(f"Return status: {ret_status}")
                if not ret_status:
                    speak_output = data[prompts.ERROR_UNKNOWN]
                else:
                    speak_output = f"{data[prompts.TASK_LIST]} {task_summaries}"
            else:
                speak_output = data[prompts.ERROR_UNKNOWN]
        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        # Get localised strings
        data = handler_input.attributes_manager.request_attributes["_"]
        speak_output = data[prompts.HELP]

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        # Get localised strings
        data = handler_input.attributes_manager.request_attributes["_"]
        speak_output = data[prompts.GOODBYE]

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )


class LocalizationInterceptor(AbstractRequestInterceptor):
    """
    Add function to request attributes, that can load locale specific data.
    """

    def process(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        logger.info("Locale is {}".format(locale[:2]))

        # Localized strings stored in language_strings.json
        with open("language_strings.json") as language_prompts:
            language_data = json.load(language_prompts)

        # Set default translation data to broader translation
        data = language_data[locale[:2]]
        # If a more specialized translation exists, then select it instead
        # example: "fr-CA" will pick "fr" translations first, but if "fr-CA" translation exists,
        #          then pick that instead
        if locale in language_data:
            data.update(language_data[locale])
        handler_input.attributes_manager.request_attributes["_"] = data


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(AddNewTaskIntentHandler())
sb.add_request_handler(GetToDoCountIntentHandler())
sb.add_request_handler(GetToDoListIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler())
sb.add_global_request_interceptor(LocalizationInterceptor())
sb.add_exception_handler(CatchAccountLinkingErrorHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
