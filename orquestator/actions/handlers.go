package actions

import (
	"encoding/json"
	"log"
	"orquestator/api/calendar"
	"orquestator/api/session"
	"orquestator/helper"
)

type ActionHandler func(string, string, json.RawMessage) (string, error)

var actions map[string]ActionHandler

func registerAction(actionName string, handler ActionHandler) {
	actions[actionName] = handler
}

// Get an action handler
func GetActionHandler(actionName string) ActionHandler {
	return actions[actionName]
}

// Init all actions handlers for the model
func InitActions() {
	actions = make(map[string]ActionHandler)

	registerAction("TALK", HandleTalk)
	registerAction("END_CALL", HandleEndCall)
	registerAction("CALENDAR_LIST", HandleCalendarList)
	registerAction("CALENDAR_CREATE", HandleCalendarCreate)
	registerAction("CALENDAR_UPDATE", HandleCalendarUpdate)
	registerAction("CALENDAR_DELETE", HandleCalendarDelete)
	registerAction("CALENDAR_SEARCH", HandleCalendarSearch)
}

func HandleTalk(callSid, fromNumber string, data json.RawMessage) (string, error) {
	var talkData TalkData
	if err := json.Unmarshal(data, &talkData); err != nil {
		log.Println("Error unmarshaling TALK data:", err)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}
	return helper.GatherCall(talkData.Message)
}

func HandleCalendarList(callSid, fromNumber string, data json.RawMessage) (string, error) {
	var payload calendar.CalendarListRequest
	if err := json.Unmarshal(data, &payload); err != nil {
		log.Println("Error unmarshaling CALENDAR_LIST data:", err)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}

	respBody, err := calendar.CalendarList(&payload)
	ctx := "CALENDAR_LIST_ERROR"
	if err == nil {
		// Verificamos si la respuesta es una lista vacía "[]"
		if string(respBody) == "[]" {
			ctx = "CALENDAR_LIST_OK: No hay turnos agendados para este día. El día está totalmente libre."
		} else {
			ctx = "CALENDAR_LIST_OK " + string(respBody)
		}
	} else {
		ctx = "CALENDAR_LIST_ERROR " + err.Error()
	}

	contextResponse, ctxErr := session.Context(callSid, ctx)
	if ctxErr != nil {
		log.Println("Error context response:", ctxErr)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}

	if contextResponse.Action != "TALK" {
		log.Printf("La IA decidió saltar directamente a: %s", contextResponse.Action)

		nextHandler := GetActionHandler(contextResponse.Action)
		if nextHandler != nil {
			return nextHandler(callSid, fromNumber, contextResponse.Data)
		}
	}

	var talkData TalkData
	if err = json.Unmarshal(contextResponse.Data, &talkData); err != nil {
		log.Println("Error unmarshaling TALK data:", err)
		return helper.EndCall("Lo siento, no pude procesar tu solicitud.")
	}

	return helper.GatherCall(talkData.Message)
}

func HandleCalendarCreate(callSid, fromNumber string, data json.RawMessage) (string, error) {
	var payload calendar.CalendarCreateRequest
	if err := json.Unmarshal(data, &payload); err != nil {
		log.Println("Error unmarshaling CALENDAR_CREATE data:", err)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}

	payload.ClientPhone = fromNumber

	respBody, err := calendar.CalendarCreate(&payload)
	ctx := "CALENDAR_CREATE_ERROR"
	if err == nil {
		ctx = "CALENDAR_CREATE_OK " + string(respBody)
	} else {
		ctx = "CALENDAR_CREATE_ERROR " + err.Error()
	}

	contextResponse, ctxErr := session.Context(callSid, ctx)
	if ctxErr != nil {
		log.Println("Error context response:", ctxErr)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}

	var talkData TalkData
	if err = json.Unmarshal(contextResponse.Data, &talkData); err != nil {
		log.Println("Error unmarshaling context response data:", err)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}

	return helper.GatherCall(talkData.Message)
}

