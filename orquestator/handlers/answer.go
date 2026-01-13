package handlers

import (
	"log"
	"net/http"
	"orquestator/actions"
	"orquestator/api/session"

	"github.com/gin-gonic/gin"
)

func AnswerHandler(context *gin.Context) {
	callSid := context.PostForm("CallSid")

	response, err := session.Start(callSid)
	if err != nil {
		log.Println("Answer error:", err)
		return
	}

	if response.Action != "TALK" {
		log.Printf("Session error: Triying to start the conversation with action (%s)\n", response.Action)
		return
	}

	result, err := actions.HandleTalk(callSid, response.Data)
	if err != nil {
		log.Println("Error handling action:", response.Action, err)
		context.String(http.StatusInternalServerError, err.Error())
		return
	}

	context.Header("Content-Type", "text/xml")
	context.String(http.StatusOK, result)
}
