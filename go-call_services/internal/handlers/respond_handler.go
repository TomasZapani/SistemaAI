package handlers

import (
	"bytes"
	"encoding/json"
	"log"
	"net/http"

	"github.com/gofiber/fiber/v2"
)

type RespondPayload struct {
	Text string `json:"text"`
}

func RespondToClient(c *fiber.Ctx) error {

	// 1. Parsear JSON recibido
	var payload RespondPayload
	if err := c.BodyParser(&payload); err != nil {
		return c.Status(400).JSON(fiber.Map{
			"error": "invalid JSON",
		})
	}

	log.Println("Recibimos texto del cliente:", payload.Text)

	// 2. Construir body para el microservicio IA
	body, _ := json.Marshal(map[string]interface{}{
		"message": payload.Text,
		"context": nil, // o "" si querés
	})

	// 3. Enviar al microservicio IA (Python)
	resp, err := http.Post("http://localhost:8000/ai/reason", "application/json", bytes.NewBuffer(body))
	if err != nil {
		return c.Status(500).JSON(fiber.Map{
			"error": "cannot connect to AI service",
		})
	}
	defer resp.Body.Close()

	// 4. Decodificar respuesta del microservicio IA
	var aiResponse map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&aiResponse)

	// 5. Devolver la respuesta del agente
	return c.JSON(fiber.Map{
		"reply": aiResponse["reply"],
		"notes": aiResponse["notes"],
	})
}
