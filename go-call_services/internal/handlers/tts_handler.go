package handlers

import (
	"bytes"
	"io"
	"net/http"

	"github.com/gofiber/fiber/v2"
)

type TTSRequest struct {
	Text string `json:"text"`
}

func TextToSpeech(c *fiber.Ctx) error {
	var payload TTSRequest
	if err := c.BodyParser(&payload); err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "invalid JSON"})
	}

	// Construir request a Python
	body := []byte(`{"text":"` + payload.Text + `"}`)

	resp, err := http.Post(
		"http://localhost:8000/ai/tts",
		"application/json",
		bytes.NewBuffer(body),
	)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "cannot connect to TTS service"})
	}
	defer resp.Body.Close()

	audioBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "cannot read audio"})
	}

	// Devolver audio MP3
	c.Set("Content-Type", "audio/mpeg")
	return c.Send(audioBytes)
}
