package handler

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
	"strconv"
	"twilio-ai-agent-go/agent"
	"twilio-ai-agent-go/database"

	"github.com/gin-gonic/gin"
	"github.com/twilio/twilio-go/twiml"
)

// --- Helpers de TwiML ---

func EndCall(message string, context *gin.Context) {
	twimlResult, err := twiml.Voice([]twiml.Element{
		&twiml.VoiceSay{
			Message:  message,
			Voice:    "Polly.Lupe-Generative",
			Language: "es-US",
		},
		&twiml.VoiceHangup{},
	})
	if err != nil {
		context.String(http.StatusInternalServerError, err.Error())
		return
	}
	context.Header("Content-Type", "text/xml")
	context.String(http.StatusOK, twimlResult)
}

func GatherCall(message string, context *gin.Context) {
	twimlResult, err := twiml.Voice([]twiml.Element{
		&twiml.VoiceGather{
			Action:          os.Getenv("GATHER_ENDPOINT"),
			Language:        "es-ES",
			Input:           "speech",
			Enhanced:        "true",
			SpeechTimeout:   "auto",
			ProfanityFilter: "false",
			BargeIn:         "false",
			SpeechModel:     "experimental_conversations",
			InnerElements: []twiml.Element{
				&twiml.VoiceSay{
					Message:  message,
					Voice:    "Polly.Lupe-Generative",
					Language: "es-US",
				},
			},
		},
	})
	if err != nil {
		context.String(http.StatusInternalServerError, err.Error())
		return
	}
	context.Header("Content-Type", "text/xml")
	context.String(http.StatusOK, twimlResult)
}

// --- Manejadores de Acciones ---

func handleTalk(context *gin.Context, data json.RawMessage) {
	var talkData agent.TalkData
	if err := json.Unmarshal(data, &talkData); err != nil {
		log.Println("Error unmarshaling TALK data:", err)
		EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.", context)
		return
	}
	GatherCall(talkData.Message, context)
}

func handleCalendarList(context *gin.Context, callSid string, data json.RawMessage) {
	var payload agent.CalendarListData
	if err := json.Unmarshal(data, &payload); err != nil {
		log.Println("Error unmarshaling CALENDAR_LIST data:", err)
		EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.", context)
		return
	}

	respBody, err := agent.CalendarList(&payload)
	ctx := "CALENDAR_LIST_ERROR"
	if err == nil {
		ctx = "CALENDAR_LIST_OK " + string(respBody)
	} else {
		ctx = "CALENDAR_LIST_ERROR " + err.Error()
	}

	contextResponse, ctxErr := agent.Context(callSid, ctx)
	if ctxErr != nil {
		log.Println("Error context response:", ctxErr)
		EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.", context)
		return
	}

	var talkData agent.TalkData
	if err = json.Unmarshal(contextResponse.Data, &talkData); err != nil {
		log.Println("Error unmarshaling context response data:", err)
		EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.", context)
		return
	}

	GatherCall(talkData.Message, context)
}

func handleCalendarCreate(context *gin.Context, callSid string, data json.RawMessage) {
	var payload agent.CalendarCreateData
	if err := json.Unmarshal(data, &payload); err != nil {
		log.Println("Error unmarshaling CALENDAR_CREATE data:", err)
		EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.", context)
		return
	}

	respBody, err := agent.CalendarCreate(&payload)
	ctx := "CALENDAR_CREATE_ERROR"
	if err == nil {
		ctx = "CALENDAR_CREATE_OK " + string(respBody)
	} else {
		ctx = "CALENDAR_CREATE_ERROR " + err.Error()
	}

	contextResponse, ctxErr := agent.Context(callSid, ctx)
	if ctxErr != nil {
		log.Println("Error context response:", ctxErr)
		EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.", context)
		return
	}

	var talkData agent.TalkData
	if err = json.Unmarshal(contextResponse.Data, &talkData); err != nil {
		log.Println("Error unmarshaling context response data:", err)
		EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.", context)
		return
	}

	GatherCall(talkData.Message, context)
}

