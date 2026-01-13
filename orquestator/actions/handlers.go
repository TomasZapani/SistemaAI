package actions

import (
	"encoding/json"
	"log"
	"orquestator/api/calendar"
	"orquestator/api/session"
	"orquestator/helper"
)

type ActionHandler func(string, json.RawMessage) (string, error)

var actions map[string]ActionHandler

func registerAction(actionName string, handler ActionHandler) {
	actions[actionName] = handler
}

func GetAction(actionName string) ActionHandler {
	return actions[actionName]
}

func InitActions() {
	actions = make(map[string]ActionHandler)

	registerAction("TALK", HandleTalk)
	registerAction("END_CALL", HandleEndCall)
	registerAction("CALENDAR_LIST", HandleCalendarList)
	registerAction("CALENDAR_CREATE", HandleCalendarCreate)
	registerAction("CALENDAR_UPDATE", HandleCalendarUpdate)
	registerAction("CALENDAR_DELETE", HandleCalendarDelete)
}

func HandleTalk(callSid string, data json.RawMessage) (string, error) {
	var talkData TalkData
	if err := json.Unmarshal(data, &talkData); err != nil {
		log.Println("Error unmarshaling TALK data:", err)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}
	return helper.GatherCall(talkData.Message)
}

func HandleCalendarList(callSid string, data json.RawMessage) (string, error) {
	var payload calendar.CalendarListRequest
	if err := json.Unmarshal(data, &payload); err != nil {
		log.Println("Error unmarshaling CALENDAR_LIST data:", err)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}

	respBody, err := calendar.CalendarList(&payload)
	ctx := "CALENDAR_LIST_ERROR"
	if err == nil {
		ctx = "CALENDAR_LIST_OK " + string(respBody)
	} else {
		ctx = "CALENDAR_LIST_ERROR " + err.Error()
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

func HandleCalendarCreate(callSid string, data json.RawMessage) (string, error) {
	var payload calendar.CalendarCreateRequest
	if err := json.Unmarshal(data, &payload); err != nil {
		log.Println("Error unmarshaling CALENDAR_CREATE data:", err)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}

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

func HandleCalendarUpdate(callSid string, data json.RawMessage) (string, error) {
	var payload calendar.CalendarUpdateRequest
	if err := json.Unmarshal(data, &payload); err != nil {
		log.Println("Error unmarshaling CALENDAR_UPDATE data:", err)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}

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

func HandleCalendarDelete(callSid string, data json.RawMessage) (string, error) {
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

func HandleEndCall(callSid string, data json.RawMessage) (string, error) {
	log.Printf("(%s): Finished call.\n", callSid)
	var talkData TalkData
	if err := json.Unmarshal(data, &talkData); err != nil {
		log.Println("Error unmarshaling END_CALL data:", err)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}
	session.End(callSid)
	return helper.EndCall(talkData.Message)
}

/*
func HandleCreateAppointment(callSid string, fromNumber string, data json.RawMessage) (string, error) {
	var appointmentData CreateAppointmentData
	if err := json.Unmarshal(data, &appointmentData); err != nil {
		log.Println("Error unmarshaling appointment data:", err)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}

	// 1. Guardar en DB
	err := database.CreateAppointment(&appointmentData, fromNumber)

	// 2. Notificar al Agente sobre el resultado (Context)
	contextResponse, err := Context(callSid, strconv.FormatBool(err == nil))
	if err != nil {
		log.Println("Error context response:", err)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}

	// 3. Responder al usuario con el mensaje que el agente decida
	var talkData TalkData
	if err = json.Unmarshal(contextResponse.Data, &talkData); err != nil {
		log.Println("Error unmarshaling context response data:", err)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}

	return helper.GatherCall(talkData.Message)
}
*/
