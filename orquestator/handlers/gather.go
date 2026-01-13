package handlers

import (
	"log"
	"net/http"
	"orquestator/actions"
	"orquestator/api/session"

	"github.com/gin-gonic/gin"
)

func GatherHandler(context *gin.Context) {
	// fromNumber := context.PostForm("From")
	//fromNumber := "+1333555666"
	speech := context.PostForm("SpeechResult")
	callSid := context.PostForm("CallSid")

	log.Printf("(%s): %s\n", callSid, speech)

	response, err := session.Send(callSid, speech)
	if err != nil {
		log.Println("Agent Send Error:", err)
		// helper.EndCall("Lo siento, tuvimos un error interno, por favor intentalo más tarde.")
	}

	log.Printf("Action: %s", response.Action)

	actionHandler := actions.GetAction(response.Action)
	if actionHandler == nil {
		log.Println("Error action not found:", response.Action)
		return
	}

	result, err := actionHandler(callSid, response.Data)
	if err != nil {
		log.Println("Error handling action:", response.Action, err)
		context.String(http.StatusInternalServerError, err.Error())
		return
	}

	context.Header("Content-Type", "text/xml")
	context.String(http.StatusOK, result)
}
