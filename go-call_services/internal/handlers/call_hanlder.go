package handlers

import (
	"log"

	"github.com/gofiber/fiber/v2"
)


func StartCall(c *fiber.Ctx) error {
	type StartPayload struct {
		CallID string `json:"call_id"`
		From   string `json:"from"`
		To     string `json:"to"`
	}

	var body StartPayload
	if err := c.BodyParser(&body); err != nil {
		return c.Status(400).JSON(fiber.Map{
			"error": "invalid JSON",
		})
	}

	log.Println("🔔 Nueva llamada iniciada:")
	log.Println("CallID:", body.CallID)
	log.Println("From:", body.From)
	log.Println("To:", body.To)

	return c.JSON(fiber.Map{
		"status":  "call received",
		"call_id": body.CallID,
	})
}
