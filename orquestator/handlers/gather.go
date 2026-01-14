package handlers

import (
	"log"
	"net/http"
	"orquestator/actions"
	"orquestator/api/session"

	"github.com/gin-gonic/gin"
)

// GatherHandler handles the speech transcription and voice logic
func GatherHandler(context *gin.Context) {
	// Use context.PostForm("From") to get the client number
	//fromNumber := context.PostForm("From")
	speech := context.PostForm("SpeechResult")
	callSid := context.PostForm("CallSid")

	log.Printf("(%s): %s\n", callSid, speech)

	response, err := session.Send(callSid, speech)
	if err != nil {
		log.Println("Agent Send Error:", err)
		// helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}

	log.Printf("Action: %s", response.Action)

	// Get the action handler
	actionHandler := actions.GetActionHandler(response.Action)
	if actionHandler == nil {
		log.Println("Error action not found:", response.Action)
		return
	}

	// Get the action result
	result, err := actionHandler(callSid, response.Data)
	if err != nil {
		log.Println("Error handling action:", response.Action, err)
		context.String(http.StatusInternalServerError, err.Error())
		return
	}

	// Send result to Twilio
	context.Header("Content-Type", "text/xml")
	context.String(http.StatusOK, result)
}
