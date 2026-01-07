package main

import (
	"call-service/internal/handlers"
	"log"

	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Get("/health", func(c *fiber.Ctx) error {
		return c.JSON(fiber.Map{
			"status":  "ok",
			"service": "call-service",
		})
	})

	calls := app.Group("/calls")
	calls.Post("/start", handlers.StartCall)
	calls.Post("/audio", handlers.ReceiveAudio)
	calls.Post("/respond", handlers.RespondToClient)
	calls.Post("/process", handlers.ProcessCall)
	calls.Post("/tts", handlers.TextToSpeech)
	calls.Post("/process-full", handlers.ProcessFullCall)
	app.Post("/twilio/voice", handlers.TwilioVoice)
	app.Post("/twilio/handle-recording", handlers.TwilioHandleRecording)

	log.Println("Call service running on http://localhost:3000")
	log.Fatal(app.Listen(":3000"))
}
