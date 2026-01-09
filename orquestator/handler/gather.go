package handler

import (
	"log"
	"net/http"
	"twilio-ai-agent-go/agent"
	"twilio-ai-agent-go/database"

	"github.com/gin-gonic/gin"
	"github.com/twilio/twilio-go/twiml"
)

func endCall(message string, context *gin.Context) {
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
	} else {
		context.Header("Content-Type", "text/xml")
		context.String(http.StatusOK, twimlResult)
	}
}

func gatherCall(message string, context *gin.Context) {
	twimlResult, err := twiml.Voice([]twiml.Element{
		&twiml.VoiceGather{
			Action:          "https://germproof-jason-noncontrastive.ngrok-free.dev/gather",
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
	} else {
		context.Header("Content-Type", "text/xml")
		context.String(http.StatusOK, twimlResult)
	}
}

func GatherHandler(context *gin.Context) {
	// fromNumber := context.PostForm("From")
	fromNumber := "+1333555666"
	speech := context.PostForm("SpeechResult")
	callSid := context.PostForm("CallSid")

	log.Printf("(%s): %s\n", callSid, speech)

	actionResponse, err := agent.Query(callSid, speech)
	if err != nil {
		log.Println(err)

		endCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.", context)
		return
	}

	log.Println(actionResponse.Action, actionResponse.Message)

	switch actionResponse.Action {
	case "END_CALL":
		endCall(actionResponse.Message, context)
		agent.End(callSid)
		log.Printf("(%s): Finished call.\n", callSid)
		return
	case "CREATE_APPOINTMENT":
		appointmentData := actionResponse.Data

		err := database.CreateAppointment(&appointmentData, fromNumber)
		if err != nil {
			log.Println("Error appointment:", err)
			endCall("No pude agendar tu cita debido a un error interno, por favor intente más tarde.", context)
			return
		}
	}

	gatherCall(actionResponse.Message, context)
}