func HandleCalendarUpdate(callSid, fromNumber string, data json.RawMessage) (string, error) {
	var payload calendar.CalendarUpdateRequest
	if err := json.Unmarshal(data, &payload); err != nil {
		log.Println("Error unmarshaling CALENDAR_UPDATE data:", err)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}

	payload.ClientPhone = fromNumber

	respBody, err := calendar.CalendarUpdate(&payload)
	ctx := "CALENDAR_UPDATE_ERROR"
	if err == nil {
		ctx = "CALENDAR_UPDATE_OK " + string(respBody)
	} else {
		ctx = "CALENDAR_UPDATE_ERROR " + err.Error()
	}

	contextResponse, ctxErr := session.Context(callSid, ctx)
	if ctxErr != nil {
		log.Println("Error context response:", ctxErr)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}

	var talkData TalkData
	if err = json.Unmarshal(contextResponse.Data, &talkData); err != nil {
		log.Println("Error unmarshaling context response data:", err)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}

	return helper.GatherCall(talkData.Message)
}

func HandleCalendarDelete(callSid, fromNumber string, data json.RawMessage) (string, error) {
	var payload calendar.CalendarDeleteRequest
	if err := json.Unmarshal(data, &payload); err != nil {
		log.Println("Error unmarshaling CALENDAR_DELETE data:", err)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}

	respBody, err := calendar.CalendarDelete(&payload)
	ctx := "CALENDAR_DELETE_ERROR"
	if err == nil {
		ctx = "CALENDAR_DELETE_OK " + string(respBody)
	} else {
		ctx = "CALENDAR_DELETE_ERROR " + err.Error()
	}

	contextResponse, ctxErr := session.Context(callSid, ctx)
	if ctxErr != nil {
		log.Println("Error context response:", ctxErr)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}

	var talkData TalkData
	if err = json.Unmarshal(contextResponse.Data, &talkData); err != nil {
		log.Println("Error unmarshaling context response data:", err)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}

	return helper.GatherCall(talkData.Message)
}

func HandleEndCall(callSid, fromNumber string, data json.RawMessage) (string, error) {
	log.Printf("(%s): Finished call.\n", callSid)
	var talkData TalkData
	if err := json.Unmarshal(data, &talkData); err != nil {
		log.Println("Error unmarshaling END_CALL data:", err)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}
	session.End(callSid)
	return helper.EndCall(talkData.Message)
}

func HandleCalendarSearch(callSid, fromNumber string, data json.RawMessage) (string, error) {
	var payload calendar.CalendarSearchRequest
	if err := json.Unmarshal(data, &payload); err != nil {
		log.Println("Error unmarshaling CALENDAR_SEARCH data:", err)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}

	payload.ClientPhone = fromNumber

	respBody, err := calendar.CalendarSearch(&payload)
	ctx := "CALENDAR_SEARCH_ERROR"
	if err == nil {
		// Verificamos si la respuesta es una lista vacía "[]"
		if string(respBody) == "[]" {
			ctx = "CALENDAR_SEARCH_OK: No hay turnos agendados para este numero."
		} else {
			ctx = "CALENDAR_SEARCH_OK " + string(respBody)
		}
	} else {
		ctx = "CALENDAR_SEARCH_ERROR " + err.Error()
	}

	contextResponse, ctxErr := session.Context(callSid, ctx)
	if ctxErr != nil {
		log.Println("Error context response:", ctxErr)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}

	if contextResponse.Action != "TALK" {
		log.Printf("La IA decidió saltar directamente a: %s", contextResponse.Action)

		nextHandler := GetActionHandler(contextResponse.Action)
		if nextHandler != nil {
			return nextHandler(callSid, fromNumber, contextResponse.Data)
		}
	}

	var talkData TalkData
	if err = json.Unmarshal(contextResponse.Data, &talkData); err != nil {
		log.Println("Error unmarshaling TALK data:", err)
		return helper.EndCall("Lo siento, no pude procesar tu solicitud.")
	}

	return helper.GatherCall(talkData.Message)
}
