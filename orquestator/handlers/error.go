package handlers

import (
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
)

func ErrorHandler(c *gin.Context) {
	// Obtener todos los parámetros del formulario
	formData := c.Request.PostForm
	if len(formData) == 0 {
		// Parsear primero el formulario si no está
		c.Request.ParseForm()
		formData = c.Request.PostForm
	}

	// Imprimir todos los campos para debug
	for key, values := range formData {
		fmt.Printf("%s: %v\n", key, values)
	}

	// Campos comunes de Twilio
	errorCode := c.PostForm("ErrorCode")
	errorMessage := c.PostForm("ErrorMessage")
	callSid := c.PostForm("CallSid")

	fmt.Printf("Twilio Error received: Code=%s, Message=%s, CallSid=%s\n", errorCode, errorMessage, callSid)

	// Responder a Twilio con 200 OK para que no siga enviando retries
	c.Status(http.StatusOK)
}