func handleCalendarUpdate(context *gin.Context, callSid string, data json.RawMessage) {
	var payload agent.CalendarUpdateData
	if err := json.Unmarshal(data, &payload); err != nil {
		log.Println("Error unmarshaling CALENDAR_UPDATE data:", err)
		EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.", context)
		return
	}

	respBody, err := agent.CalendarUpdate(&payload)
	ctx := "CALENDAR_UPDATE_ERROR"
	if err == nil {
		ctx = "CALENDAR_UPDATE_OK " + string(respBody)
	} else {
		ctx = "CALENDAR_UPDATE_ERROR " + err.Error()
	}

	contextResponse, ctxErr := agent.Context(callSid, ctx)
	if ctxErr != nil {
		log.Println("Error context response:", ctxErr)
		EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.", context)
		return
	}

	var talkData agent.TalkData
	if err = json.Unmarshal(contextResponse.Data, &talkData); err != nil {
		log.Println("Error unmarshaling context response data:", err)
		EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.", context)
		return
	}

	GatherCall(talkData.Message, context)
}

func handleCalendarDelete(context *gin.Context, callSid string, data json.RawMessage) {
	var payload agent.CalendarDeleteData
	if err := json.Unmarshal(data, &payload); err != nil {
		log.Println("Error unmarshaling CALENDAR_DELETE data:", err)
		EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.", context)
		return
	}

	respBody, err := agent.CalendarDelete(&payload)
	ctx := "CALENDAR_DELETE_ERROR"
	if err == nil {
		ctx = "CALENDAR_DELETE_OK " + string(respBody)
	} else {
		ctx = "CALENDAR_DELETE_ERROR " + err.Error()
	}

	contextResponse, ctxErr := agent.Context(callSid, ctx)
	if ctxErr != nil {
		log.Println("Error context response:", ctxErr)
		EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.", context)
		return
	}

	var talkData agent.TalkData
	if err = json.Unmarshal(contextResponse.Data, &talkData); err != nil {
		log.Println("Error unmarshaling context response data:", err)
		EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.", context)
		return
	}

	GatherCall(talkData.Message, context)
}

func handleEndCall(context *gin.Context, callSid string, data json.RawMessage) {
	log.Printf("(%s): Finished call.\n", callSid)
	var talkData agent.TalkData
	if err := json.Unmarshal(data, &talkData); err != nil {
		log.Println("Error unmarshaling END_CALL data:", err)
		EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.", context)
		return
	}
	EndCall(talkData.Message, context)
	agent.EndSession(callSid)
}

func handleCreateAppointment(context *gin.Context, callSid string, fromNumber string, data json.RawMessage) {
	var appointmentData agent.CreateAppointmentData
	if err := json.Unmarshal(data, &appointmentData); err != nil {
		log.Println("Error unmarshaling appointment data:", err)
		EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.", context)
		return
	}

	// 1. Guardar en DB
	err := database.CreateAppointment(&appointmentData, fromNumber)

	// 2. Notificar al Agente sobre el resultado (Context)
	contextResponse, err := agent.Context(callSid, strconv.FormatBool(err == nil))
	if err != nil {
		log.Println("Error context response:", err)
		EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.", context)
		return
	}

	// 3. Responder al usuario con el mensaje que el agente decida
	var talkData agent.TalkData
	if err = json.Unmarshal(contextResponse.Data, &talkData); err != nil {
		log.Println("Error unmarshaling context response data:", err)
		EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.", context)
		return
	}

	GatherCall(talkData.Message, context)
}

// --- Handler Principal ---

func GatherHandler(context *gin.Context) {
	// fromNumber := context.PostForm("From")
	fromNumber := "+1333555666"
	speech := context.PostForm("SpeechResult")
	callSid := context.PostForm("CallSid")

	log.Printf("(%s): %s\n", callSid, speech)

	response, err := agent.Send(callSid, speech)
	if err != nil {
		log.Println("Agent Send Error:", err)
		EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.", context)
		return
	}

	log.Printf("Action: %s", response.Action)

	switch response.Action {
	case "TALK":
		handleTalk(context, response.Data)
	case "END_CALL":
		handleEndCall(context, callSid, response.Data)
	case "CREATE_APPOINTMENT":
		handleCreateAppointment(context, callSid, fromNumber, response.Data)
	case "CALENDAR_LIST":
		handleCalendarList(context, callSid, response.Data)
	case "CALENDAR_CREATE":
		handleCalendarCreate(context, callSid, response.Data)
	case "CALENDAR_UPDATE":
		handleCalendarUpdate(context, callSid, response.Data)
	case "CALENDAR_DELETE":
		handleCalendarDelete(context, callSid, response.Data)
	default:
		log.Printf("Unknown action: %s", response.Action)
		EndCall("Acción no reconocida", context)
	}
}
