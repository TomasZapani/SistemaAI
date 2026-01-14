package handlers

import (
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
)

// Handle Twilio errors
func ErrorHandler(c *gin.Context) {
	formData := c.Request.PostForm
	if len(formData) == 0 {
		c.Request.ParseForm()
		formData = c.Request.PostForm
	}

	for key, values := range formData {
		fmt.Printf("%s: %v\n", key, values)
	}

	errorCode := c.PostForm("ErrorCode")
	errorMessage := c.PostForm("ErrorMessage")
	callSid := c.PostForm("CallSid")

	fmt.Printf("Twilio Error received: Code=%s, Message=%s, CallSid=%s\n", errorCode, errorMessage, callSid)

	c.Status(http.StatusOK)
}
