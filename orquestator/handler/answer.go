package handler

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/twilio/twilio-go/twiml"
)

func AnswerHandler(context *gin.Context) {
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
					Message:  "Hola, bienvenido al asistente de voz, por favor dime tu consulta.",
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
