package actions

import (
	"encoding/json"
	"log"
	"orquestator/api/appointment"
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
	registerAction("APPOINTMENT_LIST", HandleAppointmentList)
	registerAction("APPOINTMENT_CREATE", HandleAppointmentCreate)
	registerAction("APPOINTMENT_UPDATE", HandleAppointmentUpdate)
	registerAction("APPOINTMENT_DELETE", HandleAppointmentDelete)
	registerAction("APPOINTMENT_SEARCH", HandleAppointmentSearch)
}

func HandleTalk(callSid, fromNumber string, data json.RawMessage) (string, error) {
	var talkData TalkData
	if err := json.Unmarshal(data, &talkData); err != nil {
		log.Println("Error unmarshaling TALK data:", err)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}
	return helper.GatherCall(talkData.Message)
}

func HandleAppointmentList(callSid, fromNumber string, data json.RawMessage) (string, error) {
	var payload appointment.AppointmentListRequest
	if err := json.Unmarshal(data, &payload); err != nil {
		log.Println("Error unmarshaling APPOINTMENT_LIST data:", err)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}

	respBody, err := appointment.AppointmentList(&payload)
	ctx := "APPOINTMENT_LIST_ERROR"
	if err == nil {
		// Verificamos si la respuesta es una lista vacía "[]"
		if string(respBody) == "[]" {
			ctx = "APPOINTMENT_LIST_OK: No hay turnos agendados para este día. El día está totalmente libre."
		} else {
			ctx = "APPOINTMENT_LIST_OK " + string(respBody)
		}
	} else {
		ctx = "APPOINTMENT_LIST_ERROR " + err.Error()
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

func HandleAppointmentCreate(callSid, fromNumber string, data json.RawMessage) (string, error) {
	var payload appointment.AppointmentCreateRequest
	if err := json.Unmarshal(data, &payload); err != nil {
		log.Println("Error unmarshaling APPOINTMENT_CREATE data:", err)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}

	payload.ClientPhone = fromNumber

	respBody, err := appointment.AppointmentCreate(&payload)
	ctx := "APPOINTMENT_CREATE_ERROR"
	if err == nil {
		ctx = "APPOINTMENT_CREATE_OK " + string(respBody)
	} else {
		ctx = "APPOINTMENT_CREATE_ERROR " + err.Error()
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

func HandleAppointmentUpdate(callSid, fromNumber string, data json.RawMessage) (string, error) {
	var payload appointment.AppointmentUpdateRequest
	if err := json.Unmarshal(data, &payload); err != nil {
		log.Println("Error unmarshaling APPOINTMENT_UPDATE data:", err)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}

	payload.ClientPhone = fromNumber

	respBody, err := appointment.AppointmentUpdate(&payload)
	ctx := "APPOINTMENT_UPDATE_ERROR"
	if err == nil {
		ctx = "APPOINTMENT_UPDATE_OK " + string(respBody)
	} else {
		ctx = "APPOINTMENT_UPDATE_ERROR " + err.Error()
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

func HandleAppointmentDelete(callSid, fromNumber string, data json.RawMessage) (string, error) {
	var payload appointment.AppointmentDeleteRequest
	if err := json.Unmarshal(data, &payload); err != nil {
		log.Println("Error unmarshaling APPOINTMENT_DELETE data:", err)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}

	respBody, err := appointment.AppointmentDelete(&payload)
	ctx := "APPOINTMENT_DELETE_ERROR"
	if err == nil {
		ctx = "APPOINTMENT_DELETE_OK " + string(respBody)
	} else {
		ctx = "APPOINTMENT_DELETE_ERROR " + err.Error()
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

func HandleAppointmentSearch(callSid, fromNumber string, data json.RawMessage) (string, error) {
	var payload appointment.AppointmentSearchRequest
	if err := json.Unmarshal(data, &payload); err != nil {
		log.Println("Error unmarshaling APPOINTMENT_SEARCH data:", err)
		return helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}

	payload.ClientPhone = fromNumber

	respBody, err := appointment.AppointmentSearch(&payload)
	ctx := "APPOINTMENT_SEARCH_ERROR"
	if err == nil {
		// Verificamos si la respuesta es una lista vacía "[]"
		if string(respBody) == "[]" {
			ctx = "APPOINTMENT_SEARCH_OK: No hay turnos agendados para este numero."
		} else {
			ctx = "APPOINTMENT_SEARCH_OK " + string(respBody)
		}
	} else {
		ctx = "APPOINTMENT_SEARCH_ERROR " + err.Error()
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
