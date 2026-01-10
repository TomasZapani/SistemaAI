package handler

import (
	"encoding/json"
	"log"
	"twilio-ai-agent-go/agent"

	"github.com/gin-gonic/gin"
)

func AnswerHandler(context *gin.Context) {
	callSid := context.PostForm("CallSid")

	response, err := agent.StartSession(callSid)
	if err != nil {
		log.Println("Answer error:", err)
		return
	}

	if response.Action != "TALK" {
		log.Printf("Agent error: Triying to start the conversation with action (%s)\n", response.Action)
		return
	}

	var talkData agent.TalkData

	if err = json.Unmarshal(response.Data, &talkData); err != nil {
		log.Println("Error unmarshaling response:", err)
		return
	}

	GatherCall(talkData.Message, context)
}
