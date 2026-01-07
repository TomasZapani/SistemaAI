package handlers

import (
	"github.com/gofiber/fiber/v2"
)

func TwilioVoice(c *fiber.Ctx) error {
	twiml := `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="alice" language="es-ES">
    Hola, soy tu asistente inteligente. Decime en qué puedo ayudarte después del tono.
  </Say>
  <Record
    action="https://6a592ea75829.ngrok-free.app/twilio/handle-recording"
    method="POST"
    maxLength="20"
    playBeep="true"
  />
</Response>`

	c.Set("Content-Type", "application/xml")
	return c.SendString(twiml)
}
